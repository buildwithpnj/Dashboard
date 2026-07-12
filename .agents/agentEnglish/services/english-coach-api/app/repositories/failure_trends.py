from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import FailureTrend
from app.repositories.base import BaseDBRepository

class FailureTrendsRepository(BaseDBRepository[FailureTrend]):
    """DB-backed repository managing failure trend counts over rolling time windows."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, FailureTrend)

    async def create(self, trend: FailureTrend) -> FailureTrend:
        """Saves a new FailureTrend record."""
        self.db.add(trend)
        await self.db.flush()
        return trend

    async def get_trends(self, tenant_id: str, product_id: str, window_size: str) -> List[FailureTrend]:
        """Retrieves failure trends matching the tenant, product, and window size, ordered by creation date desc."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id,
            self.model_cls.window_size == window_size
        ).order_by(desc(self.model_cls.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_trend_history(self, tenant_id: str, product_id: str, error_bucket: str) -> List[FailureTrend]:
        """Retrieves failure trends matching the tenant, product, and error bucket, ordered by creation date desc."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id,
            self.model_cls.error_bucket == error_bucket
        ).order_by(desc(self.model_cls.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
