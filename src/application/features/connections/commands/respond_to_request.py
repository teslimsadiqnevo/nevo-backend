"""Respond to connection request command."""

from datetime import datetime

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.connections.dtos import (
    RespondToRequestInput,
    RespondToRequestOutput,
)
from src.core.config.constants import ConnectionStatus
from src.core.exceptions import EntityNotFoundError, ValidationError


class RespondToConnectionRequestCommand(
    UseCase[RespondToRequestInput, RespondToRequestOutput]
):
    """Accept or reject a student's connection request."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(
        self, input_dto: RespondToRequestInput
    ) -> RespondToRequestOutput:
        async with self.uow:
            connection = await self.uow.connections.get_by_id(input_dto.connection_id)
            if not connection:
                raise EntityNotFoundError("Connection", input_dto.connection_id)

            # Verify the teacher owns this connection
            if connection.teacher_id != input_dto.teacher_id:
                raise ValidationError("You can only respond to your own connection requests")

            # Verify it's still pending
            if connection.status != ConnectionStatus.PENDING:
                raise ValidationError(
                    f"Connection is already {connection.status.value}"
                )

            # Apply action
            action = input_dto.action.lower().strip()
            if action == "accept":
                connection.status = ConnectionStatus.ACCEPTED
            elif action == "reject":
                connection.status = ConnectionStatus.REJECTED
            else:
                raise ValidationError("Action must be 'accept' or 'reject'")

            connection.updated_at = datetime.utcnow()
            updated = await self.uow.connections.update(connection)
            await self.uow.commit()

            return RespondToRequestOutput(
                connection_id=updated.id,
                status=updated.status.value,
            )
