import pytest
import jwt
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.mark.anyio
async def test_dataset_registration_and_metrics_endpoints():
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    # Create a temporary input file
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False, encoding="utf-8") as f:
        f.write("Some mock document chunks content details.")
        tmp_name = f.name
        
    try:
        token = jwt.encode(
            {"sub": "admin_user", "role": "admin", "tenant_id": "tenant_dataset"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Register Dataset
        res = client.post(
            "/v1/admin/data/dataset",
            json={"name": "Test Ingest", "version": "v1.0", "file_path": tmp_name},
            headers=headers
        )
        assert res.status_code == 200
        dataset_id = res.json()["dataset"]["id"]

        # 2. Ingest Dataset
        res = client.post(
            f"/v1/admin/data/dataset/{dataset_id}/ingest",
            headers=headers
        )
        assert res.status_code == 200

        # 3. Check status
        res = client.get(
            f"/v1/admin/data/dataset/{dataset_id}/status",
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["status"] == "INGESTED"

        # 4. View Metrics
        res = client.get(
            "/v1/admin/data/dataset-metrics",
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["total_documents"] >= 1
        assert res.json()["total_chunks"] >= 1

    finally:
        os.remove(tmp_name)
        settings.AUTH_ENABLED = old_auth_state
