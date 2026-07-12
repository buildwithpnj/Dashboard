from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.api.deps import (
    get_db,
    get_review_queue_repository,
    get_prompt_versions_repository,
    get_review_service
)
from app.db.models import ReviewQueue, PromptVersion
from app.repositories.review_queue import ReviewQueueRepository
from app.repositories.prompt_versions import PromptVersionsRepository
from app.services.review_service import ReviewService
from app.security.auth import get_current_user, UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter(prefix="/admin", tags=["Operations Admin"])
admin_only = Depends(RoleChecker(allowed_roles=["admin"]))

@router.get("/review-queue", summary="List pending human-in-the-loop review items", dependencies=[admin_only])
async def list_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Loads all pending validation runs filtered by caller's tenant."""
    repo = ReviewQueueRepository(db)
    items = await repo.get_pending_by_tenant(tenant_id=current_user.tenant_id)
    return [
        {
            "id": i.id,
            "request_id": i.request_id,
            "trace_id": i.trace_id,
            "product_id": i.product_id,
            "input_text": i.input_text,
            "original_response": i.original_response,
            "status": i.status,
            "created_at": i.created_at
        }
        for i in items
    ]

@router.post("/review/{id}/resolve", summary="Resolve a pending review queue item", dependencies=[admin_only])
async def resolve_review_item(
    id: str,
    payload: dict,
    current_user: UserPrincipal = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db)
):
    """Applies reviewer updates and marks a queue item resolved."""
    notes = payload.get("notes", "Resolved by admin.")
    status_code = payload.get("status", "APPROVED")
    edited_text = payload.get("edited_response")
    
    resolved_item = await service.resolve_item(
        item_id=id,
        status=status_code,
        edited_response=edited_text,
        notes=notes,
        assigned_to=current_user.user_id
    )
    if not resolved_item:
        raise HTTPException(status_code=404, detail="Review item not found")
        
    # Trigger learning loop feedback promotions
    from app.repositories.feedback_examples import FeedbackExamplesRepository
    from app.services.learning_loop import LearningLoopService
    
    fb_repo = FeedbackExamplesRepository(db)
    loop_service = LearningLoopService(fb_repo)
    
    is_pos = (status_code == "APPROVED")
    out_text = edited_text or resolved_item.original_response
    await loop_service.register_feedback(
        tenant_id=resolved_item.tenant_id,
        product_id=resolved_item.product_id,
        input_text=resolved_item.input_text,
        output_text=out_text,
        is_positive=is_pos
    )

    return {"status": "success", "item": {"id": resolved_item.id, "status": resolved_item.status}}

@router.get("/prompt-versions", summary="List prompt templates configurations", dependencies=[admin_only])
async def list_prompts(db: AsyncSession = Depends(get_db)):
    """Loads all prompt templates variations registered in registry."""
    stmt = select(PromptVersion).order_by(PromptVersion.product_id, PromptVersion.version.desc())
    res = await db.execute(stmt)
    prompts = res.scalars().all()
    return [
        {
            "id": p.id,
            "product_id": p.product_id,
            "task_id": p.task_id,
            "version": p.version,
            "prompt_template": p.prompt_template,
            "is_active": p.is_active
        }
        for p in prompts
    ]

@router.post("/prompt-activate", summary="Safely activate a prompt version", dependencies=[admin_only])
async def activate_prompt(payload: dict, db: AsyncSession = Depends(get_db)):
    """Sets a target prompt version active and deactivates other versions for the same task."""
    version_id = payload.get("version_id")
    if not version_id:
        raise HTTPException(status_code=400, detail="Missing version_id parameter")

    repo = PromptVersionsRepository(db)
    target = await repo.get_by_id(version_id)
    if not target:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    # Deactivate others for same product and task
    stmt_deactivate = (
        update(PromptVersion)
        .where(
            PromptVersion.product_id == target.product_id,
            PromptVersion.task_id == target.task_id,
            PromptVersion.id != version_id
        )
        .values(is_active=False)
    )
    await db.execute(stmt_deactivate)

    target.is_active = True
    await db.commit()

    return {"status": "success", "activated_version": target.version}
