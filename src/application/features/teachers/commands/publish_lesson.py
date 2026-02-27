"""Publish lesson command."""

from dataclasses import dataclass
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.core.config.constants import LessonStatus
from src.core.exceptions import AuthorizationError, EntityNotFoundError, ValidationError


@dataclass
class PublishLessonOutput:
    """Output DTO for publishing a lesson."""

    lesson_id: UUID
    status: str
    message: str


class PublishLessonCommand:
    """Command to publish a draft lesson."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, lesson_id: UUID, teacher_id: UUID) -> PublishLessonOutput:
        async with self.uow:
            lesson = await self.uow.lessons.get_by_id(lesson_id)
            if not lesson:
                raise EntityNotFoundError("Lesson", str(lesson_id))

            if lesson.teacher_id != teacher_id:
                raise AuthorizationError("You can only publish your own lessons")

            if lesson.status == LessonStatus.PUBLISHED:
                raise ValidationError("Lesson is already published")

            if lesson.status == LessonStatus.ARCHIVED:
                raise ValidationError("Cannot publish an archived lesson")

            lesson.publish()
            await self.uow.lessons.update(lesson)
            await self.uow.commit()

            return PublishLessonOutput(
                lesson_id=lesson.id,
                status="published",
                message="Lesson published successfully",
            )
