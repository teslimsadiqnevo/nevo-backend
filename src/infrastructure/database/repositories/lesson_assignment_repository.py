"""Lesson assignment repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.constants import AssignmentStatus
from src.domain.entities.lesson_assignment import LessonAssignment
from src.domain.interfaces.repositories import ILessonAssignmentRepository
from src.infrastructure.database.models.lesson_assignment import LessonAssignmentModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class LessonAssignmentRepository(
    BaseRepository[LessonAssignmentModel, LessonAssignment],
    ILessonAssignmentRepository,
):
    """Lesson assignment repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LessonAssignmentModel)

    def _to_entity(self, model: LessonAssignmentModel) -> LessonAssignment:
        return LessonAssignment(
            id=model.id,
            lesson_id=model.lesson_id,
            student_id=model.student_id,
            teacher_id=model.teacher_id,
            assignment_type=model.assignment_type,
            status=model.status,
            assigned_at=model.assigned_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: LessonAssignment) -> LessonAssignmentModel:
        return LessonAssignmentModel(
            id=entity.id,
            lesson_id=entity.lesson_id,
            student_id=entity.student_id,
            teacher_id=entity.teacher_id,
            assignment_type=entity.assignment_type,
            status=entity.status,
            assigned_at=entity.assigned_at,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, assignment: LessonAssignment) -> LessonAssignment:
        model = self._to_model(assignment)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, assignment_id: UUID) -> Optional[LessonAssignment]:
        model = await self._get_by_id(assignment_id)
        return self._to_entity(model) if model else None

    async def update(self, assignment: LessonAssignment) -> LessonAssignment:
        model = await self._get_by_id(assignment.id)
        if model:
            model.status = assignment.status
            model.started_at = assignment.started_at
            model.completed_at = assignment.completed_at
            model.updated_at = assignment.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return assignment

    async def list_by_teacher(
        self, teacher_id: UUID, status: Optional[AssignmentStatus] = None
    ) -> List[LessonAssignment]:
        query = select(LessonAssignmentModel).where(
            LessonAssignmentModel.teacher_id == teacher_id
        )
        if status:
            query = query.where(LessonAssignmentModel.status == status)
        query = query.order_by(LessonAssignmentModel.assigned_at.desc())
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_student(
        self, student_id: UUID, status: Optional[AssignmentStatus] = None
    ) -> List[LessonAssignment]:
        query = select(LessonAssignmentModel).where(
            LessonAssignmentModel.student_id == student_id
        )
        if status:
            query = query.where(LessonAssignmentModel.status == status)
        query = query.order_by(LessonAssignmentModel.assigned_at.desc())
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_lesson(self, lesson_id: UUID) -> List[LessonAssignment]:
        query = (
            select(LessonAssignmentModel)
            .where(LessonAssignmentModel.lesson_id == lesson_id)
            .order_by(LessonAssignmentModel.assigned_at.desc())
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_lesson_and_student(
        self, lesson_id: UUID, student_id: UUID
    ) -> Optional[LessonAssignment]:
        query = select(LessonAssignmentModel).where(
            LessonAssignmentModel.lesson_id == lesson_id,
            LessonAssignmentModel.student_id == student_id,
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def count_by_teacher(self, teacher_id: UUID) -> int:
        query = select(func.count()).where(
            LessonAssignmentModel.teacher_id == teacher_id
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def bulk_create(
        self, assignments: List[LessonAssignment]
    ) -> List[LessonAssignment]:
        models = [self._to_model(a) for a in assignments]
        self.session.add_all(models)
        await self.session.flush()
        return [self._to_entity(m) for m in models]
