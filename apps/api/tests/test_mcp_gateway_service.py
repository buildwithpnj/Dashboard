import pytest
from unittest.mock import AsyncMock, patch
from app.services.mcp_gateway_service import McpGatewayService
from app.services.mcp_trace_service import McpTraceService

@pytest.mark.asyncio
async def test_execute_mcp_unregistered_tool():
    db = AsyncMock()
    success, msg, data = await McpGatewayService.execute_mcp_tool(
        db, "tenant_1", "unregistered_tool_name", {}
    )
    assert success is False
    assert "not registered" in msg
    assert data == {}

@pytest.mark.asyncio
async def test_execute_mcp_policy_blocked():
    db = AsyncMock()
    McpTraceService.clear_traces()
    
    # Missing tenant id to trigger policy guard block
    success, msg, data = await McpGatewayService.execute_mcp_tool(
        db, "", "search_knowledge", {"query": "something"}
    )
    assert success is False
    assert "Policy Block" in msg
    assert len(McpTraceService.get_traces()) == 1

@pytest.mark.asyncio
async def test_execute_mcp_tool_success_search():
    db = AsyncMock()
    McpTraceService.clear_traces()
    
    # Mock search retrieval results
    with patch("app.services.hybrid_retrieval_service.HybridRetrievalService.retrieve", new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = [
            {"chunk_id": "c_1", "chunk_summary": "Sync habits details"}
        ]
        
        success, msg, data = await McpGatewayService.execute_mcp_tool(
            db, "tenant_1", "search_knowledge", {"query": "sync habits"}
        )
        
        assert success is True
        assert "Retrieved 1" in msg
        assert len(data["matches"]) == 1
        assert len(McpTraceService.get_traces()) == 1
