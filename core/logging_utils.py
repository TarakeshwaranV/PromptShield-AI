import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from core.database import log_security_event

# Configure standard Python logger
logger = logging.getLogger("PromptShieldAI")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [PromptShield] %(message)s", "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def record_security_audit(
    chatbot_config: str,
    event_type: str,
    test_id: Optional[str] = None,
    detector_decision: Optional[str] = None,
    risk_score: Optional[float] = None,
    layer_responsible: Optional[str] = None,
    tool_name: Optional[str] = None,
    authorization_outcome: Optional[str] = None,
    execution_latency_ms: Optional[float] = None,
    details: Optional[str] = None
) -> int:
    """
    Log security events both to console and persistent SQLite database.
    Ensures safe redaction of any sensitive information.
    """
    logger.info(
        f"CONFIG={chatbot_config} | EVENT={event_type} | LAYER={layer_responsible} | "
        f"DECISION={detector_decision} | RISK={risk_score} | TOOL={tool_name} | "
        f"AUTH={authorization_outcome} | LATENCY={execution_latency_ms:.2f}ms"
        if execution_latency_ms else
        f"CONFIG={chatbot_config} | EVENT={event_type} | LAYER={layer_responsible} | "
        f"DECISION={detector_decision} | RISK={risk_score} | TOOL={tool_name} | AUTH={authorization_outcome}"
    )
    
    return log_security_event(
        chatbot_config=chatbot_config,
        event_type=event_type,
        test_id=test_id,
        detector_decision=detector_decision,
        risk_score=risk_score,
        layer_responsible=layer_responsible,
        tool_name=tool_name,
        authorization_outcome=authorization_outcome,
        execution_latency_ms=execution_latency_ms,
        details=details
    )
