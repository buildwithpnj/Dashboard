import pytest
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.database import get_db
from app.models.governance import PreviewSession, SystemConfig

@pytest.fixture(autouse=True)
def mock_db_dependency():
    mock_session = AsyncMock()
    
    dummy_session = PreviewSession(
        id="mock_session_id",
        ip_address="127.0.0.1",
        turns=0,
        tokens=0,
        cost=0.0,
        active=True
    )
    
    async def mock_refresh(obj):
        if not getattr(obj, "id", None):
            obj.id = "mock_session_id"
            
    mock_session.refresh = mock_refresh
    
    async def mock_execute(query, *args, **kwargs):
        query_str = str(query).lower()
        mock_result = MagicMock()
        
        if "durable_preview_sessions" in query_str:
            mock_result.scalar_one_or_none.return_value = dummy_session
        elif "system_configs" in query_str:
            mock_result.scalar_one_or_none.return_value = None
        else:
            mock_result.scalar_one_or_none.return_value = None
            
        mock_result.scalars.return_value.all.return_value = []
        return mock_result
        
    mock_session.execute = mock_execute
    
    async def override_get_db():
        yield mock_session
        
    app.dependency_overrides[get_db] = override_get_db
    yield mock_session
    app.dependency_overrides.clear()
