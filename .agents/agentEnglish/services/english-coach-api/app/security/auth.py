import logging
from typing import Optional, Dict, Any
from fastapi import Security, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# Authentication headers scheme declarations
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
security_bearer = HTTPBearer(auto_error=False)

class UserPrincipal:
    """Security model wrapping the active caller's identification and roles."""
    def __init__(self, user_id: str, tenant_id: str, role: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role

def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    token: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> UserPrincipal:
    """Validates the request authentication parameters, returning user details."""
    if not settings.AUTH_ENABLED:
        # Auth disabled: fallback to default mock admin principal to prevent breakages
        return UserPrincipal(
            user_id="default_user",
            tenant_id=settings.DEFAULT_TENANT_ID,
            role="admin"
        )

    # 1. Verify API Key
    if api_key:
        if api_key == settings.ADMIN_API_KEY:
            return UserPrincipal(
                user_id="admin_user",
                tenant_id=settings.DEFAULT_TENANT_ID,
                role="admin"
            )
        else:
            logger.warning("Invalid API Key supplied.")
            from app.observability.metrics import ObservabilityMetricsTracker
            ObservabilityMetricsTracker.record_auth_denied()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key"
            )

    # 2. Verify JWT Bearer Token
    if token:
        try:
            payload = jwt.decode(
                token.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = payload.get("sub", "unknown_user")
            tenant_id = payload.get("tenant_id", settings.DEFAULT_TENANT_ID)
            role = payload.get("role", "user")
            return UserPrincipal(user_id=user_id, tenant_id=tenant_id, role=role)
        except Exception as e:
            logger.error(f"JWT Token validation failed: {e}")
            from app.observability.metrics import ObservabilityMetricsTracker
            ObservabilityMetricsTracker.record_auth_denied()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token"
            )

    # 3. No authentication provided
    from app.observability.metrics import ObservabilityMetricsTracker
    ObservabilityMetricsTracker.record_auth_denied()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials are required"
    )
