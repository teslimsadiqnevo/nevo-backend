"""Student endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.queries import GetStudentProfileQuery, GetStudentDashboardQuery
from src.application.features.students.commands import SetPinCommand
from src.application.features.progress.queries import GetStudentProgressQuery
from src.application.features.connections.queries import GetStudentConnectionsQuery
from src.application.features.connections.commands import (
    SendConnectionRequestCommand,
    RemoveConnectionCommand,
)
from src.application.features.connections.dtos import (
    SendConnectionRequestInput,
    RemoveConnectionInput,
)
from src.application.features.auth.dtos import SetPinInput
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError, ValidationError, ConflictError
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.student import (
    StudentProfileResponse,
    StudentProgressResponse,
    StudentDashboardResponse,
)
from src.presentation.schemas.connection import (
    StudentConnectionsResponse,
    SendConnectionRequest,
    SendConnectionResponse,
)
from src.presentation.schemas.auth import SetPinRequest, SetPinResponse

router = APIRouter()


@router.get(
    "/me/dashboard",
    response_model=StudentDashboardResponse,
    summary="Get student home dashboard",
    description="""
Get all data needed for the student Home page in a single call.

**Requires:** Student role.

**Returns:**
- Student's first name for greeting
- Current/last lesson in progress with step progress
- Recent teacher feedback messages
- Learning stats (lessons completed, streak, average score)
- Attention span for break timer
    """,
    responses={
        200: {"description": "Student dashboard data"},
        404: {"description": "Student not found"},
    },
)
async def get_my_dashboard(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get current student's home dashboard."""
    try:
        query = GetStudentDashboardQuery(uow)
        result = await query.execute(current_user.id)

        return StudentDashboardResponse(
            student_name=result.student_name,
            current_lesson={
                "lesson_id": str(result.current_lesson.lesson_id),
                "title": result.current_lesson.title,
                "subject": result.current_lesson.subject,
                "topic": result.current_lesson.topic,
                "current_step": result.current_lesson.current_step,
                "total_steps": result.current_lesson.total_steps,
            } if result.current_lesson else None,
            recent_feedback=[
                {
                    "message": fb.message,
                    "teacher_name": fb.teacher_name,
                    "created_at": fb.created_at.isoformat(),
                }
                for fb in result.recent_feedback
            ],
            stats={
                "total_lessons_completed": result.stats.total_lessons_completed,
                "current_streak_days": result.stats.current_streak_days,
                "average_score": result.stats.average_score,
            },
            attention_span_minutes=result.attention_span_minutes,
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    "/me/profile",
    response_model=StudentProfileResponse,
    summary="Get my learning profile",
    description="""
Get the current student's AI-generated NeuroProfile.

**Requires:** Student role.

**Returns:** The student's personalized learning profile including:
- Learning style (visual, auditory, kinesthetic, etc.)
- Reading level
- Complexity tolerance
- Estimated attention span in minutes
- Sensory triggers to avoid
- Interest areas
- Profile version and last update time

**Prerequisite:** Student must have completed the onboarding assessment.
    """,
    responses={
        200: {"description": "Student's NeuroProfile"},
        404: {"description": "Profile not found — student hasn't completed assessment"},
    },
)
async def get_my_profile(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get current student's learning profile."""
    try:
        query = GetStudentProfileQuery(uow)
        result = await query.execute(current_user.id)

        return StudentProfileResponse(
            student_id=str(result.student_id),
            student_name=result.student_name,
            learning_style=result.learning_style,
            reading_level=result.reading_level,
            complexity_tolerance=result.complexity_tolerance,
            attention_span_minutes=result.attention_span_minutes,
            sensory_triggers=result.sensory_triggers,
            interests=result.interests,
            profile_version=result.profile_version,
            last_updated=result.last_updated.isoformat(),
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    "/me/progress",
    response_model=StudentProgressResponse,
    summary="Get my learning progress",
    description="""
Get the current student's overall learning progress and statistics.

**Requires:** Student role.

**Returns:**
- Total lessons completed and time spent
- Average score across all lessons
- Current and longest learning streaks
- Per-lesson progress breakdown (status, percentage, score)
- Skill mastery levels
    """,
    responses={
        200: {"description": "Student's progress summary with lesson and skill details"},
        404: {"description": "Progress not found"},
    },
)
async def get_my_progress(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get current student's learning progress."""
    try:
        query = GetStudentProgressQuery(uow)
        result = await query.execute(current_user.id)

        return StudentProgressResponse(
            student_id=str(result.student_id),
            student_name=result.student_name,
            total_lessons_completed=result.total_lessons_completed,
            total_time_spent_minutes=result.total_time_spent_minutes,
            average_score=result.average_score,
            current_streak_days=result.current_streak_days,
            longest_streak_days=result.longest_streak_days,
            last_activity_at=result.last_activity_at.isoformat() if result.last_activity_at else None,
            lessons=[
                {
                    "lesson_id": str(l.lesson_id),
                    "lesson_title": l.lesson_title,
                    "status": l.status,
                    "progress_percentage": l.progress_percentage,
                    "score": l.score,
                }
                for l in result.lessons
            ],
            skills=[
                {
                    "skill_name": s.skill_name,
                    "mastery_level": s.mastery_level,
                    "lessons_completed": s.lessons_completed,
                }
                for s in result.skills
            ],
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post(
    "/me/pin",
    response_model=SetPinResponse,
    summary="Set or update my PIN",
    description="""
Set or update the student's 4-digit PIN for Nevo ID login.

**Requires:** Student role.

**Prerequisites:**
- Student must have completed their assessment (Nevo ID auto-generated)

**PIN Requirements:**
- Exactly 4 digits (0-9)
- Setting a new PIN overwrites the previous one

**After setting PIN:**
Student can login using `POST /auth/login/nevo-id` with their Nevo ID + PIN.
    """,
    responses={
        200: {"description": "PIN set successfully, returns Nevo ID"},
        400: {"description": "Invalid PIN format or no Nevo ID (assessment not completed)"},
        404: {"description": "User not found"},
    },
)
async def set_my_pin(
    request: SetPinRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Set or update student's 4-digit PIN (students only)."""
    try:
        command = SetPinCommand(uow)
        result = await command.execute(
            SetPinInput(user_id=current_user.id, pin=request.pin)
        )

        return SetPinResponse(
            success=result.success,
            message=result.message,
            nevo_id=result.nevo_id,
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


@router.get(
    "/me/connections",
    response_model=StudentConnectionsResponse,
    summary="Get my connections",
    description="""
Get the student's teacher connections (pending and accepted).

**Requires:** Student role.

**Returns:**
- Student's Nevo ID
- Pending connection requests
- Connected teachers with name and subject
    """,
    responses={
        200: {"description": "Student's connections"},
        404: {"description": "Student not found"},
    },
)
async def get_my_connections(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get current student's teacher connections."""
    try:
        query = GetStudentConnectionsQuery(uow)
        result = await query.execute(current_user.id)

        return StudentConnectionsResponse(
            nevo_id=result.nevo_id,
            pending=[
                {
                    "connection_id": str(c.connection_id),
                    "teacher_name": c.teacher_name,
                    "subject": c.subject,
                    "created_at": c.created_at.isoformat(),
                }
                for c in result.pending
            ],
            connected=[
                {
                    "connection_id": str(c.connection_id),
                    "teacher_name": c.teacher_name,
                    "subject": c.subject,
                    "created_at": c.created_at.isoformat(),
                }
                for c in result.connected
            ],
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post(
    "/me/connections",
    response_model=SendConnectionResponse,
    summary="Send connection request",
    description="""
Send a connection request to a teacher using their class code.

**Requires:** Student role.

**Input:** Teacher's class code (e.g. NEVO-CLASS-4K7)
    """,
    responses={
        200: {"description": "Connection request sent"},
        404: {"description": "Teacher not found for class code"},
        409: {"description": "Already connected or request pending"},
    },
)
async def send_connection_request(
    request: SendConnectionRequest,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Send a connection request to a teacher."""
    try:
        command = SendConnectionRequestCommand(uow)
        result = await command.execute(
            SendConnectionRequestInput(
                student_id=current_user.id,
                class_code=request.class_code,
            )
        )

        return SendConnectionResponse(
            connection_id=str(result.connection_id),
            teacher_name=result.teacher_name,
            status=result.status,
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.delete(
    "/me/connections/{connection_id}",
    summary="Remove a connection",
    description="""
Remove a teacher connection (pending or accepted).

**Requires:** Student role.
    """,
    responses={
        200: {"description": "Connection removed"},
        404: {"description": "Connection not found"},
    },
)
async def remove_connection(
    connection_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Remove a student's connection."""
    try:
        command = RemoveConnectionCommand(uow)
        await command.execute(
            RemoveConnectionInput(
                student_id=current_user.id,
                connection_id=connection_id,
            )
        )
        return {"message": "Connection removed"}

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


@router.get(
    "/{student_id}/profile",
    response_model=StudentProfileResponse,
    summary="Get a student's learning profile",
    description="""
View a specific student's NeuroProfile.

**Requires:** Teacher, School Admin, or Parent role.

**Use cases:**
- Teachers reviewing a student's learning preferences before class
- Parents monitoring their child's profile
- School admins auditing student assessments
    """,
    responses={
        200: {"description": "Student's NeuroProfile"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Student or profile not found"},
    },
)
async def get_student_profile(
    student_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.PARENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get a student's learning profile (teachers/parents/admins)."""
    try:
        query = GetStudentProfileQuery(uow)
        result = await query.execute(student_id)

        return StudentProfileResponse(
            student_id=str(result.student_id),
            student_name=result.student_name,
            learning_style=result.learning_style,
            reading_level=result.reading_level,
            complexity_tolerance=result.complexity_tolerance,
            attention_span_minutes=result.attention_span_minutes,
            sensory_triggers=result.sensory_triggers,
            interests=result.interests,
            profile_version=result.profile_version,
            last_updated=result.last_updated.isoformat(),
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    "/{student_id}/progress",
    response_model=StudentProgressResponse,
    summary="Get a student's learning progress",
    description="""
View a specific student's learning progress and statistics.

**Requires:** Teacher, School Admin, or Parent role.

**Returns:** Same data as `/me/progress` but for a specific student.
Useful for teachers tracking student engagement and parents monitoring progress.
    """,
    responses={
        200: {"description": "Student's progress summary"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Student or progress not found"},
    },
)
async def get_student_progress(
    student_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.PARENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get a student's learning progress (teachers/parents/admins)."""
    try:
        query = GetStudentProgressQuery(uow)
        result = await query.execute(student_id)

        return StudentProgressResponse(
            student_id=str(result.student_id),
            student_name=result.student_name,
            total_lessons_completed=result.total_lessons_completed,
            total_time_spent_minutes=result.total_time_spent_minutes,
            average_score=result.average_score,
            current_streak_days=result.current_streak_days,
            longest_streak_days=result.longest_streak_days,
            last_activity_at=result.last_activity_at.isoformat() if result.last_activity_at else None,
            lessons=[
                {
                    "lesson_id": str(l.lesson_id),
                    "lesson_title": l.lesson_title,
                    "status": l.status,
                    "progress_percentage": l.progress_percentage,
                    "score": l.score,
                }
                for l in result.lessons
            ],
            skills=[
                {
                    "skill_name": s.skill_name,
                    "mastery_level": s.mastery_level,
                    "lessons_completed": s.lessons_completed,
                }
                for s in result.skills
            ],
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
