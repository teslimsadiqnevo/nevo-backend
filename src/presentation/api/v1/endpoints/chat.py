"""Chat endpoints - Ask Nevo AI tutor."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.chat.commands import AskNevoCommand
from src.application.features.chat.dtos import AskNevoInput
from src.core.config.constants import UserRole
from src.core.exceptions import AIServiceError, EntityNotFoundError, ValidationError
from src.domain.interfaces.services import IAIService
from src.presentation.api.v1.dependencies import (
    get_ai_service,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.chat import (
    AskNevoRequest,
    AskNevoResponse,
    ChatHistoryResponse,
)

router = APIRouter()


@router.post(
    "/ask",
    response_model=AskNevoResponse,
    summary="Ask Nevo a question",
    description="""
Ask the Nevo AI tutor a question and get a personalized response.

**Requires:** Student role with completed NeuroProfile.

**How it works:**
1. Student sends a question (optionally with current lesson context)
2. Nevo uses the student's NeuroProfile to tailor the response
3. Both the question and response are saved to chat history
4. Response adapts to the student's learning style and reading level

**Tips:**
- Include `lesson_id` for lesson-specific help
- Nevo remembers recent conversation context
    """,
    responses={
        200: {"description": "Nevo's personalized response"},
        404: {"description": "Student or profile not found"},
        502: {"description": "AI service error"},
    },
)
async def ask_nevo(
    request: AskNevoRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
    ai_service: IAIService = Depends(get_ai_service),
):
    """Ask Nevo AI tutor a question."""
    try:
        from uuid import UUID

        command = AskNevoCommand(uow, ai_service)
        result = await command.execute(
            AskNevoInput(
                student_id=current_user.id,
                message=request.message,
                lesson_id=UUID(request.lesson_id) if request.lesson_id else None,
            )
        )

        return AskNevoResponse(
            response=result.response,
            message_id=str(result.message_id),
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message,
        )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="""
Get the student's recent chat history with Nevo.

**Requires:** Student role.

**Returns:** Messages in chronological order (oldest first).
Use the `limit` parameter to control how many messages to retrieve.
    """,
    responses={
        200: {"description": "Chat history"},
    },
)
async def get_chat_history(
    limit: int = Query(default=50, ge=1, le=100, description="Max messages to return"),
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get student's chat history with Nevo."""
    async with uow:
        messages = await uow.chat_messages.list_by_student(
            current_user.id, limit=limit
        )

        return ChatHistoryResponse(
            messages=[
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ]
        )
