"""Refresh token command use case."""

from uuid import UUID

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import RefreshTokenInput, RefreshTokenOutput
from src.core.exceptions import AuthenticationError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token_type,
)


class RefreshTokenCommand(UseCase[RefreshTokenInput, RefreshTokenOutput]):
    """Use case for refreshing access tokens."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: RefreshTokenInput) -> RefreshTokenOutput:
        """Execute token refresh."""
        # Verify refresh token
        payload = verify_token_type(input_dto.refresh_token, "refresh")

        if not payload:
            raise AuthenticationError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        async with self.uow:
            # Verify user still exists and is active
            user = await self.uow.users.get_by_id(UUID(user_id))

            if not user:
                raise AuthenticationError("User not found")

            if not user.is_active:
                raise AuthenticationError("Account is disabled")

            # Create new tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }

            if user.school_id:
                token_data["school_id"] = str(user.school_id)

            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token({"sub": str(user.id)})

            return RefreshTokenOutput(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )
