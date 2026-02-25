"""Reset password command."""

from datetime import datetime
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import ResetPasswordInput
from src.core.exceptions import AuthenticationError, ValidationError
from src.core.security.jwt import decode_token
from src.core.security.password import hash_password


class ResetPasswordCommand:
    """Reset a user's password using a valid reset token."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: ResetPasswordInput) -> None:
        # Decode and validate the reset token
        payload = decode_token(input_dto.reset_token)
        if not payload or payload.get("purpose") != "password_reset":
            raise AuthenticationError("Invalid or expired reset token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid reset token")

        async with self.uow:
            user = await self.uow.users.get_by_id(UUID(user_id))
            if not user:
                raise AuthenticationError("Invalid reset token")

            if len(input_dto.new_password) < 8:
                raise ValidationError(
                    message="Password must be at least 8 characters",
                    field="new_password",
                )

            user.password_hash = hash_password(input_dto.new_password)
            user.updated_at = datetime.utcnow()
            await self.uow.users.update(user)
            await self.uow.commit()
