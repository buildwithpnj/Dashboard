import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import ReviewerProductivity
from app.repositories.reviewer_productivity import ReviewerProductivityRepository
from app.services.review_prioritizer import ReviewPrioritizer

def test_review_prioritizer():
    prioritizer = ReviewPrioritizer()

    backlog = [
        {"id": "1", "composite_score": 0.95}, # Low risk
        {"id": "2", "composite_score": 0.50}, # Low confidence confusion (+2.0)
        {"id": "3", "composite_score": 0.95, "input_text": "Please help suicide emergency"} # Wellness emergency (+3.0)
    ]

    prioritized = prioritizer.prioritize(backlog)
    assert prioritized[0]["id"] == "3" # Urgent first
    assert prioritized[1]["id"] == "2" # Confusion next

@pytest.mark.anyio
async def test_reviewer_productivity_tracking():
    async with AsyncSessionLocal() as session:
        repo = ReviewerProductivityRepository(session)
        reviewer_id = f"rev-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"

        # 1. First resolution - aligned (drift starts at 0.5 default)
        await repo.update_productivity(reviewer_id, tenant_id, duration_ms=5000.0, is_aligned=True)
        
        prod = await repo.get_by_reviewer(reviewer_id, tenant_id)
        assert prod is not None
        assert prod.resolutions_count == 1
        assert prod.avg_duration_ms == 5000.0
        assert prod.drift_score == 0.45 # 0.5 - 0.05

        # 2. Second resolution - non-aligned (drift penalty)
        await repo.update_productivity(reviewer_id, tenant_id, duration_ms=7000.0, is_aligned=False)
        prod_updated = await repo.get_by_reviewer(reviewer_id, tenant_id)
        assert prod_updated.resolutions_count == 2
        assert prod_updated.avg_duration_ms == 6000.0 # (5000 + 7000) / 2
        assert prod_updated.drift_score == 0.55 # 0.45 + 0.10

        await session.rollback()
