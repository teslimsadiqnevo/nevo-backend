"""Teacher endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError
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

router = APIRouter()


@router.get("/dashboard", response_model=TeacherDashboardResponse)
async def get_teacher_dashboard(
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get teacher dashboard with overview statistics.
    """
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
            active_students_today=0,  # TODO: Implement activity tracking
            average_class_score=progress_stats.get("average_score", 0),
            students_needing_attention=0,  # TODO: Implement attention flagging
            lesson_engagement_rate=0.0,  # TODO: Calculate engagement
        )


@router.get("/students", response_model=StudentListResponse)
async def list_students(
    page: int = 1,
    page_size: int = 20,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    List students assigned to the teacher.
    """
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
