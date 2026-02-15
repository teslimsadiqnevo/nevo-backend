"""TeacherFeedback repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.teacher_feedback import TeacherFeedback
from src.domain.interfaces.repositories import ITeacherFeedbackRepository
from src.infrastructure.database.models.teacher_feedback import TeacherFeedbackModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class TeacherFeedbackRepository(
    BaseRepository[TeacherFeedbackModel, TeacherFeedback],
    ITeacherFeedbackRepository,
):
    """TeacherFeedback repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TeacherFeedbackModel)

    def _to_entity(self, model: TeacherFeedbackModel) -> TeacherFeedback:
        """Convert model to entity."""
        return TeacherFeedback(
            id=model.id,
            teacher_id=model.teacher_id,
            student_id=model.student_id,
            lesson_id=model.lesson_id,
            message=model.message,
            created_at=model.created_at,
        )

    def _to_model(self, entity: TeacherFeedback) -> TeacherFeedbackModel:
        """Convert entity to model."""
        return TeacherFeedbackModel(
            id=entity.id,
            teacher_id=entity.teacher_id,
            student_id=entity.student_id,
            lesson_id=entity.lesson_id,
            message=entity.message,
            created_at=entity.created_at,
        )

    async def create(self, feedback: TeacherFeedback) -> TeacherFeedback:
        """Create a new feedback."""
        model = self._to_model(feedback)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, feedback_id: UUID) -> Optional[TeacherFeedback]:
        """Get feedback by ID."""
        model = await self._get_by_id(feedback_id)
        return self._to_entity(model) if model else None

    async def list_by_student(
        self, student_id: UUID, limit: int = 5
    ) -> List[TeacherFeedback]:
        """List recent feedback for a student."""
        result = await self.session.execute(
            select(TeacherFeedbackModel)
            .where(TeacherFeedbackModel.student_id == student_id)
            .order_by(TeacherFeedbackModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]
