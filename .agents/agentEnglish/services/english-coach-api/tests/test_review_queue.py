import pytest
import jwt
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import ReviewQueue
from app.repositories.review_queue import ReviewQueueRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_review_queue_resolution():
    """Asserts that pending verification items can be resolved by administrators."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    tenant_id = "tenant_review"
    item_id = str(uuid.uuid4())
    
    try:
        # 1. Create a pending review item in DB
        async with AsyncSessionLocal() as db:
            repo = ReviewQueueRepository(db)
            item = ReviewQueue(
                id=item_id,
                request_id="req-123",
                tenant_id=tenant_id,
                product_id="english_coach",
                input_text="Network issue",
                original_response="Coached output",
                status="PENDING"
            )
            await repo.create(item)
            await db.commit()

        # Generate admin token
        token = jwt.encode(
            {"sub": "admin_user", "role": "admin", "tenant_id": tenant_id},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get pending reviews
        res = client.get("/v1/admin/review-queue", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

        # 3. Resolve the item
        res = client.post(
            f"/v1/admin/review/{item_id}/resolve",
            json={"status": "APPROVED", "edited_response": "Overridden coached output", "notes": "Approved by testing"},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["item"]["status"] == "APPROVED"

    finally:
        settings.AUTH_ENABLED = old_auth_state
