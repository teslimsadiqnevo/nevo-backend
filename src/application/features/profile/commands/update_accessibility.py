"""Update accessibility settings command."""

from datetime import datetime
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.profile.dtos import (
    ProfileSettingsOutput,
    UpdateAccessibilityInput,
)
from src.core.exceptions import EntityNotFoundError


class UpdateAccessibilityCommand:
    """Update a student's accessibility preferences."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: UpdateAccessibilityInput) -> ProfileSettingsOutput:
        async with self.uow:
            user = await self.uow.users.get_by_id(input_dto.user_id)
            if not user:
                raise EntityNotFoundError("User", input_dto.user_id)

            if input_dto.voice_guidance is not None:
                user.voice_guidance = input_dto.voice_guidance
            if input_dto.large_text is not None:
                user.large_text = input_dto.large_text
            if input_dto.extra_spacing is not None:
                user.extra_spacing = input_dto.extra_spacing

            user.updated_at = datetime.utcnow()
            await self.uow.users.update(user)
            await self.uow.commit()

            return ProfileSettingsOutput(
                student_name=user.full_name,
                role=user.role.value.lower(),
                nevo_id=user.nevo_id,
                has_pin=user.has_pin,
                voice_guidance=user.voice_guidance,
                large_text=user.large_text,
                extra_spacing=user.extra_spacing,
            )
