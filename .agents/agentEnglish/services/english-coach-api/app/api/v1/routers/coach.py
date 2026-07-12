from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.coach import (
    CoachRespondRequest,
    CoachRespondResponse,
    CoachFeedbackRequest,
    CoachFeedbackResponse
)
from app.services.coach_service import CoachService
from app.services.feedback_service import FeedbackService
from app.api.deps import (
    get_coach_service,
    get_feedback_service,
    get_budget_guard,
    get_usage_ledger_repository
)
from app.services.budget_guard import BudgetGuard
from app.repositories.usage_ledger import UsageLedgerRepository
from app.security.auth import UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter()

@router.post(
    "/respond",
    response_model=CoachRespondResponse,
    summary="Get language correction and translation coaching"
)
async def respond(
    request: CoachRespondRequest,
    service: CoachService = Depends(get_coach_service),
    current_user: UserPrincipal = Depends(RoleChecker(allowed_roles=["admin", "user"])),
    budget_guard: BudgetGuard = Depends(get_budget_guard),
    usage_repo: UsageLedgerRepository = Depends(get_usage_ledger_repository)
) -> CoachRespondResponse:
    """Evaluates Prakash's English, Hinglish, or Hindi text, providing corrections and tagging errors."""
    try:
        # 1. Budget enforcement check
        await budget_guard.validate_budget(current_user.tenant_id)
        
        # 2. Process query response
        res = await service.process_request(request, tenant_id=current_user.tenant_id)
        
        # 3. Log usage tokens and costs
        import uuid
        from app.db.models import UsageLedger
        ledger_entry = UsageLedger(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            product_id="english_coach",
            user_id=current_user.user_id,
            token_input=res.token_usage.input_tokens,
            token_output=res.token_usage.output_tokens,
            cost_usd=res.token_usage.estimated_cost_usd
        )
        await usage_repo.create(ledger_entry)
        await usage_repo.db.commit()

        # 4. Human validation check for low-confidence outputs (< 80%)
        from app.api.deps import get_review_queue_repository
        from app.services.handoff_service import HandoffService
        review_repo = await get_review_queue_repository(usage_repo.db)
        handoff = HandoffService(review_repo)
        
        original_text = (res.natural_english or "") + " " + (res.explanation or "")
        await handoff.check_and_queue(
            request_id=res.response_id,
            tenant_id=current_user.tenant_id,
            product_id="english_coach",
            input_text=request.text,
            original_response=original_text,
            confidence=res.confidence
        )
        await review_repo.db.commit()

        return res
    except ValueError as val_err:
        if "limit of" in str(val_err) or "cap exceeded" in str(val_err) or "spending limit" in str(val_err):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(val_err)
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while evaluating the input phrase: {str(e)}"
        )

@router.post(
    "/feedback",
    response_model=CoachFeedbackResponse,
    summary="Record approved corrections and feedback notes"
)
async def feedback(
    request: CoachFeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
    current_user: UserPrincipal = Depends(RoleChecker(allowed_roles=["admin", "user"]))
) -> CoachFeedbackResponse:
    """Logs user validation checks and corrections to train future practice sessions."""
    try:
        return await service.record_feedback(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while recording feedback metrics: {str(e)}"
        )
