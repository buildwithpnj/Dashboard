import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.task_action_service import TaskActionService
from app.models.goals import Goal

@pytest.mark.asyncio
async def test_create_task_success():
    db = AsyncMock()
    
    # We want TaskActionService.create_task to run
    task = await TaskActionService.create_task(
        db=db,
        user_id="user_555",
        title="Implement looping tests",
        description="Verify V47 persistence",
        category="Engineering"
    )
    
    assert task.user_id == "user_555"
    assert task.title == "Implement looping tests"
    assert task.status == "pending"
    assert db.add.called
    assert db.commit.called

@pytest.mark.asyncio
async def test_update_task_status():
    db = AsyncMock()
    existing_task = Goal(
        user_id="user_555",
        title="Check status logic",
        status="pending"
    )
    
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = existing_task
    db.execute.return_value = mock_res
    
    updated = await TaskActionService.update_task_status(db, "task_abc", "completed", 100)
    assert updated.status == "completed"
    assert updated.progress == 100
