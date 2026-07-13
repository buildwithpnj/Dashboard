from typing import Dict, Any, List

class McpToolRegistry:
    @classmethod
    def get_registered_tools(cls) -> List[Dict[str, Any]]:
        """
        Returns schemas for exposed Model Context Protocol (MCP) tools.
        """
        return [
            {
                "name": "search_knowledge",
                "description": "Searches matching knowledge chunks inside the workspace RAG layer",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search keyword"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_task",
                "description": "Creates a persistent workspace goal/task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Short title of the task"},
                        "description": {"type": "string", "description": "Detailed notes"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "get_recent_updates",
                "description": "Lists recently updated files or goals",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    @classmethod
    def is_tool_registered(cls, name: str) -> bool:
        """
        Validates if a tool name is registered in the MCP boundary.
        """
        tools = cls.get_registered_tools()
        return any(t["name"] == name for t in tools)
