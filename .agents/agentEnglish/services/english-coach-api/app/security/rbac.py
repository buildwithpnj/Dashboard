from typing import List
from fastapi import Depends, HTTPException, status
from app.security.auth import UserPrincipal, get_current_user

class RoleChecker:
    """Dependency validator checking if authenticated user roles are authorized."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserPrincipal = Depends(get_current_user)) -> UserPrincipal:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this resource"
            )
        return user
