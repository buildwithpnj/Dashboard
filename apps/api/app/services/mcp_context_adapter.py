from typing import Dict, Any

class McpContextAdapter:
    @classmethod
    def format_environment_context(
        cls,
        user_id: str,
        current_route: str
    ) -> Dict[str, Any]:
        """
        Formats active session parameters for the MCP tools.
        """
        return {
            "mcp_scope": "warborn_os_active",
            "active_user": user_id,
            "viewport_route": current_route,
            "session_context_type": "standard_oauth_bearer"
        }
