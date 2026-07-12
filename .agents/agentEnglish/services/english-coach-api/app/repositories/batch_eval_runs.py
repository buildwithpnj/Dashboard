import uuid
import datetime
import json
import logging
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import BatchEvalRun

logger = logging.getLogger(__name__)


class BatchEvalRunsRepository:
    """Manages persistence of large-scale evaluation run execution records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run: BatchEvalRun) -> None:
        """Inserts a new batch eval run record."""
        self.db.add(run)
        await self.db.flush()

    async def get_by_id(self, run_id: str) -> Optional[BatchEvalRun]:
        """Retrieves a batch eval run by its primary key."""
        stmt = select(BatchEvalRun).where(BatchEvalRun.id == run_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        run_id: str,
        processed_count: int,
        passed_count: int,
        failed_count: int,
        total_tokens: int,
        cost_usd: float,
        checkpoint_json: Optional[str] = None
    ) -> None:
        """Updates run progress counters and cost tracking fields."""
        stmt = (
            update(BatchEvalRun)
            .where(BatchEvalRun.id == run_id)
            .values(
                processed_count=processed_count,
                passed_count=passed_count,
                failed_count=failed_count,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                checkpoint_json=checkpoint_json
            )
        )
        await self.db.execute(stmt)

    async def complete_run(self, run_id: str, status: str = "COMPLETED") -> None:
        """Marks a run as completed or budget-stopped with a completion timestamp."""
        stmt = (
            update(BatchEvalRun)
            .where(BatchEvalRun.id == run_id)
            .values(
                status=status,
                completed_at=datetime.datetime.utcnow()
            )
        )
        await self.db.execute(stmt)

    async def list_runs(self, tenant_id: str = "default_tenant", limit: int = 20) -> List[BatchEvalRun]:
        """Lists recent eval runs for a tenant, ordered by creation date descending."""
        stmt = (
            select(BatchEvalRun)
            .where(BatchEvalRun.tenant_id == tenant_id)
            .order_by(BatchEvalRun.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
