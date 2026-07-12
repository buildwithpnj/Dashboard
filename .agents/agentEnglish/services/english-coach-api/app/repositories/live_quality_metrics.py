from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import LiveQualityMetric
from app.repositories.base import BaseDBRepository

class LiveQualityMetricsRepository(BaseDBRepository[LiveQualityMetric]):
    """DB-backed repository managing live rolling quality aggregates."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, LiveQualityMetric)

    async def create(self, metric: LiveQualityMetric) -> LiveQualityMetric:
        """Saves a new LiveQualityMetric to the database."""
        self.db.add(metric)
        await self.db.flush()
        return metric

    async def get_latest(self, tenant_id: str, product_id: str, window_size: str) -> Optional[LiveQualityMetric]:
        """Retrieves the latest rolling quality metric for a given tenant, product, and window size."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id,
            self.model_cls.window_size == window_size
        ).order_by(desc(self.model_cls.created_at))
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_history(self, tenant_id: str, product_id: str, limit: int = 50) -> List[LiveQualityMetric]:
        """Lists historical quality metrics for a given tenant and product, ordered by creation date desc."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id
        ).order_by(desc(self.model_cls.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
