"""Assessment endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.assessments.commands import SubmitAssessmentCommand
from src.application.features.assessments.queries import GetQuestionsQuery
from src.application.features.assessments.dtos import SubmitAssessmentInput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.domain.interfaces.services import IAIService
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    get_ai_service,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.assessment import (
    AssessmentQuestionsResponse,
    SubmitAssessmentRequest,
    SubmitAssessmentResponse,
)

router = APIRouter()


@router.get("/questions", response_model=AssessmentQuestionsResponse)
async def get_assessment_questions():
    """
    Get onboarding assessment questions.

    Returns structured questions for student assessment.
    """
    query = GetQuestionsQuery()
    result = await query.execute()

    return AssessmentQuestionsResponse(
        questions=[
            {
                "id": q.id,
                "text": q.text,
                "type": q.type,
                "category": q.category,
                "options": q.options,
                "scale_min": q.scale_min,
                "scale_max": q.scale_max,
                "is_required": q.is_required,
            }
            for q in result.questions
        ],
        total_questions=result.total_questions,
        categories=result.categories,
    )


@router.post("/submit", response_model=SubmitAssessmentResponse)
async def submit_assessment(
    request: SubmitAssessmentRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
    ai_service: IAIService = Depends(get_ai_service),
):
    """
    Submit assessment answers and generate student profile.

    - **answers**: List of question answers
    """
    try:
        command = SubmitAssessmentCommand(uow, ai_service)
        result = await command.execute(
            SubmitAssessmentInput(
                student_id=current_user.id,
                answers=request.answers,
            )
        )

        return SubmitAssessmentResponse(
            status=result.status,
            message=result.message,
            assessment_id=str(result.assessment_id) if result.assessment_id else None,
            profile_id=str(result.profile_id) if result.profile_id else None,
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
