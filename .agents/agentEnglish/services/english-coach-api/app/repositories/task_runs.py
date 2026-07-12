import datetime
from typing import List, Optional
from sqlalchemy import select, update
from app.repositories.base import BaseDBRepository
from app.db.models import TaskRun

class TaskRunsRepository(BaseDBRepository[TaskRun]):
    """DB-backed repository tracking execution states, durations, and retry counts of Celery async tasks."""

    def __init__(self, db):
        super().__init__(db, TaskRun)

    async def get_by_status(self, status: str) -> List[TaskRun]:
        """Loads task execution runs filtered by status (e.g. PENDING, SUCCESS, FAILURE)."""
        stmt = select(self.model_cls).filter(self.model_cls.status == status).order_by(self.model_cls.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_task_state(
        self,
        task_id: str,
        status: str,
        duration_ms: float = 0.0,
        retries: int = 0,
        failure_reason: Optional[str] = None
    ) -> Optional[TaskRun]:
        """Updates runtime details, statuses, and completion times of task runs."""
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.id == task_id)
            .values(
                status=status,
                duration_ms=duration_ms,
                retries=retries,
                failure_reason=failure_reason,
                completed_at=datetime.datetime.utcnow() if status in ["SUCCESS", "FAILURE"] else None
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()
        return await self.get_by_id(task_id)
