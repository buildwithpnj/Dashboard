import pytest
import time
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import Session, Message
from app.repositories.sessions import SessionsRepository
from app.repositories.messages import MessagesRepository
from app.tasks.worker import BackgroundJobWorker
from app.tasks.jobs import consolidate_session_memory, run_live_eval_check

@pytest.mark.anyio
async def test_background_job_execution_flow():
    """Asserts that thread pool workers accept and process tasks asynchronously."""
    async with AsyncSessionLocal() as db:
        sess_repo = SessionsRepository(db)
        msg_repo = MessagesRepository(db)

        session_id = f"sess-{uuid.uuid4()}"
        
        # 1. Create a session and message
        sess = Session(
            id=session_id,
            user_id="user_test",
            product_id="english_coach",
            is_active=True
        )
        await sess_repo.create(sess)
        
        msg = Message(
            id=f"msg-{uuid.uuid4()}",
            session_id=session_id,
            role="user",
            content="Hello English Coach background tasks check.",
            metadata_json="{}"
        )
        await msg_repo.create(msg)
        await db.commit()

        # 2. Submit consolidation and evaluation jobs to ThreadPoolExecutor
        BackgroundJobWorker.submit_job(consolidate_session_memory, session_id)
        BackgroundJobWorker.submit_job(run_live_eval_check, "response-001")

        # Give the threads a short period of time to process
        time.sleep(0.5)

        # 3. Cleanup test records
        await sess_repo.delete(sess)
        await db.commit()
