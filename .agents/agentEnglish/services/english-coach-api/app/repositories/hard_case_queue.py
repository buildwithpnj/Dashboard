from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import HardCase
from app.repositories.base import BaseDBRepository

class HardCaseQueueRepository(BaseDBRepository[HardCase]):
    """DB-backed repository managing sampled complex edge cases queued for reviewer labeling."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, HardCase)

    async def create(self, hard_case: HardCase) -> HardCase:
        self.db.add(hard_case)
        await self.db.flush()
        return hard_case

    async def get_pending(self, tenant_id: str, limit: int = 100) -> List[HardCase]:
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.status == "PENDING"
        ).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_status(self, case_id: str, status: str) -> None:
        stmt = select(self.model_cls).filter(self.model_cls.id == case_id)
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        if record:
            record.status = status
            await self.db.flush()
