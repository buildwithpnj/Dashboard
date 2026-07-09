from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run database migrations and seeding in a separate thread to avoid event loop conflicts
    import sys
    import threading
    
    def run_migrations_and_seed():
        print("DEBUG: Running database migrations in worker thread...", file=sys.stderr)
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            print("DEBUG: Database migrations applied successfully in thread!", file=sys.stderr)
            
            # Run async seed_data in this clean thread event loop
            import asyncio
            from seed import seed_data
            asyncio.run(seed_data())
            print("DEBUG: Database seeding complete in thread!", file=sys.stderr)
        except Exception as e:
            print(f"DEBUG: Thread migrations/seeding failed: {e}", file=sys.stderr)

    thread = threading.Thread(target=run_migrations_and_seed)
    thread.start()
    thread.join() # Wait for database initialization to finish before starting API
    
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
