import pytest
import jwt
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import PromptVersion
from app.repositories.prompt_versions import PromptVersionsRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_prompt_versions_activation():
    """Asserts that prompt versions can be registered, listed, and activated."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    version_id = str(uuid.uuid4())
    try:
        # 1. Create a prompt version
        async with AsyncSessionLocal() as db:
            repo = PromptVersionsRepository(db)
            pv = PromptVersion(
                id=version_id,
                product_id="english_coach",
                task_id="correction",
                version="v2.0",
                prompt_template="Test template: {text}",
                is_active=False
            )
            await repo.create(pv)
            await db.commit()

        # Generate admin token
        token = jwt.encode(
            {"sub": "admin_user", "role": "admin", "tenant_id": "tenant_test"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 2. List prompt versions
        res = client.get("/v1/admin/prompt-versions", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

        # 3. Activate the prompt version
        res = client.post(
            "/v1/admin/prompt-activate",
            json={"version_id": version_id},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["activated_version"] == "v2.0"

    finally:
        settings.AUTH_ENABLED = old_auth_state
