"""School admin registration command."""

from datetime import datetime

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos.school_admin_signup_dtos import (
    SchoolAdminSignUpInput,
    SchoolAdminSignUpOutput,
)
from src.core.config.constants import UserRole
from src.core.exceptions import ConflictError
from src.core.security import create_access_token, create_refresh_token, hash_password
from src.domain.entities.school import School
from src.domain.entities.user import User


class RegisterSchoolAdminCommand:
    """Register a new school admin with automatic school creation."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: SchoolAdminSignUpInput) -> SchoolAdminSignUpOutput:
        async with self.uow:
            # 1. Check email uniqueness
            if await self.uow.users.exists_by_email(input_dto.email):
                raise ConflictError("A user with this email already exists")

            # 2. Create new school workspace
            school = School(
                name=input_dto.school_name,
                address=input_dto.school_address,
                city=input_dto.school_city,
                state=input_dto.school_state,
            )
            school = await self.uow.schools.create(school)

            # 3. Split full name
            parts = input_dto.full_name.strip().split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            # 4. Create school admin user
            user = User(
                email=input_dto.email,
                password_hash=hash_password(input_dto.password),
                role=UserRole.SCHOOL_ADMIN,
                first_name=first_name,
                last_name=last_name,
                school_id=school.id,
            )
            user = await self.uow.users.create(user)

            await self.uow.commit()

            # 5. Create JWT tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "school_id": str(school.id),
            }
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": str(user.id)})

            return SchoolAdminSignUpOutput(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                name=user.full_name,
                school_id=school.id,
                school_name=school.name,
            )
