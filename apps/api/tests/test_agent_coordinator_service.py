import pytest
from unittest.mock import AsyncMock, patch
from app.services.agent_coordinator_service import AgentCoordinatorService

@pytest.mark.asyncio
async def test_coordinate_multi_agent_flow_task():
    db = AsyncMock()
    
    payload = {"title": "Task Action Release", "description": "V48 coordinator test"}
    
    # We patch confirmation service to mock successful write verification
    with patch("app.services.action_confirmation_service.ActionConfirmationService.process_task_creation_with_verification", new_callable=AsyncMock) as mock_confirm:
        mock_confirm.return_value = (True, "Verified task creation success", "task_123")
        
        result = await AgentCoordinatorService.coordinate_multi_agent_run(
            db=db,
            user_id="user_abc",
            query="add task for release goals",
            payload=payload
        )
        
        assert result["status"] == "success"
        assert len(result["plan"]) == 2
        assert result["plan"][0]["agent"] == "retrieval"
        assert result["plan"][1]["agent"] == "action"
        assert result["final_state"]["action_success"] is True
        assert len(result["trace_history"]) == 2
