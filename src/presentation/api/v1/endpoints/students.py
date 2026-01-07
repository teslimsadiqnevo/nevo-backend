"""Student endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.queries import GetStudentProfileQuery
from src.application.features.progress.queries import GetStudentProgressQuery
from src.core.config.constants import UserRole
from src.core.exceptions import EntityNotFoundError
from src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_uow,
    require_role,
    CurrentUser,
)
from src.presentation.schemas.student import (
    StudentProfileResponse,
    StudentProgressResponse,
)

router = APIRouter()


@router.get("/me/profile", response_model=StudentProfileResponse)
async def get_my_profile(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get current student's learning profile.
    """
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


@router.get("/me/progress", response_model=StudentProgressResponse)
async def get_my_progress(
    current_user: CurrentUser = Depends(require_role([UserRole.STUDENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get current student's learning progress.
    """
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


@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    student_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.PARENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get a student's learning profile (for teachers/parents).
    """
    # TODO: Add authorization check for parent access
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


@router.get("/{student_id}/progress", response_model=StudentProgressResponse)
async def get_student_progress(
    student_id: UUID,
    current_user: CurrentUser = Depends(require_role([UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.PARENT])),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Get a student's learning progress (for teachers/parents).
    """
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
