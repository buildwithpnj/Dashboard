import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.persistence_hardening_service import PersistenceHardeningService
from app.models.governance import PreviewSession

@pytest.mark.asyncio
async def test_session_cleanup_job():
    db = AsyncMock()
    
    # Mock database result returning 3 older sessions
    mock_sessions = [PreviewSession(ip_address="127.0.0.1") for _ in range(3)]
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = mock_sessions
    db.execute.return_value = mock_res
    
    count = await PersistenceHardeningService.cleanup_expired_sessions(db)
    assert count == 3
    assert db.delete.call_count == 3
    db.commit.assert_called_once()
