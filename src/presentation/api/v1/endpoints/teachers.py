"""Teacher endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.commands import SendFeedbackCommand
from src.application.features.students.dtos import SendFeedbackInput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.domain.value_objects.pagination import PaginationParams
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.teacher import (
    TeacherDashboardResponse,
    StudentListResponse,
)
from src.presentation.schemas.student import (
    SendFeedbackRequest,
    SendFeedbackResponse,
)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=TeacherDashboardResponse,
    summary="Get teacher dashboard",
    description="""
Get an overview of the teacher's classroom statistics.

**Requires:** Teacher role.

**Returns:**
- Total students and lessons count
- Average class score
- Active students today
- Students needing attention (low scores or inactivity)
- Lesson engagement rate
    """,
    responses={
        200: {"description": "Teacher dashboard with classroom statistics"},
        404: {"description": "Teacher not found"},
    },
)
async def get_teacher_dashboard(
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get teacher dashboard with overview statistics."""
    async with uow:
        # Get teacher info
        teacher = await uow.users.get_by_id(current_user.id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found",
            )

        # Get lessons count
        lessons_result = await uow.lessons.list_by_teacher(
            teacher_id=current_user.id,
            pagination=PaginationParams(page=1, page_size=1),
        )

        # Get students
        students_result = await uow.users.list_students_by_teacher(
            teacher_id=current_user.id,
            pagination=PaginationParams(page=1, page_size=1),
        )

        # Get aggregated progress
        progress_stats = await uow.progress.get_aggregated_by_teacher(current_user.id)

        return TeacherDashboardResponse(
            teacher_id=str(current_user.id),
            teacher_name=teacher.full_name,
            total_students=students_result.total,
            total_lessons=lessons_result.total,
            active_students_today=0,
            average_class_score=progress_stats.get("average_score", 0),
            students_needing_attention=0,
            lesson_engagement_rate=0.0,
        )


@router.get(
    "/students",
    response_model=StudentListResponse,
    summary="List teacher's students",
    description="""
List all students assigned to this teacher with their progress summaries.

**Requires:** Teacher role.

**Returns per student:**
- Basic info (name, email)
- Whether they've completed their NeuroProfile assessment
- Lessons completed count
- Average score
- Last activity timestamp

**Pagination:** Use `page` and `page_size` query parameters.
    """,
    responses={
        200: {"description": "Paginated list of students with progress summaries"},
    },
)
async def list_students(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """List students assigned to the teacher."""
    async with uow:
        result = await uow.users.list_students_by_teacher(
            teacher_id=current_user.id,
            pagination=PaginationParams(page=page, page_size=page_size),
        )

        students = []
        for student in result.items:
            # Get profile status
            profile = await uow.neuro_profiles.get_by_user_id(student.id)

            # Get progress
            progress = await uow.progress.get_by_student_id(student.id)

            students.append({
                "id": str(student.id),
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "has_profile": profile is not None,
                "lessons_completed": progress.total_lessons_completed if progress else 0,
                "average_score": progress.average_score if progress else 0,
                "last_activity_at": progress.last_activity_at.isoformat() if progress and progress.last_activity_at else None,
            })

        return StudentListResponse(
            students=students,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )


@router.post(
    "/feedback",
    response_model=SendFeedbackResponse,
    summary="Send feedback to a student",
    description="""
Send an encouragement message to a student.

**Requires:** Teacher role.

**Use cases:**
- Sending motivational messages after lesson completion
- Providing encouragement for struggling students
- Celebrating milestones

Messages appear on the student's Home dashboard.
    """,
    responses={
        200: {"description": "Feedback sent successfully"},
        400: {"description": "Invalid request (not a teacher or invalid student)"},
        404: {"description": "Student not found"},
    },
)
async def send_feedback(
    request: SendFeedbackRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Send encouragement feedback to a student."""
    try:
        command = SendFeedbackCommand(uow)
        result = await command.execute(
            SendFeedbackInput(
                teacher_id=current_user.id,
                student_id=UUID(request.student_id),
                message=request.message,
                lesson_id=UUID(request.lesson_id) if request.lesson_id else None,
            )
        )

        return SendFeedbackResponse(
            feedback_id=str(result.feedback_id),
            message=result.message,
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
