import asyncio
from typing import Callable, Any

class PreviewTimeoutHandler:
    TIMEOUT_LIMIT = 5.0  # 5 seconds limit for public preview runs

    @classmethod
    async def execute_with_timeout(cls, func: Callable[[], Any], *args, **kwargs) -> Any:
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=cls.TIMEOUT_LIMIT)
        except asyncio.TimeoutError:
            raise TimeoutError("The model execution exceeded the safe timeout limit.")
