import os
import json
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.observability.metrics import ObservabilityMetricsTracker
from app.security.rbac import RoleChecker
from app.security.auth import get_current_user, UserPrincipal
from app.db.models import TaskRun, CheckinRun
from app.repositories.task_runs import TaskRunsRepository
from app.repositories.checkins import CheckinRunsRepository

router = APIRouter()
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get(
    "/admin/metrics",
    summary="Retrieve aggregated system metrics",
    dependencies=[admin_only]
)
async def get_admin_metrics():
    """Loads metrics tracker summaries."""
    try:
        return ObservabilityMetricsTracker.get_summary()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred loading metrics logs: {str(e)}"
        )

@router.get("/admin/system-summary", summary="Platform configuration and engine connectivity", dependencies=[admin_only])
async def get_system_summary():
    """Aggregates active environment configurations, loaded LLM provider, and general stats."""
    from app.core.config import settings
    return {
        "app_name": settings.APP_NAME,
        "app_env": settings.APP_ENV,
        "provider": settings.MODEL_PROVIDER,
        "model": settings.MODEL_NAME,
        "auth_enabled": settings.AUTH_ENABLED,
        "celery_enabled": settings.CELERY_ENABLED
    }

@router.get("/admin/task-runs", summary="List Celery task execution run status records", dependencies=[admin_only])
async def list_task_runs(db: AsyncSession = Depends(get_db)):
    """Loads active or completed Celery task tracking details from DB."""
    stmt = select(TaskRun).order_by(TaskRun.created_at.desc())
    res = await db.execute(stmt)
    runs = res.scalars().all()
    return [
        {
            "id": r.id,
            "task_name": r.task_name,
            "status": r.status,
            "retries": r.retries,
            "duration_ms": r.duration_ms,
            "failure_reason": r.failure_reason,
            "created_at": r.created_at,
            "completed_at": r.completed_at
        }
        for r in runs
    ]

@router.get("/admin/eval-summary", summary="Summary of the latest accuracy evaluation lane run", dependencies=[admin_only])
async def get_eval_summary():
    """Parses and returns details from the latest offline/manual run log."""
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    latest_run_file = os.path.join(script_dir, "data", "evals", "runs", "live_run_latest.json")
    
    if not os.path.exists(latest_run_file):
        # Fallback to local workspace mapping
        latest_run_file = os.path.join(os.path.dirname(script_dir), "data", "evals", "runs", "live_run_latest.json")

    if not os.path.exists(latest_run_file):
        return {"status": "no_run_recorded", "message": "Run scripts/run_live_evals.py to populate records."}

    with open(latest_run_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/admin/escalations", summary="List family safety escalation triggers", dependencies=[admin_only])
async def list_escalations(db: AsyncSession = Depends(get_db)):
    """Lists parent safety runs that flagged distress alerts."""
    stmt = select(CheckinRun).filter(CheckinRun.status == "escalated")
    res = await db.execute(stmt)
    runs = res.scalars().all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "tenant_id": r.tenant_id,
            "session_id": r.session_id,
            "status": r.status,
            "escalated_at": r.escalated_at,
            "notes": r.notes
        }
        for r in runs
    ]

@router.get("/admin/alerts", summary="Check platform limits and list alerts", dependencies=[admin_only])
async def check_alerts(db: AsyncSession = Depends(get_db)):
    """Validates operational metrics and raises notifications for threshold violations."""
    alerts = []
    metrics = ObservabilityMetricsTracker.get_summary()

    # 1. Auth denials spike (Denials > 10)
    auth_denials = metrics.get("auth_denied_count", 0)
    if auth_denials > 10:
        alerts.append({
            "trigger": "AUTH_DENIAL_SPIKE",
            "severity": "CRITICAL",
            "message": f"High rate of authentication failures detected: {auth_denials} blocks."
        })

    # 2. Queue failures check (Tasks with status 'FAILURE' > 5)
    stmt = select(TaskRun).filter(TaskRun.status == "FAILURE")
    res = await db.execute(stmt)
    failed_tasks_count = len(res.scalars().all())
    if failed_tasks_count > 5:
        alerts.append({
            "trigger": "QUEUE_FAILURE_SPIKE",
            "severity": "WARNING",
            "message": f"Durable task queue failures exceed limits: {failed_tasks_count} failures."
        })

    # 3. Active escalations check (Escalated checkins > 3)
    stmt = select(CheckinRun).filter(CheckinRun.status == "escalated")
    res = await db.execute(stmt)
    escalations_count = len(res.scalars().all())
    if escalations_count > 3:
        alerts.append({
            "trigger": "ESCALATION_ANOMALY",
            "severity": "CRITICAL",
            "message": f"Wellness escalation alerts exceed limits: {escalations_count} active triggers."
        })

    return {
        "status": "healthy" if not alerts else "alerting",
        "active_alerts": alerts
    }
