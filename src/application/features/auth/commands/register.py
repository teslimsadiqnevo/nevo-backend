"""Register command use case."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import RegisterInput, RegisterOutput
from src.core.config.constants import UserRole
from src.core.exceptions import ConflictError, ValidationError
from src.core.security import hash_password
from src.domain.entities.user import User


class RegisterCommand(UseCase[RegisterInput, RegisterOutput]):
    """Use case for user registration."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: RegisterInput) -> RegisterOutput:
        """Execute registration and create user."""
        async with self.uow:
            # Check if email already exists
            if await self.uow.users.exists_by_email(input_dto.email):
                raise ConflictError(
                    message="Email already registered",
                    field="email",
                )

            # Validate school_id requirement for certain roles
            if input_dto.role in [UserRole.TEACHER, UserRole.STUDENT, UserRole.SCHOOL_ADMIN]:
                if not input_dto.school_id:
                    raise ValidationError(
                        message="School ID is required for this role",
                        field="school_id",
                    )

                # Verify school exists
                school = await self.uow.schools.get_by_id(input_dto.school_id)
                if not school:
                    raise ValidationError(
                        message="School not found",
                        field="school_id",
                    )

                # Check school capacity
                if input_dto.role == UserRole.TEACHER and not school.can_add_teacher():
                    raise ValidationError(
                        message="School has reached maximum teacher capacity",
                        field="school_id",
                    )

                if input_dto.role == UserRole.STUDENT and not school.can_add_student():
                    raise ValidationError(
                        message="School has reached maximum student capacity",
                        field="school_id",
                    )

            # Create user entity
            user = User(
                email=input_dto.email,
                password_hash=hash_password(input_dto.password),
                first_name=input_dto.first_name,
                last_name=input_dto.last_name,
                age=input_dto.age,
                role=input_dto.role,
                school_id=input_dto.school_id,
                phone_number=input_dto.phone_number,
            )

            # Save user
            created_user = await self.uow.users.create(user)

            # Update school counts if applicable
            if input_dto.school_id and school:
                if input_dto.role == UserRole.TEACHER:
                    school.increment_teacher_count()
                elif input_dto.role == UserRole.STUDENT:
                    school.increment_student_count()
                await self.uow.schools.update(school)

            await self.uow.commit()

            return RegisterOutput(
                user_id=created_user.id,
                email=created_user.email,
                role=created_user.role,
            )
