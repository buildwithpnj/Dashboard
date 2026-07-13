import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goals import Goal

logger = logging.getLogger("action_result_verifier")

class ActionResultVerifier:
    @classmethod
    async def verify_task_created(
        cls,
        db: AsyncSession,
        task_id: str
    ) -> bool:
        """
        Actively queries database session to verify task creation matches persistent table records.
        """
        db.expire_all()  # Clear local session caches
        stmt = select(Goal).where(Goal.id == task_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        is_verified = record is not None
        if is_verified:
            logger.info(f"Factual Verification Success: Task {task_id} exists in persistent storage.")
        else:
            logger.error(f"Factual Verification Failure: Task {task_id} missing from database tables.")
        return is_verified

    @classmethod
    async def verify_task_status(
        cls,
        db: AsyncSession,
        task_id: str,
        expected_status: str
    ) -> bool:
        """
        Verifies task status matches expectations in DB.
        """
        db.expire_all()
        stmt = select(Goal).where(Goal.id == task_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return False
            
        is_matching = record.status == expected_status
        if is_matching:
            logger.info(f"Factual Verification Success: Task {task_id} status matches '{expected_status}'.")
        else:
            logger.error(f"Factual Verification Failure: Task {task_id} status is '{record.status}', expected '{expected_status}'.")
        return is_matching
