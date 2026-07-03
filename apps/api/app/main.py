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
    # Startup
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
