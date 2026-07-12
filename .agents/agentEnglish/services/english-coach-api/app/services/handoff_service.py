import uuid
from typing import Optional
from app.db.models import ReviewQueue
from app.repositories.review_queue import ReviewQueueRepository

class HandoffService:
    """Evaluates completions confidence metrics and routes low-confidence responses to human verification queues."""

    def __init__(self, review_repo: ReviewQueueRepository):
        self.review_repo = review_repo

    async def check_and_queue(
        self,
        request_id: str,
        tenant_id: str,
        product_id: str,
        input_text: str,
        original_response: str,
        confidence: float,
        trace_id: Optional[str] = None
    ) -> bool:
        """Determines if an output requires human validation and logs a PENDING review record if true."""
        # Low confidence (< 80%) triggers a review queue entry
        if confidence < 0.80:
            item = ReviewQueue(
                id=str(uuid.uuid4()),
                request_id=request_id,
                trace_id=trace_id or request_id,
                tenant_id=tenant_id,
                product_id=product_id,
                input_text=input_text,
                original_response=original_response,
                status="PENDING"
            )
            await self.review_repo.create(item)
            return True
        return False
