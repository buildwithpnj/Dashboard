import os
import sys
from collections.abc import AsyncGenerator
from urllib.parse import urlparse, urlunparse, quote, unquote

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def get_sanitized_db_url() -> str:
    # 1. Fetch raw URL directly from environment variables first (as injected by Render)
    raw_url = (
        os.environ.get("DATABASE_URL") or 
        os.environ.get("DATABASE_PRIVATE_URL") or 
        settings.database_url
    )
    
    if not raw_url:
        return raw_url

    # 2. Clean leading/trailing whitespace and quotes
    raw_url = raw_url.strip().strip('"').strip("'")
    
    try:
        parsed = urlparse(raw_url)
        scheme = parsed.scheme
        
        # Standardize scheme for asyncpg
        if scheme in ("postgres", "postgresql"):
            scheme = "postgresql+asyncpg"
            
        netloc = parsed.netloc
        if '@' in netloc:
            userinfo, hostinfo = netloc.rsplit('@', 1)
            if ':' in userinfo:
                username, password = userinfo.split(':', 1)
                # URL-encode username and password safely to prevent special character parse issues
                username = quote(unquote(username))
                password = quote(unquote(password))
                userinfo = f"{username}:{password}"
            else:
                userinfo = quote(unquote(userinfo))
            netloc = f"{userinfo}@{hostinfo}"
            
        # Reconstruct standardized URL
        return urlunparse((
            scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
    except Exception as e:
        print(f"DEBUG: urlparse failed for URL: {raw_url}. Error: {e}", file=sys.stderr)
        # Fallback: simple prefix replacement if urllib parsing fails
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif raw_url.startswith("postgresql://"):
            return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return raw_url


db_url = get_sanitized_db_url()

# Print debug info to help verify on Render logs
print(f"DEBUG: final engine database URL: {repr(db_url)}", file=sys.stderr)

try:
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
except Exception as e:
    print(f"DEBUG: create_async_engine failed. Error: {e}", file=sys.stderr)
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
