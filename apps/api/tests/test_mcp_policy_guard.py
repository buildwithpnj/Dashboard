import pytest
from app.services.mcp_policy_guard import McpPolicyGuard

def test_mcp_policy_guard_authorization():
    # Success check
    is_ok, msg = McpPolicyGuard.check_permissions("tenant_123", "search_knowledge", {"query": "habit trackers"})
    assert is_ok is True
    assert msg == "Authorized"
    
    # Missing tenant id check
    is_ok, msg = McpPolicyGuard.check_permissions("", "search_knowledge", {"query": "habit trackers"})
    assert is_ok is False
    assert "Missing tenant scope" in msg
    
    # Block admin tools check
    is_ok, msg = McpPolicyGuard.check_permissions("tenant_123", "delete_admin_users", {})
    assert is_ok is False
    assert "Unauthorized" in msg

    # Empty query search block
    is_ok, msg = McpPolicyGuard.check_permissions("tenant_123", "search_knowledge", {"query": "   "})
    assert is_ok is False
    assert "cannot be empty" in msg
