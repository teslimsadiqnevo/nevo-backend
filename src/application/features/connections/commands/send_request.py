"""Send connection request command."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import (
    SendConnectionRequestInput,
    SendConnectionRequestOutput,
)
from src.core.config.constants import ConnectionStatus, UserRole
from src.core.exceptions import EntityNotFoundError, ValidationError, ConflictError
from src.domain.entities.connection import Connection


class SendConnectionRequestCommand(
    UseCase[SendConnectionRequestInput, SendConnectionRequestOutput]
):
    """Send a connection request from a student to a teacher via class code."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(
        self, input_dto: SendConnectionRequestInput
    ) -> SendConnectionRequestOutput:
        async with self.uow:
            # Validate student exists
            student = await self.uow.users.get_by_id(input_dto.student_id)
            if not student:
                raise EntityNotFoundError("User", input_dto.student_id)
            if student.role != UserRole.STUDENT:
                raise ValidationError("Only students can send connection requests")

            # Find teacher by class code
            class_code = input_dto.class_code.upper().strip()
            teacher = await self.uow.users.get_by_class_code(class_code)
            if not teacher:
                raise EntityNotFoundError(
                    "Teacher", f"class_code={class_code}"
                )

            # Check for existing connection
            existing = await self.uow.connections.get_by_student_and_teacher(
                student_id=input_dto.student_id,
                teacher_id=teacher.id,
            )
            if existing:
                if existing.status == ConnectionStatus.ACCEPTED:
                    raise ConflictError("Already connected to this teacher")
                if existing.status == ConnectionStatus.PENDING:
                    raise ConflictError("Connection request already pending")
                # If rejected, allow re-request by updating status
                existing.status = ConnectionStatus.PENDING
                updated = await self.uow.connections.update(existing)
                await self.uow.commit()
                return SendConnectionRequestOutput(
                    connection_id=updated.id,
                    teacher_name=teacher.full_name,
                    status=updated.status.value,
                )

            # Create new connection
            connection = Connection(
                student_id=input_dto.student_id,
                teacher_id=teacher.id,
                status=ConnectionStatus.PENDING,
            )
            created = await self.uow.connections.create(connection)
            await self.uow.commit()

            return SendConnectionRequestOutput(
                connection_id=created.id,
                teacher_name=teacher.full_name,
                status=created.status.value,
            )

