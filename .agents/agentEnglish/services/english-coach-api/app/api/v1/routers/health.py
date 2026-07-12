from fastapi import APIRouter, HTTPException, status
from app.schemas.common import HealthCheck
from app.core.config import settings
from app.db.session import engine
from sqlalchemy import select

router = APIRouter()

@router.get("/health", response_model=HealthCheck, summary="Perform System Health Check")
def get_health() -> HealthCheck:
    """Returns application status details to ensure service is operational."""
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        app_name=settings.APP_NAME,
        app_env=settings.APP_ENV
    )

@router.get("/health/live", summary="Liveness probe checking container status")
def get_liveness():
    """Simple probe ensuring the ASGI server process is alive."""
    return {"status": "alive"}

@router.get("/health/ready", summary="Readiness probe checking database connectivity")
async def get_readiness():
    """Confirms that the database connection is open and active."""
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection offline: {str(e)}"
        )

@router.get("/health/dependencies", summary="Detailed dependencies metrics")
async def get_dependencies_health():
    """Aggregates checks for SQL database and Redis task broker systems."""
    health_results = {
        "database": "healthy",
        "redis": "healthy" if settings.CELERY_ENABLED else "disabled"
    }
    
    # 1. DB check
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as e:
        health_results["database"] = f"unhealthy: {e}"
        
    # 2. Redis check if Celery is enabled
    if settings.CELERY_ENABLED:
        try:
            import redis
            r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=1)
            r.ping()
        except Exception as e:
            health_results["redis"] = f"unhealthy: {e}"

    if any("unhealthy" in str(val) for val in health_results.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_results
        )
        
    return health_results
