import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_family_checkin_service
from app.db.models import FamilyProfile, CheckinRun
from app.repositories.family_profiles import FamilyProfilesRepository
from app.repositories.checkins import CheckinRunsRepository
from app.security.auth import get_current_user, UserPrincipal
from app.security.rbac import RoleChecker
from app.products.family_checkin.schemas import FamilyCheckinRequest, FamilyCheckinResponse
from app.products.family_checkin.service import FamilyCheckinService

router = APIRouter(prefix="/admin/family-console", tags=["Family Console"])

# Enforce admin role for all console dashboard operations
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get("/profiles", summary="List all family profiles scoped by tenant")
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user),
    _rbac=admin_only
):
    """Retrieves all elderly profiles registered under the active tenant."""
    repo = FamilyProfilesRepository(db)
    profiles = await repo.get_all_by_tenant(tenant_id=current_user.tenant_id)
    return [
        {
            "id": p.id,
            "parent_name": p.parent_name,
            "tenant_id": p.tenant_id,
            "preferred_language": p.preferred_language,
            "escalation_contacts": p.escalation_contacts_json,
            "script_stage": p.script_stage
        }
        for p in profiles
    ]

@router.post("/profiles", summary="Create or update family profile configuration")
async def save_profile(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user),
    _rbac=admin_only
):
    """Creates a new or overrides an existing wellness check configuration."""
    repo = FamilyProfilesRepository(db)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id parameter")

    profile_db_id = f"{current_user.tenant_id}_{user_id}"
    
    # Check if exists
    profile = await repo.get_by_id_and_tenant(profile_db_id, tenant_id=current_user.tenant_id)
    
    if not profile:
        profile = FamilyProfile(
            id=profile_db_id,
            parent_name=payload.get("parent_name", "Mom"),
            tenant_id=current_user.tenant_id,
            preferred_language=payload.get("preferred_language", "Hindi"),
            escalation_contacts_json=payload.get("escalation_contacts_json", "[]"),
            script_stage="start"
        )
        await repo.create(profile)
    else:
        profile.parent_name = payload.get("parent_name", profile.parent_name)
        profile.preferred_language = payload.get("preferred_language", profile.preferred_language)
        profile.escalation_contacts_json = payload.get("escalation_contacts_json", profile.escalation_contacts_json)
        await db.commit()

    return {"status": "success", "profile_id": profile.id}

@router.post("/checkin", response_model=FamilyCheckinResponse, summary="Trigger wellness checkin message evaluation")
async def trigger_checkin(
    request: FamilyCheckinRequest,
    current_user: UserPrincipal = Depends(get_current_user),
    service: FamilyCheckinService = Depends(get_family_checkin_service),
    _rbac=admin_only
):
    """Dispatches a wellness update to the coordinator pipelines."""
    return await service.process_request(request, tenant_id=current_user.tenant_id)

@router.get("/checkins", summary="List checkin runs history and escalation states")
async def list_checkin_runs(
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user),
    _rbac=admin_only
):
    """Lists history of checkin wellness assessments and safety flags."""
    repo = CheckinRunsRepository(db)
    runs = await repo.get_all_by_tenant(tenant_id=current_user.tenant_id)
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
