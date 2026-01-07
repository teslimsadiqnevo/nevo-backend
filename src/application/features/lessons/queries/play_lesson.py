"""Play lesson query - Core personalization endpoint."""

import time
from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.dtos import PlayLessonOutput
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.domain.entities.adapted_lesson import AdaptedLesson
from src.domain.interfaces.services import IAIService


class PlayLessonQuery:
    """
    Query to play a lesson with personalization.

    This is the CRITICAL endpoint that:
    1. Checks if adapted version exists for student+lesson
    2. If YES: returns cached version
    3. If NO: generates personalized version via AI
    """

    def __init__(self, uow: IUnitOfWork, ai_service: IAIService):
        self.uow = uow
        self.ai_service = ai_service

    async def execute(self, lesson_id: UUID, student_id: UUID) -> PlayLessonOutput:
        """Get or generate personalized lesson content."""
        async with self.uow:
            # Verify lesson exists
            lesson = await self.uow.lessons.get_by_id(lesson_id)
            if not lesson:
                raise EntityNotFoundError("Lesson", lesson_id)

            # Verify student exists and has a profile
            student = await self.uow.users.get_by_id(student_id)
            if not student:
                raise EntityNotFoundError("User", student_id)

            if not student.is_student:
                raise ValidationError(
                    message="Only students can play lessons",
                    field="student_id",
                )

            # Check for existing adapted lesson
            adapted = await self.uow.adapted_lessons.get_by_lesson_and_student(
                lesson_id=lesson_id,
                student_id=student_id,
            )

            if adapted and adapted.status.value == "ready":
                # Return cached version
                adapted.increment_view_count()
                await self.uow.adapted_lessons.update(adapted)
                await self.uow.commit()

                return PlayLessonOutput(
                    lesson_title=adapted.lesson_title,
                    adaptation_style=adapted.adaptation_style,
                    blocks=adapted.content_blocks_json,
                    adapted_lesson_id=adapted.id,
                    original_lesson_id=lesson_id,
                    student_id=student_id,
                )

            # Get student's neuro profile
            profile = await self.uow.neuro_profiles.get_by_user_id(student_id)
            if not profile:
                raise ValidationError(
                    message="Student must complete assessment before accessing lessons",
                    field="student_id",
                )

            # Generate adapted content
            start_time = time.time()

            adaptation_result = await self.ai_service.adapt_lesson(
                lesson=lesson,
                profile=profile,
            )

            generation_time_ms = int((time.time() - start_time) * 1000)

            # Create or update adapted lesson
            if adapted:
                adapted.lesson_title = lesson.title
                adapted.adaptation_style = adaptation_result.get(
                    "adaptation_style", "Personalized"
                )
                adapted.set_content_blocks(adaptation_result.get("blocks", []))
                adapted.ai_model_used = "gemini-pro"
                adapted.generation_duration_ms = generation_time_ms
                adapted.mark_as_ready()
                await self.uow.adapted_lessons.update(adapted)
            else:
                adapted = AdaptedLesson(
                    lesson_id=lesson_id,
                    student_id=student_id,
                    lesson_title=lesson.title,
                    adaptation_style=adaptation_result.get(
                        "adaptation_style", "Personalized"
                    ),
                    ai_model_used="gemini-pro",
                    generation_duration_ms=generation_time_ms,
                )
                adapted.set_content_blocks(adaptation_result.get("blocks", []))
                adapted.mark_as_ready()
                adapted = await self.uow.adapted_lessons.create(adapted)

            # Update lesson stats
            lesson.increment_adaptation_count()
            await self.uow.lessons.update(lesson)

            await self.uow.commit()

            return PlayLessonOutput(
                lesson_title=adapted.lesson_title,
                adaptation_style=adapted.adaptation_style,
                blocks=adapted.content_blocks_json,
                adapted_lesson_id=adapted.id,
                original_lesson_id=lesson_id,
                student_id=student_id,
            )
