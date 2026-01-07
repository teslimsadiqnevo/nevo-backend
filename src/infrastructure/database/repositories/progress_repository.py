"""Progress repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.progress import StudentProgress, LessonProgress, SkillProgress
from src.domain.interfaces.repositories import IProgressRepository
from src.core.config.constants import ProgressStatus
from src.infrastructure.database.models.progress import StudentProgressModel
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class ProgressRepository(BaseRepository[StudentProgressModel, StudentProgress], IProgressRepository):
    """Progress repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, StudentProgressModel)

    def _to_entity(self, model: StudentProgressModel) -> StudentProgress:
        """Convert model to entity."""
        # Parse lesson progress
        lesson_progress = {}
        for key, lp in (model.lesson_progress or {}).items():
            lesson_progress[key] = LessonProgress(
                lesson_id=UUID(lp["lesson_id"]),
                status=ProgressStatus(lp.get("status", "not_started")),
                started_at=lp.get("started_at"),
                completed_at=lp.get("completed_at"),
                time_spent_seconds=lp.get("time_spent_seconds", 0),
                score=lp.get("score"),
                blocks_completed=lp.get("blocks_completed", 0),
                total_blocks=lp.get("total_blocks", 0),
            )

        # Parse skill progress
        skill_progress = {}
        for key, sp in (model.skill_progress or {}).items():
            skill_progress[key] = SkillProgress(
                skill_name=sp["skill_name"],
                mastery_level=sp.get("mastery_level", 0),
                lessons_completed=sp.get("lessons_completed", 0),
                total_lessons=sp.get("total_lessons", 0),
                average_score=sp.get("average_score", 0),
                last_activity_at=sp.get("last_activity_at"),
            )

        return StudentProgress(
            id=model.id,
            student_id=model.student_id,
            lesson_progress=lesson_progress,
            skill_progress=skill_progress,
            total_lessons_completed=model.total_lessons_completed,
            total_time_spent_seconds=model.total_time_spent_seconds,
            average_score=model.average_score,
            current_streak_days=model.current_streak_days,
            longest_streak_days=model.longest_streak_days,
            last_activity_at=model.last_activity_at,
            last_lesson_id=model.last_lesson_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: StudentProgress) -> StudentProgressModel:
        """Convert entity to model."""
        # Serialize lesson progress
        lesson_progress_json = {}
        for key, lp in entity.lesson_progress.items():
            lesson_progress_json[key] = {
                "lesson_id": str(lp.lesson_id),
                "status": lp.status.value,
                "started_at": lp.started_at.isoformat() if lp.started_at else None,
                "completed_at": lp.completed_at.isoformat() if lp.completed_at else None,
                "time_spent_seconds": lp.time_spent_seconds,
                "score": lp.score,
                "blocks_completed": lp.blocks_completed,
                "total_blocks": lp.total_blocks,
            }

        # Serialize skill progress
        skill_progress_json = {}
        for key, sp in entity.skill_progress.items():
            skill_progress_json[key] = {
                "skill_name": sp.skill_name,
                "mastery_level": sp.mastery_level,
                "lessons_completed": sp.lessons_completed,
                "total_lessons": sp.total_lessons,
                "average_score": sp.average_score,
                "last_activity_at": sp.last_activity_at.isoformat() if sp.last_activity_at else None,
            }

        return StudentProgressModel(
            id=entity.id,
            student_id=entity.student_id,
            lesson_progress=lesson_progress_json,
            skill_progress=skill_progress_json,
            total_lessons_completed=entity.total_lessons_completed,
            total_time_spent_seconds=entity.total_time_spent_seconds,
            average_score=entity.average_score,
            current_streak_days=entity.current_streak_days,
            longest_streak_days=entity.longest_streak_days,
            last_activity_at=entity.last_activity_at,
            last_lesson_id=entity.last_lesson_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, progress: StudentProgress) -> StudentProgress:
        """Create progress record."""
        model = self._to_model(progress)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_student_id(self, student_id: UUID) -> Optional[StudentProgress]:
        """Get progress by student ID."""
        result = await self.session.execute(
            select(StudentProgressModel).where(StudentProgressModel.student_id == student_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, progress: StudentProgress) -> StudentProgress:
        """Update progress."""
        model = await self._get_by_id(progress.id)
        if model:
            updated = self._to_model(progress)
            model.lesson_progress = updated.lesson_progress
            model.skill_progress = updated.skill_progress
            model.total_lessons_completed = updated.total_lessons_completed
            model.total_time_spent_seconds = updated.total_time_spent_seconds
            model.average_score = updated.average_score
            model.current_streak_days = updated.current_streak_days
            model.longest_streak_days = updated.longest_streak_days
            model.last_activity_at = updated.last_activity_at
            model.last_lesson_id = updated.last_lesson_id
            model.updated_at = updated.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return progress

    async def get_aggregated_by_school(self, school_id: UUID) -> dict:
        """Get aggregated progress stats for a school."""
        result = await self.session.execute(
            select(
                func.count(StudentProgressModel.id).label("total_students"),
                func.avg(StudentProgressModel.average_score).label("avg_score"),
                func.sum(StudentProgressModel.total_lessons_completed).label("total_lessons"),
            ).join(
                UserModel, UserModel.id == StudentProgressModel.student_id
            ).where(
                UserModel.school_id == school_id
            )
        )
        row = result.one_or_none()

        return {
            "total_students": row.total_students if row else 0,
            "average_score": float(row.avg_score or 0),
            "total_lessons_completed": row.total_lessons if row else 0,
        }

    async def get_aggregated_by_teacher(self, teacher_id: UUID) -> dict:
        """Get aggregated progress stats for a teacher's students."""
        # For MVP, get progress of all students in teacher's school
        from src.infrastructure.database.models.user import UserModel

        teacher_result = await self.session.execute(
            select(UserModel.school_id).where(UserModel.id == teacher_id)
        )
        school_id = teacher_result.scalar_one_or_none()

        if not school_id:
            return {"total_students": 0, "average_score": 0, "total_lessons_completed": 0}

        return await self.get_aggregated_by_school(school_id)
