import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.access_governance_service import AccessGovernanceService
from app.models.governance import AccessRequest

@pytest.mark.asyncio
async def test_create_access_request():
    db = AsyncMock()
    async def mock_refresh(obj):
        obj.id = "req_123"
    db.refresh = mock_refresh
    
    req = await AccessGovernanceService.create_request(db, "Test User", "test@example.com", "Testing rollout")
    assert req.name == "Test User"
    assert req.email == "test@example.com"
    assert req.status == "pending"
    db.add.assert_called_once()
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_approve_request():
    db = AsyncMock()
    req = AccessRequest(name="Test User", email="test@example.com", status="pending")
    
    mock_req_res = MagicMock()
    mock_req_res.scalar_one_or_none.return_value = req
    
    mock_user_res = MagicMock()
    mock_user_res.scalar_one_or_none.return_value = None
    
    db.execute.side_effect = [mock_req_res, mock_user_res]
    
    ok = await AccessGovernanceService.approve_request(db, "req_123")
    assert ok is True
    assert req.status == "approved"
    db.commit.assert_called_once()
