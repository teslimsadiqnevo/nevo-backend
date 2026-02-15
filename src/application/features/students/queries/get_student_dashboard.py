"""Get student dashboard query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.students.dtos import (
    StudentDashboardOutput,
    CurrentLessonOutput,
    RecentFeedbackOutput,
    DashboardStatsOutput,
)
from src.core.exceptions import EntityNotFoundError


class GetStudentDashboardQuery:
    """Query to get all data needed for the student home dashboard."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, student_id: UUID) -> StudentDashboardOutput:
        """Fetch student dashboard data in a single query."""
        async with self.uow:
            # Get student
            student = await self.uow.users.get_by_id(student_id)
            if not student:
                raise EntityNotFoundError("User", student_id)

            # Get progress
            progress = await self.uow.progress.get_by_student_id(student_id)

            # Build current lesson card
            current_lesson = None
            if progress and progress.last_lesson_id:
                lesson = await self.uow.lessons.get_by_id(progress.last_lesson_id)
                if lesson:
                    lp = progress.get_lesson_progress(progress.last_lesson_id)
                    current_lesson = CurrentLessonOutput(
                        lesson_id=lesson.id,
                        title=lesson.title,
                        subject=lesson.subject,
                        topic=lesson.topic,
                        current_step=lp.blocks_completed if lp else 0,
                        total_steps=lp.total_blocks if lp else 0,
                    )

            # Get recent teacher feedback
            feedbacks = await self.uow.teacher_feedbacks.list_by_student(
                student_id, limit=3
            )
            recent_feedback = []
            for fb in feedbacks:
                teacher = await self.uow.users.get_by_id(fb.teacher_id)
                recent_feedback.append(
                    RecentFeedbackOutput(
                        message=fb.message,
                        teacher_name=teacher.full_name if teacher else "Teacher",
                        created_at=fb.created_at,
                    )
                )

            # Build stats
            stats = DashboardStatsOutput(
                total_lessons_completed=progress.total_lessons_completed if progress else 0,
                current_streak_days=progress.current_streak_days if progress else 0,
                average_score=round(progress.average_score, 1) if progress else 0.0,
            )

            # Get attention span from neuro profile
            profile = await self.uow.neuro_profiles.get_by_user_id(student_id)
            attention_span = profile.attention_span_minutes if profile else 15

            return StudentDashboardOutput(
                student_name=student.first_name,
                current_lesson=current_lesson,
                recent_feedback=recent_feedback,
                stats=stats,
                attention_span_minutes=attention_span,
            )
