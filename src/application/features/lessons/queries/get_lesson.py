"""Get lesson query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.dtos import LessonOutput
from src.core.exceptions import EntityNotFoundError


class GetLessonQuery:
    """Query to get a single lesson."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, lesson_id: UUID) -> LessonOutput:
        """Get lesson by ID."""
        async with self.uow:
            lesson = await self.uow.lessons.get_by_id(lesson_id)

            if not lesson:
                raise EntityNotFoundError("Lesson", lesson_id)

            # Get teacher name
            teacher = await self.uow.users.get_by_id(lesson.teacher_id)
            teacher_name = teacher.full_name if teacher else None

            return LessonOutput(
                id=lesson.id,
                title=lesson.title,
                description=lesson.description,
                subject=lesson.subject,
                topic=lesson.topic,
                target_grade_level=lesson.target_grade_level,
                estimated_duration_minutes=lesson.estimated_duration_minutes,
                status=lesson.status.value,
                media_url=lesson.media_url,
                media_type=lesson.media_type,
                tags=lesson.tags,
                teacher_id=lesson.teacher_id,
                teacher_name=teacher_name,
                created_at=lesson.created_at,
                view_count=lesson.view_count,
                adaptation_count=lesson.adaptation_count,
            )
