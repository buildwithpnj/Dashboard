import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    """Module-scoped client fixture using FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
