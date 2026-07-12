import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.admin_controls_service import AdminControlsService
from app.models.governance import SystemConfig

@pytest.mark.asyncio
async def test_audit_logs_logging():
    db = AsyncMock()
    
    # Mock config search returning None initially
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_res
    
    await AdminControlsService.set_config(db, admin_id="admin_123", key="disable_preview_globally", value="true")
    
    # Should call db.add twice (one config, one audit log)
    assert db.add.call_count == 2
    db.commit.assert_called_once()
