from typing import Optional
from app.db.models import ReviewQueue
from app.repositories.review_queue import ReviewQueueRepository

class ReviewService:
    """Manages manual modifications, approvals, rejections, and resolution updates of queued review cases."""

    def __init__(self, review_repo: ReviewQueueRepository):
        self.review_repo = review_repo

    async def resolve_item(
        self,
        item_id: str,
        status: str,
        edited_response: Optional[str] = None,
        notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[ReviewQueue]:
        """Locks in human operator decisions, applying text modifications and updates status flags."""
        if status not in ["APPROVED", "REJECTED", "RESOLVED"]:
            raise ValueError(f"Invalid resolution status: {status}")

        return await self.review_repo.resolve_review_item(
            item_id=item_id,
            status=status,
            edited_response=edited_response,
            reviewer_notes=notes,
            assigned_to=assigned_to
        )
