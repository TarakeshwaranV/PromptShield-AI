"""
Layer 3: Independent Runtime Authorization Guard
Enforces strict allowlisting, parameter validation,
and zero arbitrary execution guarantees.
The LLM has zero capability to authorize its own operations.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from config import ALLOWED_TOOLS
from core import mock_sales
from core.logging_utils import record_security_audit

@dataclass
class ToolExecutionResult:
    authorized: bool
    tool_name: str
    cleaned_args: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    violation_type: Optional[str] = None

class ToolAuthorizationGuard:
    def __init__(self):
        self.allowed_tools = ALLOWED_TOOLS

    def _sanitize_and_validate_arguments(self, tool_name: str, raw_args: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Rigidly validate argument names, types, and values.
        Rejects suspicious characters, arbitrary SQL snippets, and oversized payloads.
        """
        tool_spec = self.allowed_tools[tool_name]
        cleaned = {}
        
        # Check for unapproved extra arguments
        all_allowed_args = set(tool_spec["required_args"] + tool_spec["optional_args"])
        for k in raw_args.keys():
            if k not in all_allowed_args:
                return False, {}, f"Disallowed parameter '{k}' detected for tool '{tool_name}'."
                
        # Check required arguments
        for req in tool_spec["required_args"]:
            if req not in raw_args or raw_args[req] is None:
                return False, {}, f"Missing required parameter '{req}' for tool '{tool_name}'."
                
        # Specific parameter validations
        for k, v in raw_args.items():
            str_val = str(v)
            # Check for SQL/Command injection markers in parameters
            dangerous_tokens = [";", "--", "/*", "*/", "drop", "delete", "insert", "update", "exec", "system", "union", "<script>"]
            if any(dt in str_val.lower() for dt in dangerous_tokens):
                return False, {}, f"Security Exception: Suspicious token pattern identified in argument '{k}'."

            if k == "year":
                try:
                    val_int = int(v)
                    if val_int < 2000 or val_int > 2100:
                        return False, {}, f"Argument 'year' must be between 2000 and 2100 (received {val_int})."
                    cleaned["year"] = val_int
                except (ValueError, TypeError):
                    return False, {}, f"Invalid type for 'year': expected integer, got '{v}'."
                    
            elif k == "quarter":
                try:
                    val_int = int(v)
                    if val_int not in [1, 2, 3, 4]:
                        return False, {}, f"Argument 'quarter' must be 1, 2, 3, or 4 (received {val_int})."
                    cleaned["quarter"] = val_int
                except (ValueError, TypeError):
                    return False, {}, f"Invalid type for 'quarter': expected integer 1-4."
                    
            elif k == "limit":
                try:
                    val_int = int(v)
                    if val_int < 1 or val_int > 50:
                        return False, {}, f"Argument 'limit' out of bounded range 1-50."
                    cleaned["limit"] = val_int
                except (ValueError, TypeError):
                    return False, {}, f"Invalid type for 'limit': expected integer."
                    
            elif k == "region":
                valid_regions = ["North America", "EMEA", "APAC", "LATAM", "all"]
                if not isinstance(v, str) or len(v) > 30:
                    return False, {}, f"Invalid 'region' string length or format."
                cleaned["region"] = v.strip()
            else:
                cleaned[k] = v
                
        return True, cleaned, None

    def execute(self, tool_name: str, raw_args: Optional[Dict[str, Any]] = None, test_id: Optional[str] = None) -> ToolExecutionResult:
        """
        Primary execution entry point.
        Checks allowlist -> Validates arguments -> Executes mock tool.
        """
        args = raw_args or {}
        
        # 1. Allowlist enforcement
        if tool_name not in self.allowed_tools:
            record_security_audit(
                chatbot_config="shielded_pipeline",
                event_type="tool_execution_attempt",
                test_id=test_id,
                layer_responsible="Layer 3 (Guard)",
                tool_name=tool_name,
                authorization_outcome="REJECTED_UNAUTHORIZED_TOOL",
                details=f"Tool '{tool_name}' is not in the system allowlist."
            )
            return ToolExecutionResult(
                authorized=False,
                tool_name=tool_name,
                violation_type="UNAUTHORIZED_TOOL",
                error_message=f"Access Denied: Tool '{tool_name}' is not registered in the security allowlist."
            )
            
        # 2. Argument Type and Security Validation
        valid, cleaned_args, validation_err = self._sanitize_and_validate_arguments(tool_name, args)
        if not valid:
            record_security_audit(
                chatbot_config="shielded_pipeline",
                event_type="tool_execution_attempt",
                test_id=test_id,
                layer_responsible="Layer 3 (Guard)",
                tool_name=tool_name,
                authorization_outcome="REJECTED_ARGUMENT_VIOLATION",
                details=validation_err
            )
            return ToolExecutionResult(
                authorized=False,
                tool_name=tool_name,
                cleaned_args=args,
                violation_type="ARGUMENT_VIOLATION",
                error_message=validation_err
            )
            
        # 3. Independent, Safe Dispatching to Read-Only Mock Database
        try:
            if tool_name == "get_sales_summary":
                res = mock_sales.get_sales_summary(year=cleaned_args.get("year"))
            elif tool_name == "get_sales_by_month":
                res = mock_sales.get_sales_by_month(year=cleaned_args["year"], quarter=cleaned_args.get("quarter"))
            elif tool_name == "get_top_products":
                res = mock_sales.get_top_products(limit=cleaned_args.get("limit", 5))
            elif tool_name == "get_sales_by_region":
                res = mock_sales.get_sales_by_region(region=cleaned_args["region"], year=cleaned_args.get("year"))
            else:
                raise ValueError("Unmapped allowed tool")
                
            record_security_audit(
                chatbot_config="shielded_pipeline",
                event_type="tool_execution_success",
                test_id=test_id,
                layer_responsible="Layer 3 (Guard)",
                tool_name=tool_name,
                authorization_outcome="AUTHORIZED",
                details=f"Successfully executed tool '{tool_name}'."
            )
            return ToolExecutionResult(
                authorized=True,
                tool_name=tool_name,
                cleaned_args=cleaned_args,
                data=res
            )
        except Exception as e:
            record_security_audit(
                chatbot_config="shielded_pipeline",
                event_type="tool_execution_failure",
                test_id=test_id,
                layer_responsible="Layer 3 (Guard)",
                tool_name=tool_name,
                authorization_outcome="EXECUTION_ERROR",
                details=str(e)
            )
            return ToolExecutionResult(
                authorized=True,
                tool_name=tool_name,
                cleaned_args=cleaned_args,
                error_message=f"Internal database execution exception: {str(e)}"
            )

# Singleton runtime guard instance
runtime_guard = ToolAuthorizationGuard()
