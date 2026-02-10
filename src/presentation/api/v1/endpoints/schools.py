"""School endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

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


@router.post(
    "",
    response_model=SchoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new school",
    description="""
Register a new school on the Nevo platform.

**No authentication required** (for initial setup). In production,
this should be restricted to super admins.

**Required Fields:**
- `name` — School name
- `country` — Country

**Optional Fields:**
- `address`, `city`, `state` — Location details
- `phone_number`, `email` — Contact info

**After creating a school:**
1. Note the returned `id`
2. Register a school admin with `school_id` set to this value
3. Register teachers and students under the same school
    """,
    responses={
        201: {"description": "School created successfully"},
        400: {"description": "Validation error"},
    },
)
async def create_school(
    request: CreateSchoolRequest,
    uow: IUnitOfWork = Depends(get_uow),
):
    """Create a new school."""
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


@router.get(
    "/dashboard",
    response_model=SchoolDashboardResponse,
    summary="Get school admin dashboard",
    description="""
Get an overview of school-wide statistics.

**Requires:** School Admin role.

**Returns:**
- School info (name, ID)
- Total teachers and students
- Total lessons created
- Active students today
- Average school-wide score
- Assessment completion stats
    """,
    responses={
        200: {"description": "School dashboard with aggregate statistics"},
        400: {"description": "User not associated with a school"},
        404: {"description": "School not found"},
    },
)
async def get_school_dashboard(
    current_user: CurrentUser = Depends(require_role([UserRole.SCHOOL_ADMIN])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get school admin dashboard with overview statistics."""
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
            active_students_today=0,
            average_school_score=progress_stats.get("average_score", 0),
            students_completed_assessment=0,
            lessons_delivered_today=0,
        )


@router.get(
    "/teachers",
    response_model=TeacherListResponse,
    summary="List school teachers",
    description="""
List all teachers in the school with their lesson counts.

**Requires:** School Admin role.

**Returns per teacher:**
- Basic info (name, email)
- Number of lessons created
- Account creation date

**Pagination:** Use `page` and `page_size` query parameters.
    """,
    responses={
        200: {"description": "Paginated list of teachers"},
        400: {"description": "User not associated with a school"},
    },
)
async def list_teachers(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(require_role([UserRole.SCHOOL_ADMIN])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """List teachers in the school."""
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


@router.get(
    "/{school_id}",
    response_model=SchoolResponse,
    summary="Get school details",
    description="""
Get detailed information about a specific school.

**Requires:** Any authenticated user.

**Returns:** School name, location, contact info, and current
teacher/student counts.
    """,
    responses={
        200: {"description": "School details"},
        404: {"description": "School not found"},
    },
)
async def get_school(
    school_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get school details."""
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
