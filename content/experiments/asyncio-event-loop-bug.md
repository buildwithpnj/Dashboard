---
id: "EXP-10"
title: "Incident Report: asyncio.run() Destroys FastAPI's Event Loop"
tagline: "How a one-line seeding call inside a startup thread caused every single login to return 500 for six hours."
status: "completed"
category: "Backend Engineering"
tags: ["fastapi", "asyncio", "python", "debugging", "incident"]
hypothesis: "Running asyncio.run() in a thread during app startup should safely initialize the database without blocking the main event loop."
publishDate: "2026-07-09"
---

# EXP-10: Incident Report — asyncio.run() Destroys FastAPI's Event Loop

**Status:** Completed (resolved)  
**Category:** Backend Engineering  
**Date:** 2026-07-09  
**Duration:** ~2.5 hours, 7 Render deployments  
**Resolution:** Commit `c2ab969` — 21:26 IST  
**Final state:** `POST /auth/login` returns HTTP 200 with JWT

---

## Objective

Automate database initialization on every Render deployment. Specifically:

1. Run Alembic migrations (`alembic upgrade head`) to ensure schema is always current.
2. Seed a default admin user (`prakashjhadps@gmail.com`) if one doesn't exist in the `users` table.

Both operations should happen inside FastAPI's `lifespan` startup hook so the API is fully initialized by the time the first request arrives. No manual intervention should be required after a fresh deploy.

This is standard deployment automation. It should be boring.

---

## Hypothesis

Running `asyncio.run()` inside a `ThreadPoolExecutor` thread during the FastAPI startup lifespan hook should safely execute the async seed coroutine without blocking the main event loop. The thread has its own execution context; `asyncio.run()` will create a fresh event loop inside that thread, run the coroutine, and exit cleanly. The main uvicorn event loop is unaffected.

This is what most developers assume. It is wrong.

---

## Implementation (Original — Broken)

The startup lifespan hook ran migrations synchronously via `subprocess.run(["alembic", "upgrade", "head"])`, which was fine. For seeding, the async SQLAlchemy session was needed, which meant calling an async function. The implementation used `asyncio.run()` inside a thread:

```python
# lifespan.py (original — broken)
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Migrations (synchronous — fine)
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    # Seeding (async — broken approach)
    def run_seed():
        asyncio.run(seed())  # <-- the problem

    with ThreadPoolExecutor() as pool:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(pool, run_seed)

    yield
    # shutdown logic
```

And `seed()` was an async coroutine using the SQLAlchemy async session:

```python
# seed.py (original — broken)
async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "prakashjhadps@gmail.com")
        )
        if result.scalar_one_or_none() is None:
            user = User(
                email="prakashjhadps@gmail.com",
                hashed_password=get_password_hash("defaultpassword"),
                is_active=True,
            )
            session.add(user)
            await session.commit()
```

This looked reasonable. It was not.

---

## The Failure

After the migrations ran successfully and the seed ostensibly completed without raising an exception, every subsequent request to any database-touching endpoint returned HTTP 500. The Render logs showed a single recurring error on every request:

```
RuntimeError: Event loop is closed
  File ".../sqlalchemy/ext/asyncio/engine.py", line 123, in connect
    ...
  File ".../asyncio/futures.py", line 201, in result
    raise self._exception
RuntimeError: Event loop is closed
```

The error wasn't happening during startup. It was happening on the first `await db.execute(...)` inside a normal request handler, well after the lifespan hook had completed and the API had reported itself as ready. The Render health check was passing. The API was "up." But every login attempt, every database read, every database write — all 500.

---

## Investigation Process

### Deployment 1 — URL Scheme Mismatch

Before hitting the event loop bug, we first had to get through a stack of precondition failures. The first Render deployment failed during migration because Render injects `DATABASE_URL` as `postgresql://`, but SQLAlchemy async requires `postgresql+asyncpg://`.

**Error:**
```
sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql
```

**Fix (commit `a7f4a82`):** Add a scheme rewrite in `config.py`:

```python
@property
def database_url(self) -> str:
    url = os.environ.get("DATABASE_URL", "")
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)
```

### Deployment 2 — Password Special Character

The database password is `dobbie@KAP1`. The `@` character is the URL authority delimiter. Python's `urlparse` sees:

```
postgresql+asyncpg://user:dobbie  <-- split here
KAP1@db.host.supabase.co/dbname   <-- treated as host
```

The connection string was being handed to asyncpg with a mangled hostname.

**Error:**
```
asyncpg.exceptions.InvalidAuthorizationSpecificationError:
password authentication failed for user "..."
```

**Fix (commits `da78343`, `19a5820`):** Parse the URL into components with `urllib.parse.urlsplit`, URL-encode the password field using `urllib.parse.quote(password, safe='')`, reconstruct with `urlunsplit`.

### Deployment 3 — DATABASE_URL= Literal Prefix

When copied from Render's environment variable dashboard, the value sometimes includes the variable key as part of the string:

```
DATABASE_URL=postgresql://user:pass@host/db
```

`urlsplit("DATABASE_URL=postgresql://...")` does not parse this as a URL — it produces a nonsense result with no scheme.

**Fix (commit `f5ce6a6`):**
```python
url = url.removeprefix("DATABASE_URL=").strip()
```

### Deployment 4 — PgBouncer Statement Cache

Supabase exposes PostgreSQL through PgBouncer in transaction pooling mode. PgBouncer in this mode does not support named prepared statements — each transaction is handled by a potentially different backend connection, and prepared statements are per-connection. SQLAlchemy and asyncpg both cache prepared statements by default.

**Error:**
```
asyncpg.exceptions.FeatureNotSupportedError:
prepared statement "__asyncpg_stmt_0__" already exists
```

**Fix (commit `562c032`):** Disable statement cache on both the async engine and the Alembic sync engine:

```python
# database.py
engine = create_async_engine(
    settings.database_url,
    connect_args={"statement_cache_size": 0},
)

# alembic/env.py
connectable = create_engine(
    sync_url,
    connect_args={"statement_cache_size": 0},
)
```

### Deployment 5 — ConfigParser `%` Escaping

Alembic reads configuration via Python's `configparser` module. ConfigParser treats `%` as the start of an interpolation directive (`%(varname)s` format). The URL-encoded `@` in the database password is `%40`. When this string was written into the Alembic config object:

```python
config.set_main_option("sqlalchemy.url", database_url)
```

ConfigParser attempted to interpolate `%40` as a variable reference, found it malformed, and raised:

```
configparser.InterpolationSyntaxError:
'%' must be followed by '%' or '(', found: '%40'
  File "alembic/env.py", line 18, in run_migrations_online
```

**Fix (commit `21a52f5`):** Double every `%` before writing to the config:

```python
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)
```

After deployment 5, migrations completed. Seeding reported success. The API started. The health check passed.

Login returned 500.

### Deployment 6 — Chasing the Event Loop Error

The `RuntimeError: Event loop is closed` error appeared on every database operation after startup. Initial hypotheses:

- The async engine was being created before the event loop started. (Ruled out — we verified engine creation was inside the lifespan hook.)
- The session factory was holding a reference to a closed engine. (Ruled out — the error appeared on fresh requests with fresh sessions.)
- uvicorn was using a different event loop than the one SQLAlchemy was initialized on. (Partially correct framing — but we were looking at the wrong layer.)

We added startup debug logging (`e209b71`):

```python
import asyncio
import logging

logger.info(f"Event loop id at startup: {id(asyncio.get_event_loop())}")
```

And compared to the loop id inside a failing request handler. They were different. The startup loop and the request-handling loop were different objects. The startup loop was closed; the request loop was the "new" default — which was also closed because the original had been closed.

### Deployment 7 — Root Cause Isolated

The debug output made the sequence clear. The startup lifespan ran `asyncio.run(seed())` inside a thread. After that call, `asyncio.get_event_loop()` returned a closed loop object. All subsequent `await` calls on the async engine used this closed loop.

---

## The Root Cause

`asyncio.run()` is specified by PEP 3156 and documented in the Python stdlib. What the documentation says:

> This function always creates a new event loop and closes it at the end.

Key word: **closes it at the end.**

`asyncio.run()` does the following in CPython's implementation:

```python
def run(main, *, debug=None):
    if events._get_running_loop() is not None:
        raise RuntimeError("asyncio.run() cannot be called from a running event loop")
    
    loop = events.new_event_loop()
    try:
        events.set_event_loop(loop)  # <-- sets as default event loop
        # ... run the coroutine ...
        return loop.run_until_complete(main)
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            events.set_event_loop(None)  # <-- clears the default event loop
            loop.close()                 # <-- closes the loop
```

Two critical lines:
1. `events.set_event_loop(loop)` — when called from inside a thread, this sets the default event loop **for the process**, not just the thread.
2. `events.set_event_loop(None)` in the `finally` block — clears the process-level default event loop to `None` after the temporary loop is closed.

The sequence in our application:

```
[Main Thread]
uvicorn creates loop_A, sets it as the process default event loop.
FastAPI lifespan fires.
lifespan calls loop_A.run_in_executor(pool, run_seed).

[Worker Thread - run_seed]
asyncio.run(seed()) is called.
asyncio.run() internally:
  → creates loop_B
  → sets loop_B as process default (replaces loop_A as default)
  → runs seed() on loop_B
  → closes loop_B
  → sets process default event loop to None

[Main Thread - resumes]
uvicorn is still running on loop_A (loop_A object is still alive and running).
BUT: asyncio.get_event_loop() now returns None or raises RuntimeError.
Any code path that calls asyncio.get_event_loop() to access the running loop
finds None or a closed loop.
AsyncSessionLocal() internally uses get_event_loop() to schedule coroutines.
→ RuntimeError: Event loop is closed on every request.
```

This is subtle. `loop_A` (uvicorn's loop) is still running — it never got closed. The problem is that the process-level default event loop reference was replaced and then cleared by `asyncio.run()` in the worker thread. Any code that looks up the default event loop now fails.

---

## The Fix

Remove asyncio entirely from the seed path. The seed operation is a one-time startup task that inserts at most one row. It does not benefit from async I/O. Rewrite it as a synchronous function using `psycopg2` directly through SQLAlchemy's sync dialect.

```python
# seed.py (fixed — commit c2ab969)
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

def seed_sync() -> None:
    """
    Synchronous seed function. Safe to call from a thread.
    Uses psycopg2 (sync) driver — zero interaction with the asyncio event loop.
    """
    # Convert async URL to sync URL for psycopg2
    sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(sync_url, connect_args={"sslmode": "require"})

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email LIMIT 1"),
                {"email": "prakashjhadps@gmail.com"}
            )
            if result.fetchone() is not None:
                logger.info("Seed user already exists — skipping.")
                return

            conn.execute(
                text("""
                    INSERT INTO users (email, hashed_password, is_active, is_superuser)
                    VALUES (:email, :pw, true, true)
                """),
                {
                    "email": "prakashjhadps@gmail.com",
                    "pw": get_password_hash("defaultpassword"),
                }
            )
            conn.commit()
            logger.info("Seed user created: prakashjhadps@gmail.com")
    finally:
        engine.dispose()
```

The lifespan hook calls it directly in the thread:

```python
# lifespan.py (fixed)
def run_startup_tasks():
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    seed_sync()  # synchronous — no asyncio.run()

with ThreadPoolExecutor() as pool:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(pool, run_startup_tasks)
```

`seed_sync()` runs synchronously inside the thread. It uses `psycopg2` (a blocking, synchronous PostgreSQL driver) through SQLAlchemy's synchronous engine. It never touches `asyncio.run()`, `asyncio.get_event_loop()`, or any asyncio primitive. It cannot interfere with the uvicorn event loop because it is entirely outside the asyncio execution model.

---

## Verification

Commit `c2ab969` deployed to Render at 21:26 IST.

Render startup logs:

```
INFO: Running Alembic migrations...
INFO: alembic.runtime.migration - Running upgrade -> abc123, initial schema
INFO: Seed user created: prakashjhadps@gmail.com
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:10000
```

Login test:

```bash
curl -X POST https://dashboard-nb61.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "prakashjhadps@gmail.com", "password": "defaultpassword"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

HTTP 200. The bug was gone.

---

## Lessons Learned

**1. `asyncio.run()` is a script-level function.**
It is designed to be the outermost call in a Python script — `if __name__ == "__main__": asyncio.run(main())`. It explicitly creates and closes an event loop. Do not call it inside a running async application, and especially do not call it from a thread inside a running async application. The `finally: loop.close()` semantics make it inherently unsafe in this context.

**2. If you need to call async code from a non-async context inside a running server, use `loop.run_until_complete()` from the already-running loop.**
But get the loop *before* spawning the thread. `asyncio.get_event_loop()` inside a thread is implementation-defined in newer Python versions (3.10+ emits a DeprecationWarning and will eventually raise). The safest pattern is to pass the loop explicitly into the thread:

```python
loop = asyncio.get_event_loop()

def run_in_thread():
    future = asyncio.run_coroutine_threadsafe(seed(), loop)
    future.result(timeout=30)

with ThreadPoolExecutor() as pool:
    pool.submit(run_in_thread).result()
```

**3. The better answer is: don't use async for one-time startup I/O.**
Seeding a database once at startup is not a performance-sensitive operation. Synchronous psycopg2 is fast enough. The complexity introduced by async seeding — managing event loop lifecycle, thread safety, coroutine scheduling — was not justified by any performance requirement.

**4. Compound failures obscure root causes.**
We hit five distinct, unrelated failures (URL scheme, password encoding, literal prefix, PgBouncer cache, ConfigParser escaping) before reaching the actual root cause. Each fix was real and necessary, but each also extended the debugging cycle. A local Docker environment that mirrors Render's injection behavior would have surfaced all five failures in a single local test run rather than across seven deployments.

---

## Prevention

**Rule:** Never call `asyncio.run()` inside a FastAPI lifespan hook or any code path executed during server runtime.

**Enforcement (to be added to CI):**
- `grep -r "asyncio.run(" app/` in CI pipeline, fail if found anywhere except `if __name__ == "__main__"` blocks.

**Tooling:**
- Add a local `docker-compose.yml` that mirrors the Render environment, including environment variable injection with the `DATABASE_URL=` prefix quirk, for pre-deployment validation.

**Code pattern:**
- One-time startup operations (migrations, seeding, cache warming) → use synchronous code with synchronous drivers.
- Runtime request handlers → use async SQLAlchemy with asyncpg.
- Never mix the two in ways that cross the asyncio boundary.
