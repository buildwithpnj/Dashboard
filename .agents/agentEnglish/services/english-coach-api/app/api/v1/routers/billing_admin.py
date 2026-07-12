from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_usage_ledger_repository
from app.db.models import UsageLedger
from app.repositories.usage_ledger import UsageLedgerRepository
from app.security.auth import get_current_user, UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter(prefix="/admin", tags=["Billing Admin"])
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get("/usage-summary", summary="Retrieve tenant token and expenditure metrics", dependencies=[admin_only])
async def get_usage_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Aggregates monthly token counts and cost estimates for the caller's tenant."""
    stmt = select(
        func.sum(UsageLedger.token_input).label("total_input"),
        func.sum(UsageLedger.token_output).label("total_output"),
        func.sum(UsageLedger.cost_usd).label("total_cost")
    ).filter(UsageLedger.tenant_id == current_user.tenant_id)
    
    res = await db.execute(stmt)
    row = res.fetchone()
    
    return {
        "tenant_id": current_user.tenant_id,
        "total_input_tokens": int(row[0]) if row and row[0] is not None else 0,
        "total_output_tokens": int(row[1]) if row and row[1] is not None else 0,
        "total_estimated_cost_usd": float(row[2]) if row and row[2] is not None else 0.0
    }

@router.get("/tenant-costs", summary="List cost aggregates across all tenants", dependencies=[admin_only])
async def get_tenant_costs(db: AsyncSession = Depends(get_db)):
    """Compiles costs grouped across all active tenant databases partitions."""
    stmt = select(
        UsageLedger.tenant_id,
        func.sum(UsageLedger.cost_usd).label("total_cost")
    ).group_by(UsageLedger.tenant_id)
    
    res = await db.execute(stmt)
    rows = res.all()
    return [
        {
            "tenant_id": row[0],
            "total_cost_usd": float(row[1]) if row[1] is not None else 0.0
        }
        for row in rows
    ]
