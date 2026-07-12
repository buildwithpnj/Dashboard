from fastapi import APIRouter, Depends, HTTPException, status
from app.products.family_checkin.schemas import FamilyCheckinRequest, FamilyCheckinResponse
from app.products.family_checkin.service import FamilyCheckinService
from app.api.deps import get_family_checkin_service
from app.security.auth import UserPrincipal
from app.security.rbac import RoleChecker

router = APIRouter()

@router.post(
    "/family/checkin",
    response_model=FamilyCheckinResponse,
    summary="Evaluate parent wellness check-in updates"
)
async def family_checkin(
    request: FamilyCheckinRequest,
    service: FamilyCheckinService = Depends(get_family_checkin_service),
    current_user: UserPrincipal = Depends(RoleChecker(allowed_roles=["admin", "user"]))
) -> FamilyCheckinResponse:
    """Evaluates parent health metrics and runs escalation workflows for user safety."""
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
            detail=f"An error occurred while evaluating parent check-ins: {str(e)}"
        )
