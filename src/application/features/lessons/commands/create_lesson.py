"""Create lesson command use case."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.dtos import CreateLessonInput, CreateLessonOutput
from src.core.exceptions import AuthorizationError, EntityNotFoundError
from src.domain.entities.lesson import Lesson


class CreateLessonCommand(UseCase[CreateLessonInput, CreateLessonOutput]):
    """Use case for creating a new lesson."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: CreateLessonInput) -> CreateLessonOutput:
        """Create a new lesson."""
        async with self.uow:
            # Verify teacher exists and has permission
            teacher = await self.uow.users.get_by_id(input_dto.teacher_id)
            if not teacher:
                raise EntityNotFoundError("User", input_dto.teacher_id)

            if not teacher.is_teacher:
                raise AuthorizationError(
                    message="Only teachers can create lessons",
                    required_role="teacher",
                )

            # Create lesson entity
            lesson = Lesson(
                title=input_dto.title,
                teacher_id=input_dto.teacher_id,
                school_id=teacher.school_id,
                description=input_dto.description,
                original_text_content=input_dto.original_text_content,
                subject=input_dto.subject,
                topic=input_dto.topic,
                target_grade_level=input_dto.target_grade_level,
                estimated_duration_minutes=input_dto.estimated_duration_minutes,
                tags=list(input_dto.tags) if input_dto.tags else [],
                media_url=input_dto.media_url,
                media_type=input_dto.media_type,
            )

            # Save lesson
            created_lesson = await self.uow.lessons.create(lesson)
            await self.uow.commit()

            return CreateLessonOutput(
                lesson_id=created_lesson.id,
                status="uploaded",
            )
