"""Get profile settings query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.profile.dtos import ProfileSettingsOutput
from src.core.exceptions import EntityNotFoundError


class GetProfileSettingsQuery:
    """Query to get a student's profile settings."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, student_id: UUID) -> ProfileSettingsOutput:
        """Fetch student's profile info and accessibility settings."""
        async with self.uow:
            user = await self.uow.users.get_by_id(student_id)
            if not user:
                raise EntityNotFoundError("User", student_id)

            return ProfileSettingsOutput(
                student_name=user.full_name,
                role=user.role.value.lower(),
                nevo_id=user.nevo_id,
                has_pin=user.has_pin,
                voice_guidance=user.voice_guidance,
                large_text=user.large_text,
                extra_spacing=user.extra_spacing,
            )
