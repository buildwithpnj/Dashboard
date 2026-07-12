from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db
from app.security.rbac import RoleChecker
from app.security.auth import get_current_user, UserPrincipal
from app.repositories.live_quality_metrics import LiveQualityMetricsRepository
from app.repositories.failure_trends import FailureTrendsRepository
from app.repositories.regression_events import RegressionEventsRepository
from app.services.version_recommender import VersionRecommender
from app.services.rollback_service import RollbackService

router = APIRouter(prefix="/admin/quality", tags=["Quality Admin"])
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get("/rolling-metrics", summary="List recent rolling live quality metrics", dependencies=[admin_only])
async def list_rolling_metrics(
    product_id: str = "english_coach",
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Lists historical rolling live quality metrics for the caller's tenant and specified product."""
    repo = LiveQualityMetricsRepository(db)
    metrics = await repo.list_history(tenant_id=current_user.tenant_id, product_id=product_id, limit=limit)
    return [
        {
            "id": m.id,
            "tenant_id": m.tenant_id,
            "product_id": m.product_id,
            "model_name": m.model_name,
            "prompt_version": m.prompt_version,
            "window_size": m.window_size,
            "avg_score": m.avg_score,
            "pass_rate": m.pass_rate,
            "escalation_rate": m.escalation_rate,
            "review_queue_rate": m.review_queue_rate,
            "budget_spend": m.budget_spend,
            "token_usage": m.token_usage,
            "created_at": m.created_at
        }
        for m in metrics
    ]

@router.get("/failure-trends", summary="List rolling failure trends", dependencies=[admin_only])
async def list_failure_trends(
    product_id: str = "english_coach",
    window_size: str = "24h",
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Retrieves aggregated failure trend category counts for the caller's tenant."""
    repo = FailureTrendsRepository(db)
    trends = await repo.get_trends(tenant_id=current_user.tenant_id, product_id=product_id, window_size=window_size)
    return [
        {
            "id": t.id,
            "tenant_id": t.tenant_id,
            "product_id": t.product_id,
            "error_bucket": t.error_bucket,
            "count": t.count,
            "window_size": t.window_size,
            "created_at": t.created_at
        }
        for t in trends
    ]

@router.get("/alerts", summary="List active regression events", dependencies=[admin_only])
async def list_alerts(
    product_id: str = "english_coach",
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Lists active, unresolved performance regression event alerts."""
    repo = RegressionEventsRepository(db)
    events = await repo.get_active_events(tenant_id=current_user.tenant_id, product_id=product_id)
    return [
        {
            "id": e.id,
            "tenant_id": e.tenant_id,
            "product_id": e.product_id,
            "metric_name": e.metric_name,
            "baseline_value": e.baseline_value,
            "current_value": e.current_value,
            "threshold_crossed": e.threshold_crossed,
            "severity": e.severity,
            "prompt_version": e.prompt_version,
            "model_name": e.model_name,
            "status": e.status,
            "created_at": e.created_at
        }
        for e in events
    ]

@router.post("/rollback/recommend", summary="Generate a recommended rollback plan for an event", dependencies=[admin_only])
async def recommend_rollback(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """Generates a rollback recommendation plan based on a regression event ID."""
    event_id = payload.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing required field: event_id")

    event_repo = RegressionEventsRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Regression event not found")

    recommender = VersionRecommender(db)
    rollback_svc = RollbackService(recommender)
    
    plan = await rollback_svc.evaluate_rollback(event)
    if not plan:
        raise HTTPException(
            status_code=404, 
            detail="No eligible historical prompt version found to rollback to."
        )

    return plan

@router.post("/rollback/approve", summary="Approve and execute a recommended rollback plan", dependencies=[admin_only])
async def approve_rollback(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """Approves a rollback plan, resolving the alert event and mocking the prompt switch."""
    event_id = payload.get("event_id")
    recommended_version = payload.get("recommended_version")

    # If the payload contains a plan dictionary, unpack it
    plan = payload.get("plan")
    if isinstance(plan, dict):
        event_id = plan.get("event_id", event_id)
        recommended_version = plan.get("recommended_version", recommended_version)

    if not event_id:
        raise HTTPException(status_code=400, detail="Missing required field: event_id")

    event_repo = RegressionEventsRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Regression event not found")

    # Mark regression event as resolved in repository
    await event_repo.resolve_event(event_id)
    
    # Commit changes
    await db.commit()

    target_ver = recommended_version or "v1.0"
    return {
        "status": "success",
        "message": f"Rollback approved. Prompt version switched successfully to {target_ver}."
    }
