import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_probe():
    res = client.get("/v1/coach/health/live")
    assert res.status_code == 200
    assert res.json() == {"status": "alive"}

def test_readiness_probe():
    res = client.get("/v1/coach/health/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ready"}

def test_dependencies_health_probe():
    res = client.get("/v1/coach/health/dependencies")
    assert res.status_code == 200
    data = res.json()
    assert "database" in data
    assert "redis" in data
    assert data["database"] == "healthy"
