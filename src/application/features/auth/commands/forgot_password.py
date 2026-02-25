"""Forgot password command."""

import logging
from datetime import timedelta

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import ForgotPasswordInput
from src.core.security.jwt import create_access_token
from src.domain.interfaces.services import IEmailService

logger = logging.getLogger(__name__)


class ForgotPasswordCommand:
    """Send a password reset email with a JWT reset token."""

    def __init__(self, uow: IUnitOfWork, email_service: IEmailService):
        self.uow = uow
        self.email_service = email_service

    async def execute(self, input_dto: ForgotPasswordInput) -> None:
        async with self.uow:
            user = await self.uow.users.get_by_email(input_dto.email)

            if not user:
                # Return silently — don't reveal if email exists
                return

            # Create a short-lived JWT for password reset (1 hour)
            reset_token = create_access_token(
                data={"sub": str(user.id), "purpose": "password_reset"},
                expires_delta=timedelta(hours=1),
            )

            try:
                await self.email_service.send_password_reset_email(
                    to=user.email,
                    reset_token=reset_token,
                )
            except Exception:
                # Log but don't expose email service failures to the client
                logger.warning("Failed to send password reset email to %s", user.email)
