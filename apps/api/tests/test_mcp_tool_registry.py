import pytest
from app.services.mcp_tool_registry import McpToolRegistry

def test_mcp_tool_registry_checks():
    tools = McpToolRegistry.get_registered_tools()
    assert len(tools) >= 3
    
    assert McpToolRegistry.is_tool_registered("search_knowledge") is True
    assert McpToolRegistry.is_tool_registered("create_task") is True
    assert McpToolRegistry.is_tool_registered("unsupported_tool_xyz") is False
