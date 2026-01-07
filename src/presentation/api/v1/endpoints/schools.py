"""School endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.schools.commands import CreateSchoolCommand
from src.application.features.schools.dtos import CreateSchoolInput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError
from src.domain.value_objects.pagination import PaginationParams
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.school import (
    CreateSchoolRequest,
    SchoolResponse,
    SchoolDashboardResponse,
    TeacherListResponse,
)

router = APIRouter()


@router.post("", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    request: CreateSchoolRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Create a new school.

    Note: In production, this should require admin authentication.
    """
    command = CreateSchoolCommand(uow)
    result = await command.execute(
        CreateSchoolInput(
            name=request.name,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            phone_number=request.phone_number,
            email=request.email,
        )
    )

    return SchoolResponse(
        id=str(result.id),
        name=result.name,
        address=result.address,
        city=result.city,
        state=result.state,
        country=result.country,
        is_active=result.is_active,
        teacher_count=result.teacher_count,
        student_count=result.student_count,
        created_at=result.created_at.isoformat(),
    )


@router.get("/dashboard", response_model=SchoolDashboardResponse)
async def get_school_dashboard(
    current_user: CurrentUser = Depends(require_role([UserRole.SCHOOL_ADMIN])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get school admin dashboard with overview statistics.
    """
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with a school",
        )

    async with uow:
        # Get school info
        school = await uow.schools.get_by_id(current_user.school_id)
        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found",
            )

        # Get lessons count
        lessons_result = await uow.lessons.list_by_school(
            school_id=current_user.school_id,
            pagination=PaginationParams(page=1, page_size=1),
        )

        # Get progress stats
        progress_stats = await uow.progress.get_aggregated_by_school(current_user.school_id)

        return SchoolDashboardResponse(
            school_id=str(school.id),
            school_name=school.name,
            total_teachers=school.teacher_count,
            total_students=school.student_count,
            total_lessons=lessons_result.total,
            active_students_today=0,  # TODO: Implement
            average_school_score=progress_stats.get("average_score", 0),
            students_completed_assessment=0,  # TODO: Implement
            lessons_delivered_today=0,  # TODO: Implement
        )


@router.get("/teachers", response_model=TeacherListResponse)
async def list_teachers(
    page: int = 1,
    page_size: int = 20,
    current_user: CurrentUser = Depends(require_role([UserRole.SCHOOL_ADMIN])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    List teachers in the school.
    """
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with a school",
        )

    async with uow:
        result = await uow.users.list_by_school(
            school_id=current_user.school_id,
            role=UserRole.TEACHER,
            pagination=PaginationParams(page=page, page_size=page_size),
        )

        teachers = []
        for teacher in result.items:
            # Get lesson count
            lessons = await uow.lessons.list_by_teacher(
                teacher_id=teacher.id,
                pagination=PaginationParams(page=1, page_size=1),
            )

            teachers.append({
                "id": str(teacher.id),
                "email": teacher.email,
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
                "lesson_count": lessons.total,
                "created_at": teacher.created_at.isoformat(),
            })

        return TeacherListResponse(
            teachers=teachers,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )


@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get school details.
    """
    async with uow:
        school = await uow.schools.get_by_id(school_id)
        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found",
            )

        return SchoolResponse(
            id=str(school.id),
            name=school.name,
            address=school.address,
            city=school.city,
            state=school.state,
            country=school.country,
            is_active=school.is_active,
            teacher_count=school.teacher_count,
            student_count=school.student_count,
            created_at=school.created_at.isoformat(),
        )
