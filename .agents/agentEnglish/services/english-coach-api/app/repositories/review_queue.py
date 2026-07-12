import datetime
from typing import Optional, List
from sqlalchemy import select, update
from app.repositories.base import BaseDBRepository
from app.db.models import ReviewQueue

class ReviewQueueRepository(BaseDBRepository[ReviewQueue]):
    """DB-backed repository managing human evaluation workflow items."""

    def __init__(self, db):
        super().__init__(db, ReviewQueue)

    async def get_pending_by_tenant(self, tenant_id: str) -> List[ReviewQueue]:
        """Loads pending human-in-the-loop review items for a tenant partition."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.status == "PENDING"
        ).order_by(self.model_cls.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def resolve_review_item(
        self,
        item_id: str,
        status: str,
        edited_response: Optional[str] = None,
        reviewer_notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[ReviewQueue]:
        """Marks a queue item resolved, logging edited text and reviewer summaries."""
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.id == item_id)
            .values(
                status=status,
                edited_response=edited_response,
                reviewer_notes=reviewer_notes,
                assigned_to=assigned_to,
                resolved_at=datetime.datetime.utcnow()
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()
        return await self.get_by_id(item_id)
