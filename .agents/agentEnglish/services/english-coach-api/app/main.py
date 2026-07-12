import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.log_config import setup_logging
from app.api.v1.routers import health, coach, lifeos, family, voice, admin, family_console, billing_admin, ops_admin, data_admin, eval_admin, quality_admin

# Initialize system log configuration once on startup
setup_logging(log_level=settings.LOG_LEVEL)

def create_app() -> FastAPI:
    """FastAPI application factory pattern to create clean, isolated app instances."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.2.0",
        description="Warborn Multi-Agent Platform API supporting English Coach, LifeOS health, and Family Parent Check-in."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(
        health.router,
        prefix=f"{settings.API_V1_PREFIX}/coach",
        tags=["Health"]
    )
    app.include_router(
        coach.router,
        prefix=f"{settings.API_V1_PREFIX}/coach",
        tags=["Coach"]
    )
    app.include_router(
        lifeos.router,
        prefix=f"{settings.API_V1_PREFIX}/coach",
        tags=["LifeOS"]
    )
    app.include_router(
        family.router,
        prefix=f"{settings.API_V1_PREFIX}/coach",
        tags=["Family"]
    )
    app.include_router(
        voice.router,
        prefix=f"{settings.API_V1_PREFIX}/coach",
        tags=["Voice"]
    )
    app.include_router(
        admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Admin"]
    )
    app.include_router(
        family_console.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Family Console"]
    )
    app.include_router(
        billing_admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Billing Admin"]
    )
    app.include_router(
        ops_admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Operations Admin"]
    )
    app.include_router(
        data_admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Data Admin"]
    )
    app.include_router(
        eval_admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Evaluation Admin"]
    )
    app.include_router(
        quality_admin.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Quality Admin"]
    )


    @app.on_event("startup")
    async def on_startup():
        import asyncio
        import logging
        from alembic.config import Config
        from alembic import command
        
        logger = logging.getLogger("startup_validation")
        
        def run_migrations():
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_migrations)
        logger.info("Startup Validation: Database migrations applied successfully.")
        
        # 1. DB connection check
        try:
            from sqlalchemy import select
            from app.db.session import engine
            async with engine.connect() as conn:
                await conn.execute(select(1))
            logger.info("Startup Validation: Database connection verified successfully.")
        except Exception as db_err:
            logger.error(f"Startup Validation WARNING: Database connection failed: {db_err}")

        # 2. Redis connection check if enabled
        if settings.CELERY_ENABLED:
            try:
                import redis
                r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
                r.ping()
                logger.info("Startup Validation: Redis broker connectivity verified successfully.")
            except Exception as redis_err:
                logger.error(f"Startup Validation WARNING: Redis connectivity failed: {redis_err}")

        # 3. Provider key check
        if settings.MODEL_PROVIDER.lower() == "openai" and not settings.OPENAI_API_KEY:
            logger.warning("Startup Validation WARNING: MODEL_PROVIDER is 'openai' but OPENAI_API_KEY is not configured!")

    return app

# Instantiate primary app instance for standard ASGI running (e.g. uvicorn app.main:app)
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True if settings.APP_ENV == "dev" else False
    )
