import pytest
from core.tool_guard import ToolAuthorizationGuard, ToolExecutionResult

@pytest.fixture
def guard():
    return ToolAuthorizationGuard()

def test_tool_allowlist_enforcement(guard):
    # Allowed tools should pass allowlist check
    for tool_name in ["get_sales_summary", "get_sales_by_month", "get_top_products", "get_sales_by_region"]:
        assert tool_name in guard.allowed_tools

    # Unapproved tools must be strictly rejected
    unauthorized_tools = [
        "delete_sales_records",
        "os_system_shell",
        "execute_raw_sql",
        "drop_database_tables",
        "export_all_customer_pii"
    ]
    for unauth in unauthorized_tools:
        res = guard.execute(unauth, raw_args={})
        assert res.authorized is False
        assert res.violation_type == "UNAUTHORIZED_TOOL"
        assert "not registered in the security allowlist" in res.error_message

def test_argument_validation_and_injection_blocking(guard):
    # SQL injection attempt in parameters
    malicious_args = {"year": "2024; DROP TABLE sales_records; --"}
    res_sql = guard.execute("get_sales_by_month", raw_args=malicious_args)
    assert res_sql.authorized is False
    assert res_sql.violation_type == "ARGUMENT_VIOLATION"
    assert "Suspicious token" in res_sql.error_message

    # Invalid range bounds
    out_of_bounds = {"year": 1850}
    res_year = guard.execute("get_sales_by_month", raw_args=out_of_bounds)
    assert res_year.authorized is False
    assert "must be between 2000 and 2100" in res_year.error_message

    # Disallowed argument name
    disallowed_arg = {"year": 2024, "dangerous_extra_param": "drop"}
    res_extra = guard.execute("get_sales_by_month", raw_args=disallowed_arg)
    assert res_extra.authorized is False
    assert "Disallowed parameter" in res_extra.error_message

def test_valid_tool_execution(guard):
    # get_sales_summary
    res_summary = guard.execute("get_sales_summary", raw_args={"year": 2024})
    assert res_summary.authorized is True
    assert res_summary.data is not None
    assert "total_revenue_usd" in res_summary.data

    # get_top_products
    res_top = guard.execute("get_top_products", raw_args={"limit": 3})
    assert res_top.authorized is True
    assert len(res_top.data["top_products"]) <= 3

    # get_sales_by_region
    res_region = guard.execute("get_sales_by_region", raw_args={"region": "North America"})
    assert res_region.authorized is True
    assert res_region.data["status"] == "success"
