import pytest
import jwt
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import ReviewQueue, FeedbackExample
from app.repositories.review_queue import ReviewQueueRepository
from app.repositories.feedback_examples import FeedbackExamplesRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_human_learning_loop_flywheel():
    """Asserts that resolving a review queue item propagates positive/negative examples into feedback memory."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    tenant_id = "tenant_flywheel"
    item_id = str(uuid.uuid4())
    
    try:
        # 1. Create a pending review item
        async with AsyncSessionLocal() as db:
            review_repo = ReviewQueueRepository(db)
            item = ReviewQueue(
                id=item_id,
                request_id="req-flywheel",
                tenant_id=tenant_id,
                product_id="english_coach",
                input_text="My hinge text input",
                original_response="Coached natural reply response",
                status="PENDING"
            )
            await review_repo.create(item)
            await db.commit()

        # Admin jwt token
        token = jwt.encode(
            {"sub": "admin_ops", "role": "admin", "tenant_id": tenant_id},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Resolve queue item as APPROVED
        res = client.post(
            f"/v1/admin/review/{item_id}/resolve",
            json={"status": "APPROVED", "edited_response": "Overridden polished sentence", "notes": "flywheel pass"},
            headers=headers
        )
        assert res.status_code == 200

        # 3. Verify that the learning flywheel created a positive FeedbackExample
        async with AsyncSessionLocal() as db:
            fb_repo = FeedbackExamplesRepository(db)
            examples = await fb_repo.get_examples_by_status(tenant_id, "english_coach", "positive")
            assert len(examples) == 1
            assert examples[0].input_text == "My hinge text input"
            assert examples[0].output_text == "Overridden polished sentence"

            # Cleanup
            await fb_repo.delete(examples[0])
            await db.commit()

    finally:
        settings.AUTH_ENABLED = old_auth_state
