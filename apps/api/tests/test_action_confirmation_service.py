import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.action_confirmation_service import ActionConfirmationService
from app.models.goals import Goal

@pytest.mark.asyncio
async def test_process_task_creation_contract_violation():
    db = AsyncMock()
    # Title is missing
    payload = {"description": "No title here"}
    
    success, msg, task_id = await ActionConfirmationService.process_task_creation_with_verification(
        db, "user_123", payload
    )
    assert success is False
    assert "Action schema violation" in msg
    assert task_id is None

@pytest.mark.asyncio
async def test_process_task_creation_persistence_blocked():
    db = AsyncMock()
    # Title is a placeholder
    payload = {"title": "test", "description": "Placeholder test"}
    
    success, msg, task_id = await ActionConfirmationService.process_task_creation_with_verification(
        db, "user_123", payload
    )
    assert success is False
    assert "Action blocked" in msg
    assert task_id is None

@pytest.mark.asyncio
async def test_process_task_creation_success():
    db = AsyncMock()
    payload = {"title": "Production Release V47", "description": "Ensure action verifications work"}
    
    mock_task = Goal(id="task_verify_99", title="Production Release V47")
    
    with patch("app.services.task_action_service.TaskActionService.create_task", new_callable=AsyncMock) as mock_create, \
         patch("app.services.action_result_verifier.ActionResultVerifier.verify_task_created", new_callable=AsyncMock) as mock_verify:
        
        mock_create.return_value = mock_task
        mock_verify.return_value = True
        
        success, msg, task_id = await ActionConfirmationService.process_task_creation_with_verification(
            db, "user_123", payload
        )
        
        assert success is True
        assert "Successfully created task" in msg
        assert task_id == "task_verify_99"
