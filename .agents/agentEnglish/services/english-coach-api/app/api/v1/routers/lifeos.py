from fastapi import APIRouter, Depends, HTTPException, status
from app.products.lifeos_coach.schemas import LifeOSRespondRequest, LifeOSRespondResponse
from app.products.lifeos_coach.service import LifeOSHealthCoachService
from app.api.deps import get_lifeos_coach_service
from app.security.auth import UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter()

@router.post(
    "/lifeos/respond",
    response_model=LifeOSRespondResponse,
    summary="Retrieve habits assessment and suggestions"
)
async def lifeos_respond(
    request: LifeOSRespondRequest,
    service: LifeOSHealthCoachService = Depends(get_lifeos_coach_service),
    current_user: UserPrincipal = Depends(RoleChecker(allowed_roles=["admin", "user"]))
) -> LifeOSRespondResponse:
    """Evaluates sleep, exercise, and diet parameters and provides habits recommendations."""
    try:
        return await service.process_request(request, tenant_id=current_user.tenant_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during lifestyle coaching: {str(e)}"
        )
