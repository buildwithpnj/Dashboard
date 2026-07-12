from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import RegressionEvent
from app.repositories.base import BaseDBRepository

class RegressionEventsRepository(BaseDBRepository[RegressionEvent]):
    """DB-backed repository managing performance regression events."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, RegressionEvent)

    async def create(self, event: RegressionEvent) -> RegressionEvent:
        """Saves a new RegressionEvent."""
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_active_events(self, tenant_id: str, product_id: str) -> List[RegressionEvent]:
        """Retrieves active (unresolved) regression events for a tenant and product."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id,
            self.model_cls.status == "ACTIVE"
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def resolve_event(self, event_id: str) -> None:
        """Marks a target regression event status as RESOLVED."""
        stmt = select(self.model_cls).filter(self.model_cls.id == event_id)
        res = await self.db.execute(stmt)
        event = res.scalars().first()
        if event:
            event.status = "RESOLVED"
            await self.db.flush()
