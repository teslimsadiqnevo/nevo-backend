"""Progress tracking endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.progress.commands import UpdateProgressCommand
from src.application.features.progress.dtos import UpdateProgressInput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.progress import UpdateProgressRequest

router = APIRouter()


@router.post("/update")
async def update_progress(
    request: UpdateProgressRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Update student's lesson progress.

    Called periodically as student progresses through a lesson.
    """
    try:
        command = UpdateProgressCommand(uow)
        result = await command.execute(
            UpdateProgressInput(
                student_id=current_user.id,
                lesson_id=request.lesson_id,
                blocks_completed=request.blocks_completed,
                time_spent_seconds=request.time_spent_seconds,
                quiz_score=request.quiz_score,
                is_completed=request.is_completed,
            )
        )

        return result

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
