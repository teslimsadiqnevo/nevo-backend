"""Get student progress query."""

from uuid import UUID

from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.progress.dtos import (
    LessonProgressOutput,
    SkillProgressOutput,
    StudentProgressOutput,
)
from src.core.exceptions import EntityNotFoundError


class GetStudentProgressQuery:
    """Query to get a student's learning progress."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, student_id: UUID) -> StudentProgressOutput:
        """Get student's complete progress."""
        async with self.uow:
            # Get student
            student = await self.uow.users.get_by_id(student_id)
            if not student:
                raise EntityNotFoundError("User", student_id)

            # Get progress
            progress = await self.uow.progress.get_by_student_id(student_id)

            if not progress:
                return StudentProgressOutput(
                    student_id=student_id,
                    student_name=student.full_name,
                    total_lessons_completed=0,
                    total_time_spent_minutes=0,
                    average_score=0.0,
                    current_streak_days=0,
                    longest_streak_days=0,
                    last_activity_at=None,
                )

            # Build lesson progress list
            lesson_outputs = []
            for lesson_key, lp in progress.lesson_progress.items():
                # Get lesson title
                lesson = await self.uow.lessons.get_by_id(lp.lesson_id)
                lesson_title = lesson.title if lesson else "Unknown"

                lesson_outputs.append(
                    LessonProgressOutput(
                        lesson_id=lp.lesson_id,
                        lesson_title=lesson_title,
                        status=lp.status.value,
                        progress_percentage=lp.progress_percentage,
                        time_spent_minutes=lp.time_spent_seconds // 60,
                        score=lp.score,
                        started_at=lp.started_at,
                        completed_at=lp.completed_at,
                    )
                )

            # Build skill progress list
            skill_outputs = [
                SkillProgressOutput(
                    skill_name=sp.skill_name,
                    mastery_level=sp.mastery_level,
                    lessons_completed=sp.lessons_completed,
                    total_lessons=sp.total_lessons,
                    average_score=sp.average_score,
                )
                for sp in progress.skill_progress.values()
            ]

            return StudentProgressOutput(
                student_id=student_id,
                student_name=student.full_name,
                total_lessons_completed=progress.total_lessons_completed,
                total_time_spent_minutes=progress.total_time_spent_seconds // 60,
                average_score=progress.average_score,
                current_streak_days=progress.current_streak_days,
                longest_streak_days=progress.longest_streak_days,
                last_activity_at=progress.last_activity_at,
                lessons=lesson_outputs,
                skills=skill_outputs,
            )
