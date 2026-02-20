"""Remove connection command."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import RemoveConnectionInput
from src.core.exceptions import EntityNotFoundError, ValidationError


class RemoveConnectionCommand(UseCase[RemoveConnectionInput, bool]):
    """Remove a student's connection."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: RemoveConnectionInput) -> bool:
        async with self.uow:
            connection = await self.uow.connections.get_by_id(input_dto.connection_id)
            if not connection:
                raise EntityNotFoundError("Connection", input_dto.connection_id)

            # Verify the student owns this connection
            if connection.student_id != input_dto.student_id:
                raise ValidationError("You can only remove your own connections")

            await self.uow.connections.delete(input_dto.connection_id)
            await self.uow.commit()
            return True
