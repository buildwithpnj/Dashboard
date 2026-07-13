from typing import Dict, Any, List

class McpTraceService:
    # Memory-based static dict tracking MCP execution traces
    _traces: List[Dict[str, Any]] = []

    @classmethod
    def log_invocation(
        cls,
        tool_name: str,
        arguments: Dict[str, Any],
        latency_ms: float,
        success: bool,
        message: str
    ) -> None:
        """
        Stores details of an MCP tool run.
        """
        cls._traces.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "latency_ms": latency_ms,
            "success": success,
            "message": message
        })

    @classmethod
    def get_traces(cls) -> List[Dict[str, Any]]:
        """
        Retrieves all MCP traces.
        """
        return cls._traces

    @classmethod
    def clear_traces(cls) -> None:
        """
        Evicts history.
        """
        cls._traces.clear()
