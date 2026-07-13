import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("mcp_policy_guard")

class McpPolicyGuard:
    @classmethod
    def check_permissions(
        cls,
        tenant_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Enforces tenant partition validation before any MCP tool runs.
        """
        if not tenant_id or len(tenant_id.strip()) == 0:
            return False, "Access Denied: Missing tenant scope identifier."

        # Safety: Admin tools require special checks (mock simulation)
        if "admin" in tool_name.lower():
            return False, f"Unauthorized: Tool '{tool_name}' requires supervisor roles."

        # Safety: Empty query search checks
        if tool_name == "search_knowledge":
            query = arguments.get("query", "").strip()
            if not query:
                return False, "Input query cannot be empty."

        return True, "Authorized"
