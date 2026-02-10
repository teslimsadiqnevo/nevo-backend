"""Set PIN command use case."""

import re

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.auth.dtos import SetPinInput, SetPinOutput
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.core.security import hash_password


class SetPinCommand(UseCase[SetPinInput, SetPinOutput]):
    """Use case for setting a student's 4-digit PIN."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: SetPinInput) -> SetPinOutput:
        """Set or update the student's PIN."""
        async with self.uow:
            # Validate PIN format: exactly 4 digits
            if not re.match(r"^\d{4}$", input_dto.pin):
                raise ValidationError(
                    message="PIN must be exactly 4 digits",
                    field="pin",
                )

            # Get user
            user = await self.uow.users.get_by_id(input_dto.user_id)
            if not user:
                raise EntityNotFoundError("User", input_dto.user_id)

            # Verify user is a student
            if not user.is_student:
                raise ValidationError(
                    message="Only students can set a PIN",
                    field="user_id",
                )

            # Verify user has a Nevo ID
            if not user.has_nevo_id:
                raise ValidationError(
                    message="Complete your assessment first to get a Nevo ID",
                    field="nevo_id",
                )

            # Hash and save PIN
            user.pin_hash = hash_password(input_dto.pin)
            await self.uow.users.update(user)
            await self.uow.commit()

            return SetPinOutput(
                success=True,
                message="PIN set successfully",
                nevo_id=user.nevo_id,
            )
