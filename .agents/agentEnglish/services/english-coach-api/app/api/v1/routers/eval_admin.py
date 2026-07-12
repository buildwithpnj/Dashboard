from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.db.models import BatchEvalRun, EvalExampleResult, GoldExample, HardNegativeExample
from app.security.auth import get_current_user, UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter(prefix="/admin/eval", tags=["Evaluation Admin"])
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get("/runs", summary="List recent evaluation runs", dependencies=[admin_only])
async def list_runs(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Retrieves recent evaluation runs for the authenticated tenant."""
    stmt = (
        select(BatchEvalRun)
        .where(BatchEvalRun.tenant_id == current_user.tenant_id)
        .order_by(BatchEvalRun.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    runs = res.scalars().all()
    return [
        {
            "id": r.id,
            "dataset_name": r.dataset_name,
            "product_id": r.product_id,
            "status": r.status,
            "total_examples": r.total_examples,
            "processed_count": r.processed_count,
            "passed_count": r.passed_count,
            "failed_count": r.failed_count,
            "cost_usd": r.cost_usd,
            "started_at": r.started_at,
            "completed_at": r.completed_at
        }
        for r in runs
    ]

@router.get("/run/{id}/summary", summary="Retrieve detailed run status and metrics", dependencies=[admin_only])
async def get_run_summary(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full progress, cost and failure metrics for a specific run ID."""
    run_stmt = select(BatchEvalRun).where(BatchEvalRun.id == id)
    res = await db.execute(run_stmt)
    run = res.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
        
    return {
        "run_id": run.id,
        "dataset_name": run.dataset_name,
        "product_id": run.product_id,
        "status": run.status,
        "cost_usd": run.cost_usd,
        "total_examples": run.total_examples,
        "processed_count": run.processed_count,
        "passed_count": run.passed_count,
        "failed_count": run.failed_count,
        "total_tokens": run.total_tokens
    }

@router.get("/stats", summary="Show aggregate gold and hard-negative promotion counts", dependencies=[admin_only])
async def get_promotion_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Provides counts of gold and hard negatives currently registered under the tenant."""
    # Count Gold Examples
    gold_stmt = select(GoldExample).where(GoldExample.tenant_id == current_user.tenant_id)
    gold_res = await db.execute(gold_stmt)
    gold_items = gold_res.scalars().all()
    
    gold_status = {}
    for item in gold_items:
        gold_status[item.review_status] = gold_status.get(item.review_status, 0) + 1
        
    # Count Hard Negatives
    neg_stmt = select(HardNegativeExample).where(HardNegativeExample.tenant_id == current_user.tenant_id)
    neg_res = await db.execute(neg_stmt)
    neg_items = neg_res.scalars().all()
    
    neg_buckets = {}
    for item in neg_items:
        neg_buckets[item.error_bucket] = neg_buckets.get(item.error_bucket, 0) + 1
        
    return {
        "tenant_id": current_user.tenant_id,
        "total_gold_examples": len(gold_items),
        "gold_status_breakdown": gold_status,
        "total_hard_negatives": len(neg_items),
        "hard_negatives_by_bucket": neg_buckets
    }
