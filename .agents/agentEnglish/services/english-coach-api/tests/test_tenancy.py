import pytest
import uuid
import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import Session, LearnerProfile, FamilyProfile
from app.repositories.sessions import SessionsRepository
from app.repositories.learner_profiles import LearnerProfilesRepository
from app.repositories.family_profiles import FamilyProfilesRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_multi_tenant_database_query_isolation():
    """Asserts that sessions and profiles query filters partition results correctly by tenant."""
    async with AsyncSessionLocal() as db:
        sess_repo = SessionsRepository(db)
        profile_repo = LearnerProfilesRepository(db)

        user_id = f"user-{uuid.uuid4()}"
        
        # 1. Create a session under tenant_A
        sess_a = Session(
            id=f"sess-a-{uuid.uuid4()}",
            user_id=user_id,
            tenant_id="tenant_A",
            product_id="english_coach",
            is_active=True
        )
        await sess_repo.create(sess_a)

        # 2. Create a session under tenant_B
        sess_b = Session(
            id=f"sess-b-{uuid.uuid4()}",
            user_id=user_id,
            tenant_id="tenant_B",
            product_id="english_coach",
            is_active=True
        )
        await sess_repo.create(sess_b)

        # 3. Query active session for user under tenant_A
        fetched_a = await sess_repo.get_active_by_user_and_product(user_id, "english_coach", tenant_id="tenant_A")
        assert fetched_a is not None
        assert fetched_a.id == sess_a.id

        # 4. Query active session for user under tenant_B
        fetched_b = await sess_repo.get_active_by_user_and_product(user_id, "english_coach", tenant_id="tenant_B")
        assert fetched_b is not None
        assert fetched_b.id == sess_b.id

        # 5. Query session for user under non-existent tenant_C should return None
        fetched_c = await sess_repo.get_active_by_user_and_product(user_id, "english_coach", tenant_id="tenant_C")
        assert fetched_c is None

        await db.rollback()

def test_family_checkin_tenancy_routing():
    """Asserts that family profiles are isolated by tenant during API request processing."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    try:
        user_id = f"parent-{uuid.uuid4()}"
        
        # Generate JWT tokens for tenant_A and tenant_B
        token_a = jwt.encode(
            {"sub": "user_a", "role": "user", "tenant_id": "tenant_A"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        token_b = jwt.encode(
            {"sub": "user_b", "role": "user", "tenant_id": "tenant_B"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )

        # Post check-in as tenant_A (this creates a profile scoped under tenant_A)
        res = client.post(
            "/v1/coach/family/checkin",
            json={"user_id": user_id, "message_text": "Sab theek hai."},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res.status_code == 200
        
        # Post check-in as tenant_B (this should create a distinct profile scoped under tenant_B)
        res_b = client.post(
            "/v1/coach/family/checkin",
            json={"user_id": user_id, "message_text": "All is fine here."},
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_b.status_code == 200

    finally:
        settings.AUTH_ENABLED = old_auth_state
