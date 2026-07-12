import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ReviewerProductivity
from app.repositories.base import BaseDBRepository

class ReviewerProductivityRepository(BaseDBRepository[ReviewerProductivity]):
    """DB-backed repository managing reviewer throughput stats and alignment drift metrics."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ReviewerProductivity)

    async def create(self, prod: ReviewerProductivity) -> ReviewerProductivity:
        """Saves a new ReviewerProductivity record to the session."""
        self.db.add(prod)
        await self.db.flush()
        return prod

    async def get_by_reviewer(self, reviewer_id: str, tenant_id: str) -> Optional[ReviewerProductivity]:
        """Loads productivity record for a specific reviewer under a tenant partition."""
        stmt = select(self.model_cls).filter(
            self.model_cls.reviewer_id == reviewer_id,
            self.model_cls.tenant_id == tenant_id
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def update_productivity(
        self, reviewer_id: str, tenant_id: str, duration_ms: float, is_aligned: bool
    ) -> ReviewerProductivity:
        """Finds or creates a reviewer productivity record and updates rolling duration and drift score."""
        prod = await self.get_by_reviewer(reviewer_id, tenant_id)
        if not prod:
            prod = ReviewerProductivity(
                id=str(uuid.uuid4()),
                reviewer_id=reviewer_id,
                tenant_id=tenant_id,
                resolutions_count=0,
                avg_duration_ms=0.0,
                drift_score=0.5
            )

            self.db.add(prod)
            await self.db.flush()

        prod.resolutions_count += 1
        count = prod.resolutions_count

        # Rolling average calculation
        prod.avg_duration_ms = (prod.avg_duration_ms * (count - 1) + duration_ms) / count

        # Drift score calculation
        if is_aligned:
            prod.drift_score -= 0.05
        else:
            prod.drift_score += 0.10

        # Clip drift score between 0.0 and 1.0
        prod.drift_score = max(0.0, min(1.0, prod.drift_score))

        await self.db.flush()
        return prod
