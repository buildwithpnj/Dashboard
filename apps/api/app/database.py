from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

import sys
print(f"DEBUG: settings.database_url value: {repr(settings.database_url)}", file=sys.stderr)

try:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
except Exception as e:
    print(f"DEBUG: create_async_engine failed with URL: {repr(settings.database_url)}. Error: {e}", file=sys.stderr)
    raise

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
