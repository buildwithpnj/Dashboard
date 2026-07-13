import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.action_result_verifier import ActionResultVerifier
from app.models.goals import Goal

@pytest.mark.asyncio
async def test_verify_task_created_found():
    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = Goal(id="task_1", title="Verified Task")
    db.execute.return_value = mock_res
    
    verified = await ActionResultVerifier.verify_task_created(db, "task_1")
    assert verified is True

@pytest.mark.asyncio
async def test_verify_task_created_missing():
    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_res
    
    verified = await ActionResultVerifier.verify_task_created(db, "task_2")
    assert verified is False
