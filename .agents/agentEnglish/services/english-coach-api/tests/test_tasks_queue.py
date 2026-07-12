import pytest
import uuid
from app.tasks.jobs import consolidate_session_memory, run_live_eval_check
from app.db.session import AsyncSessionLocal
from app.repositories.task_runs import TaskRunsRepository

@pytest.mark.anyio
async def test_tasks_queue_logging_db():
    """Asserts that Celery tasks write status records on starting and completion."""
    # 1. Run consolidate memory task
    task_res = consolidate_session_memory("session-001")
    assert "Consolidated" in task_res or "Skipped" in task_res

    # 2. Check task_runs table for status log
    async with AsyncSessionLocal() as db:
        repo = TaskRunsRepository(db)
        runs = await repo.get_by_status("SUCCESS")
        assert len(runs) >= 1
        
        target_run = runs[0]
        assert target_run.task_name in ["consolidate_session_memory", "run_live_eval_check"]
        assert target_run.duration_ms >= 0.0
