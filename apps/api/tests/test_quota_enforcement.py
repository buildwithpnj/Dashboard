import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.admin_controls_service import AdminControlsService
from app.models.governance import PreviewSession, SystemConfig

@pytest.mark.asyncio
async def test_quota_limits_checking():
    db = AsyncMock()
    
    # Mock config fetch for preview_token_cap returning "2000"
    mock_cfg = SystemConfig(key="preview_token_cap", value="2000")
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_cfg
    db.execute.return_value = mock_res
    
    val = await AdminControlsService.get_config(db, "preview_token_cap", "2000")
    assert val == "2000"
    db.execute.assert_called_once()
