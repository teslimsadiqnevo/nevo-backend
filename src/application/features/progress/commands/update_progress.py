"""Update progress command."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.progress.dtos import UpdateProgressInput
from src.core.exceptions import EntityNotFoundError
from src.domain.entities.progress import StudentProgress


class UpdateProgressCommand(UseCase[UpdateProgressInput, dict]):
    """Use case for updating student progress."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: UpdateProgressInput) -> dict:
        """Update student's lesson progress."""
        async with self.uow:
            # Get or create progress record
            progress = await self.uow.progress.get_by_student_id(input_dto.student_id)

            if not progress:
                progress = StudentProgress(student_id=input_dto.student_id)
                progress = await self.uow.progress.create(progress)

            # Get lesson for metadata
            lesson = await self.uow.lessons.get_by_id(input_dto.lesson_id)
            if not lesson:
                raise EntityNotFoundError("Lesson", input_dto.lesson_id)

            # Get adapted lesson for block count
            adapted = await self.uow.adapted_lessons.get_by_lesson_and_student(
                lesson_id=input_dto.lesson_id,
                student_id=input_dto.student_id,
            )

            total_blocks = len(adapted.content_blocks) if adapted else 1

            # Start lesson if not started
            lesson_progress = progress.get_lesson_progress(input_dto.lesson_id)
            if not lesson_progress:
                progress.start_lesson(input_dto.lesson_id, total_blocks)

            # Update progress
            progress.update_lesson_progress(
                lesson_id=input_dto.lesson_id,
                blocks_completed=input_dto.blocks_completed,
                time_spent_seconds=input_dto.time_spent_seconds,
            )

            # Complete if needed
            if input_dto.is_completed:
                progress.complete_lesson(
                    lesson_id=input_dto.lesson_id,
                    score=input_dto.quiz_score,
                    skill_name=lesson.subject,
                )

            await self.uow.progress.update(progress)
            await self.uow.commit()

            return {
                "status": "updated",
                "lesson_id": str(input_dto.lesson_id),
                "is_completed": input_dto.is_completed,
            }
