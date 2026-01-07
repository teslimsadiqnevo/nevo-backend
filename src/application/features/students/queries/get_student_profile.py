"""Get student profile query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.dtos import StudentProfileOutput
from src.core.exceptions import EntityNotFoundError


class GetStudentProfileQuery:
    """Query to get a student's neuro profile."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, student_id: UUID) -> StudentProfileOutput:
        """Get student's neuro profile."""
        async with self.uow:
            # Get student
            student = await self.uow.users.get_by_id(student_id)
            if not student:
                raise EntityNotFoundError("User", student_id)

            # Get profile
            profile = await self.uow.neuro_profiles.get_by_user_id(student_id)
            if not profile:
                raise EntityNotFoundError("NeuroProfile", student_id)

            return StudentProfileOutput(
                student_id=student_id,
                student_name=student.full_name,
                learning_style=profile.learning_style.value,
                reading_level=profile.reading_level.value,
                complexity_tolerance=profile.complexity_tolerance.value,
                attention_span_minutes=profile.attention_span_minutes,
                sensory_triggers=[t.value for t in profile.sensory_triggers],
                interests=profile.interests,
                profile_version=profile.version,
                last_updated=profile.last_updated,
            )
