from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import DB, CurrentUser
from app.services.access_governance_service import AccessGovernanceService
from app.services.admin_controls_service import AdminControlsService
from app.services.persistence_hardening_service import PersistenceHardeningService
from typing import List

router = APIRouter(prefix="/api/governance", tags=["Launch Governance"])

class RequestAccessSchema(BaseModel):
    name: str
    email: str
    reason: str

class ConfigUpdateSchema(BaseModel):
    key: str
    value: str

@router.post("/request-access")
async def apply_access(req: RequestAccessSchema, db: DB):
    new_req = await AccessGovernanceService.create_request(
        db, name=req.name, email=req.email, reason=req.reason
    )
    return {"status": "success", "id": new_req.id}

@router.post("/approve/{request_id}")
async def approve_access(request_id: str, current_user: CurrentUser, db: DB):
    # Enforce role gating: internal_admin only
    if current_user.role != "internal_admin":
        raise HTTPException(status_code=403, detail="Admin permissions required.")
        
    ok = await AccessGovernanceService.approve_request(db, request_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Request not found.")
    return {"status": "approved"}

@router.post("/config")
async def update_config(req: ConfigUpdateSchema, current_user: CurrentUser, db: DB):
    if current_user.role != "internal_admin":
        raise HTTPException(status_code=403, detail="Admin permissions required.")
        
    await AdminControlsService.set_config(db, admin_id=current_user.id, key=req.key, value=req.value)
    return {"status": "updated"}

@router.post("/cleanup")
async def run_session_cleanup(current_user: CurrentUser, db: DB):
    if current_user.role != "internal_admin":
        raise HTTPException(status_code=403, detail="Admin permissions required.")
        
    count = await PersistenceHardeningService.cleanup_expired_sessions(db)
    return {"status": "success", "cleaned_count": count}

@router.get("/reports")
async def get_reports(current_user: CurrentUser, db: DB):
    if current_user.role != "internal_admin":
        raise HTTPException(status_code=403, detail="Admin permissions required.")
        
    from sqlalchemy import select
    from app.models.governance import AccessRequest, PreviewSession
    
    # 1. Access Request Funnel
    all_reqs_res = await db.execute(select(AccessRequest))
    all_reqs = all_reqs_res.scalars().all()
    total_reqs = len(all_reqs)
    pending_reqs = sum(1 for r in all_reqs if r.status == "pending")
    approved_reqs = sum(1 for r in all_reqs if r.status == "approved")
    rejected_reqs = sum(1 for r in all_reqs if r.status == "rejected")
    
    # 2. Quota & Session Stats
    sessions_res = await db.execute(select(PreviewSession))
    sessions = sessions_res.scalars().all()
    total_sessions = len(sessions)
    total_turns = sum(s.turns for s in sessions)
    total_tokens = sum(s.tokens for s in sessions)
    total_cost = sum(s.cost for s in sessions)
    
    # 3. Audit Logs
    audit_logs = await AdminControlsService.list_audit_logs(db)
    serialized_audits = [
        {
            "id": log.id,
            "admin_id": log.admin_id,
            "action": log.action,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in audit_logs
    ]
    
    return {
        "access_funnel": {
            "total_requests": total_reqs,
            "pending": pending_reqs,
            "approved": approved_reqs,
            "rejected": rejected_reqs
        },
        "preview_usage": {
            "total_sessions": total_sessions,
            "total_turns": total_turns,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4)
        },
        "audit_logs": serialized_audits
    }

