import pytest
import asyncio
from app.services.preview_timeout_handler import PreviewTimeoutHandler

@pytest.mark.asyncio
async def test_execution_timeout_trigger():
    async def slow_function():
        await asyncio.sleep(6.0)  # Exceeds the 5.0 seconds limit
        return "done"

    with pytest.raises(TimeoutError):
        await PreviewTimeoutHandler.execute_with_timeout(slow_function)
