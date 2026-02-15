"""Ask Nevo command - AI chat interaction."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.chat.dtos import AskNevoInput, AskNevoOutput
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.domain.entities.chat_message import ChatMessage
from src.domain.interfaces.services import IAIService


class AskNevoCommand(UseCase[AskNevoInput, AskNevoOutput]):
    """Use case for a student asking Nevo AI a question."""

    def __init__(self, uow: IUnitOfWork, ai_service: IAIService):
        self.uow = uow
        self.ai_service = ai_service

    async def execute(self, input_dto: AskNevoInput) -> AskNevoOutput:
        """Process student question and generate AI response."""
        async with self.uow:
            # Verify student exists
            student = await self.uow.users.get_by_id(input_dto.student_id)
            if not student:
                raise EntityNotFoundError("User", input_dto.student_id)
            if not student.is_student:
                raise ValidationError(
                    message="Only students can chat with Nevo",
                    field="student_id",
                )

            # Get student's neuro profile
            profile = await self.uow.neuro_profiles.get_by_user_id(
                input_dto.student_id
            )
            if not profile:
                raise EntityNotFoundError("NeuroProfile", input_dto.student_id)

            # Get recent chat history
            recent_messages = await self.uow.chat_messages.list_by_student(
                input_dto.student_id, limit=20
            )
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ]

            # Get lesson context if provided
            lesson_context = None
            if input_dto.lesson_id:
                lesson = await self.uow.lessons.get_by_id(input_dto.lesson_id)
                if lesson:
                    lesson_context = f"Title: {lesson.title}\n{lesson.original_text_content[:2000]}"

            # Save student's message
            student_msg = ChatMessage(
                student_id=input_dto.student_id,
                role="student",
                content=input_dto.message,
                lesson_id=input_dto.lesson_id,
            )
            await self.uow.chat_messages.create(student_msg)

            # Generate AI response
            response_text = await self.ai_service.generate_chat_response(
                question=input_dto.message,
                profile=profile,
                chat_history=chat_history,
                lesson_context=lesson_context,
            )

            # Save Nevo's response
            nevo_msg = ChatMessage(
                student_id=input_dto.student_id,
                role="nevo",
                content=response_text,
                lesson_id=input_dto.lesson_id,
            )
            saved_msg = await self.uow.chat_messages.create(nevo_msg)

            await self.uow.commit()

            return AskNevoOutput(
                response=response_text,
                message_id=saved_msg.id,
            )
