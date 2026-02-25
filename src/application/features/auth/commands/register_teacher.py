"""Teacher registration command."""

from datetime import datetime

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos.teacher_signup_dtos import (
    TeacherSignUpInput,
    TeacherSignUpOutput,
)
from src.core.config.constants import UserRole
from src.core.exceptions import ConflictError, ValidationError
from src.core.security import create_access_token, create_refresh_token, hash_password
from src.core.security.class_code import generate_class_code
from src.domain.entities.school import School
from src.domain.entities.user import User


class RegisterTeacherCommand:
    """Register a new teacher with school creation/lookup and class code generation."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: TeacherSignUpInput) -> TeacherSignUpOutput:
        async with self.uow:
            # 1. Check email uniqueness
            if await self.uow.users.exists_by_email(input_dto.email):
                raise ConflictError("A user with this email already exists")

            # 2. Find or create school
            school = await self.uow.schools.get_by_name(input_dto.school_name)
            if not school:
                school = School(name=input_dto.school_name)
                school = await self.uow.schools.create(school)
            else:
                if not school.can_add_teacher():
                    raise ValidationError(
                        f"School '{school.name}' has reached its maximum teacher capacity"
                    )

            # 3. Split full name
            parts = input_dto.full_name.strip().split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            # 4. Generate unique class code
            class_code = None
            for _ in range(5):
                code = generate_class_code()
                if not await self.uow.users.exists_by_class_code(code):
                    class_code = code
                    break
            if not class_code:
                raise ValidationError("Could not generate unique class code, please try again")

            # 5. Create teacher user
            user = User(
                email=input_dto.email,
                password_hash=hash_password(input_dto.password),
                role=UserRole.TEACHER,
                first_name=first_name,
                last_name=last_name,
                school_id=school.id,
                class_code=class_code,
            )
            user = await self.uow.users.create(user)

            # 6. Increment school teacher count
            school.increment_teacher_count()
            school.updated_at = datetime.utcnow()
            await self.uow.schools.update(school)

            await self.uow.commit()

            # 7. Create JWT tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "school_id": str(school.id),
            }
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": str(user.id)})

            return TeacherSignUpOutput(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                name=user.full_name,
                school_id=school.id,
                school_name=school.name,
                class_code=class_code,
            )
