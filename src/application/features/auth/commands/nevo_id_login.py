"""Nevo ID login command use case."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import NevoIdLoginInput, LoginOutput
from src.core.exceptions import AuthenticationError
from src.core.security import create_access_token, create_refresh_token, verify_password


class NevoIdLoginCommand(UseCase[NevoIdLoginInput, LoginOutput]):
    """Use case for student login via Nevo ID + PIN."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: NevoIdLoginInput) -> LoginOutput:
        """Execute Nevo ID login and return tokens."""
        async with self.uow:
            # Normalize Nevo ID to uppercase
            nevo_id = input_dto.nevo_id.upper().strip()

            # Find user by Nevo ID
            user = await self.uow.users.get_by_nevo_id(nevo_id)

            if not user:
                raise AuthenticationError("Invalid Nevo ID or PIN")

            # Verify PIN
            if not user.pin_hash:
                raise AuthenticationError("PIN not set. Please set your PIN first.")

            if not verify_password(input_dto.pin, user.pin_hash):
                raise AuthenticationError("Invalid Nevo ID or PIN")

            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("Account is disabled")

            # Update last login
            user.update_last_login()
            await self.uow.users.update(user)
            await self.uow.commit()

            # Create tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }

            if user.school_id:
                token_data["school_id"] = str(user.school_id)

            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": str(user.id)})

            return LoginOutput(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                role=user.role,
                name=user.full_name,
                school_id=user.school_id,
            )
