"""Send teacher feedback command."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.dtos import SendFeedbackInput, SendFeedbackOutput
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.domain.entities.teacher_feedback import TeacherFeedback


class SendFeedbackCommand(UseCase[SendFeedbackInput, SendFeedbackOutput]):
    """Use case for a teacher sending encouragement feedback to a student."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: SendFeedbackInput) -> SendFeedbackOutput:
        """Send feedback from teacher to student."""
        async with self.uow:
            # Verify teacher exists and is a teacher
            teacher = await self.uow.users.get_by_id(input_dto.teacher_id)
            if not teacher:
                raise EntityNotFoundError("User", input_dto.teacher_id)
            if not teacher.is_teacher:
                raise ValidationError(
                    message="Only teachers can send feedback",
                    field="teacher_id",
                )

            # Verify student exists and is a student
            student = await self.uow.users.get_by_id(input_dto.student_id)
            if not student:
                raise EntityNotFoundError("User", input_dto.student_id)
            if not student.is_student:
                raise ValidationError(
                    message="Feedback can only be sent to students",
                    field="student_id",
                )

            # Create feedback
            feedback = TeacherFeedback(
                teacher_id=input_dto.teacher_id,
                student_id=input_dto.student_id,
                message=input_dto.message,
                lesson_id=input_dto.lesson_id,
            )

            created = await self.uow.teacher_feedbacks.create(feedback)
            await self.uow.commit()

            return SendFeedbackOutput(
                feedback_id=created.id,
                message="Feedback sent successfully",
            )
