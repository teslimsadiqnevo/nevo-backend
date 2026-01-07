"""Login command use case."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import LoginInput, LoginOutput
from src.core.exceptions import AuthenticationError
from src.core.security import create_access_token, create_refresh_token, verify_password


class LoginCommand(UseCase[LoginInput, LoginOutput]):
    """Use case for user login."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: LoginInput) -> LoginOutput:
        """Execute login and return tokens."""
        async with self.uow:
            # Find user by email
            user = await self.uow.users.get_by_email(input_dto.email)

            if not user:
                raise AuthenticationError("Invalid email or password")

            # Verify password
            if not verify_password(input_dto.password, user.password_hash):
                raise AuthenticationError("Invalid email or password")

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
