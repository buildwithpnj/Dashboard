import sys
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    accounts,
    auth,
    books,
    budgets,
    categories,
    dashboard,
    gdrive,
    habits,
    notes,
    transactions,
    gcalendar,
    recovery,
    aicoach,
    public_preview,
    warborn_chat,
    governance_router,
)
from app.middleware.preview_rate_limit import PreviewRateLimitMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate environment configurations at startup
    from app.storage.config_validator import validate_config
    validate_config()

    # Run Alembic migrations via subprocess — fully isolated from asyncio, works with --reload
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"MIGRATION ERROR:\n{result.stderr}", file=sys.stderr, flush=True)
    else:
        print("DEBUG: Migrations applied.", file=sys.stderr, flush=True)

    # Run seed synchronously via asyncio.to_thread (safe with --reload)
    import asyncio
    async def _seed():
        from seed import seed_sync
        await asyncio.to_thread(seed_sync)

    await _seed()
    print("DEBUG: Seeding complete.", file=sys.stderr, flush=True)

    yield
    # Shutdown
    from app.database import engine
    await engine.dispose()





app = FastAPI(
    title="WarBorn OS API",
    description="Single-user WarBorn operating system backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - include live domain alongside localhost
cors_origins = settings.cors_origins.split(",")
if "https://buildwithpnj.in" not in cors_origins:
    cors_origins.append("https://buildwithpnj.in")
if "https://www.buildwithpnj.in" not in cors_origins:
    cors_origins.append("https://www.buildwithpnj.in")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PreviewRateLimitMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"UNHANDLED 500 ERROR on {request.method} {request.url}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Mount routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(dashboard.router)
app.include_router(gdrive.router)
app.include_router(notes.router)
app.include_router(books.router)
app.include_router(habits.router)
app.include_router(gcalendar.router)
app.include_router(recovery.router)
app.include_router(aicoach.router)
app.include_router(public_preview.router)
app.include_router(warborn_chat.router)
app.include_router(governance_router.router)

from app.storage.routes import router as storage_router
app.include_router(storage_router)



@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

