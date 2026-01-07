"""Authentication dependencies."""

from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config.constants import UserRole
from src.core.security import decode_token
from src.presentation.api.v1.dependencies.database import get_uow
from src.application.common.unit_of_work import IUnitOfWork

security = HTTPBearer()


class CurrentUser:
    """Current authenticated user."""

    def __init__(
        self,
        user_id: UUID,
        email: str,
        role: UserRole,
        school_id: Optional[UUID] = None,
    ):
        self.id = user_id
        self.email = email
        self.role = role
        self.school_id = school_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    school_id = payload.get("school_id")

    return CurrentUser(
        user_id=UUID(user_id),
        email=payload.get("email", ""),
        role=UserRole(payload.get("role", "student")),
        school_id=UUID(school_id) if school_id else None,
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
) -> CurrentUser:
    """Get current user and verify they are active."""
    async with uow:
        user = await uow.users.get_by_id(current_user.id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
            )
    return current_user


def require_role(allowed_roles: List[UserRole]):
    """Dependency factory to require specific roles."""

    async def role_checker(
        current_user: CurrentUser = Depends(get_current_active_user),
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
