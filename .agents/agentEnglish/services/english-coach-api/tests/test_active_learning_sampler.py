import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import HardCase
from app.repositories.hard_case_queue import HardCaseQueueRepository
from app.services.active_learning_sampler import ActiveLearningSampler

@pytest.mark.anyio
async def test_active_learning_sampler():
    async with AsyncSessionLocal() as session:
        hard_case_repo = HardCaseQueueRepository(session)
        sampler = ActiveLearningSampler(hard_case_repo)

        tenant_id = f"tenant-{uuid.uuid4()}"
        product_id = "english_coach"

        # Candidate examples from logs
        candidates = [
            {"source_text": "Easy text.", "composite_score": 0.95}, # high trust - skip
            {"source_text": "Hard confusing text.", "composite_score": 0.58}, # low trust - sample!
            {"source_text": "Completely wrong text.", "composite_score": 0.20} # very low - skip/hard-negative
        ]

        sampled = await sampler.sample_candidates(tenant_id, product_id, candidates)
        assert len(sampled) == 1
        assert sampled[0].input_text == "Hard confusing text."
        assert sampled[0].priority == 3

        # Check in DB queue
        pending = await hard_case_repo.get_pending(tenant_id)
        assert len(pending) == 1
        assert pending[0].input_text == "Hard confusing text."

        await session.rollback()
