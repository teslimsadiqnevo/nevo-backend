"""Get or generate class code command."""

from datetime import datetime
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import ClassCodeOutput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.core.security.class_code import generate_class_code


class GetOrGenerateClassCodeCommand:
    """Get a teacher's class code, generating one if it doesn't exist."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, teacher_id: UUID) -> ClassCodeOutput:
        async with self.uow:
            teacher = await self.uow.users.get_by_id(teacher_id)
            if not teacher:
                raise EntityNotFoundError("User", teacher_id)
            if teacher.role != UserRole.TEACHER:
                raise ValidationError("Only teachers can have class codes")

            if teacher.class_code:
                return ClassCodeOutput(class_code=teacher.class_code)

            # Generate a unique class code
            for _ in range(5):
                code = generate_class_code()
                if not await self.uow.users.exists_by_class_code(code):
                    teacher.class_code = code
                    teacher.updated_at = datetime.utcnow()
                    await self.uow.users.update(teacher)
                    await self.uow.commit()
                    return ClassCodeOutput(class_code=code)

            raise ValidationError("Could not generate unique class code, please try again")
