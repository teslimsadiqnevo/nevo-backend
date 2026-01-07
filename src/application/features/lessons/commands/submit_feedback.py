"""Submit feedback command for RLHF training data."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.lessons.dtos import SubmitFeedbackInput
from src.core.exceptions import AuthorizationError, EntityNotFoundError
from src.domain.entities.training_data import TrainingDataLog


class SubmitFeedbackCommand(UseCase[SubmitFeedbackInput, dict]):
    """Use case for submitting teacher feedback on adapted lessons."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: SubmitFeedbackInput) -> dict:
        """Submit feedback and store for training."""
        async with self.uow:
            # Verify teacher exists and has permission
            teacher = await self.uow.users.get_by_id(input_dto.teacher_id)
            if not teacher:
                raise EntityNotFoundError("User", input_dto.teacher_id)

            if not teacher.is_teacher:
                raise AuthorizationError(
                    message="Only teachers can submit feedback",
                    required_role="teacher",
                )

            # Get the adapted lesson
            adapted_lesson = await self.uow.adapted_lessons.get_by_id(
                input_dto.adapted_lesson_id
            )
            if not adapted_lesson:
                raise EntityNotFoundError("AdaptedLesson", input_dto.adapted_lesson_id)

            # Find the block that was corrected
            block_data = None
            for block in adapted_lesson.content_blocks_json:
                if str(block.get("id")) == input_dto.block_id:
                    block_data = block
                    break

            if not block_data:
                raise EntityNotFoundError("ContentBlock", input_dto.block_id)

            # Create training data log
            training_log = TrainingDataLog(
                source_id=adapted_lesson.id,
                source_type="adapted_lesson",
                model_name=adapted_lesson.ai_model_used or "unknown",
                input_context={
                    "block_id": input_dto.block_id,
                    "block_type": block_data.get("type"),
                    "original_content": block_data.get("content"),
                },
                model_output=block_data,
            )

            # Add the correction
            training_log.add_correction(
                correction={"content": input_dto.correction},
                user_id=input_dto.teacher_id,
                correction_type=input_dto.correction_type,
                notes=input_dto.notes,
            )

            await self.uow.training_data.create(training_log)
            await self.uow.commit()

            return {
                "status": "feedback_recorded",
                "message": "Feedback recorded for AI training",
                "training_log_id": str(training_log.id),
            }
