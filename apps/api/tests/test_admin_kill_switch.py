import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.admin_controls_service import AdminControlsService
from app.models.governance import SystemConfig

@pytest.mark.asyncio
async def test_admin_kill_switch_active():
    db = AsyncMock()
    
    # Mock config fetch for disable_preview_globally returning "true"
    mock_cfg = SystemConfig(key="disable_preview_globally", value="true")
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_cfg
    db.execute.return_value = mock_res
    
    disabled = await AdminControlsService.is_preview_disabled(db)
    assert disabled is True
    db.execute.assert_called_once()
