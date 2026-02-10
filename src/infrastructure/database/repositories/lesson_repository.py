"""Lesson repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config.constants import LessonStatus
from src.domain.entities.lesson import Lesson
from src.domain.interfaces.repositories import ILessonRepository
from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.infrastructure.database.models.lesson import LessonModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository[LessonModel, Lesson], ILessonRepository):
    """Lesson repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LessonModel)

    def _to_entity(self, model: LessonModel) -> Lesson:
        """Convert model to entity."""
        return Lesson(
            id=model.id,
            title=model.title,
            teacher_id=model.teacher_id,
            school_id=model.school_id,
            description=model.description,
            original_text_content=model.original_text_content,
            media_url=model.media_url,
            media_type=model.media_type,
            subject=model.subject,
            topic=model.topic,
            target_grade_level=model.target_grade_level,
            estimated_duration_minutes=model.estimated_duration_minutes,
            tags=model.tags or [],
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            published_at=model.published_at,
            view_count=model.view_count,
            adaptation_count=model.adaptation_count,
        )

    def _to_model(self, entity: Lesson) -> LessonModel:
        """Convert entity to model."""
        return LessonModel(
            id=entity.id,
            title=entity.title,
            teacher_id=entity.teacher_id,
            school_id=entity.school_id,
            description=entity.description,
            original_text_content=entity.original_text_content,
            media_url=entity.media_url,
            media_type=entity.media_type,
            subject=entity.subject,
            topic=entity.topic,
            target_grade_level=entity.target_grade_level,
            estimated_duration_minutes=entity.estimated_duration_minutes,
            tags=entity.tags,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            published_at=entity.published_at,
            view_count=entity.view_count,
            adaptation_count=entity.adaptation_count,
        )

    async def create(self, lesson: Lesson) -> Lesson:
        """Create a new lesson."""
        model = self._to_model(lesson)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        """Get lesson by ID."""
        model = await self._get_by_id(lesson_id)
        return self._to_entity(model) if model else None

    async def update(self, lesson: Lesson) -> Lesson:
        """Update lesson."""
        model = await self._get_by_id(lesson.id)
        if model:
            model.title = lesson.title
            model.description = lesson.description
            model.original_text_content = lesson.original_text_content
            model.media_url = lesson.media_url
            model.status = lesson.status
            model.published_at = lesson.published_at
            model.view_count = lesson.view_count
            model.adaptation_count = lesson.adaptation_count
            model.updated_at = lesson.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return lesson

    async def delete(self, lesson_id: UUID) -> bool:
        """Delete lesson."""
        return await self._delete(lesson_id)

    async def list_by_teacher(
        self,
        teacher_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List lessons by teacher."""
        query = (
            select(LessonModel)
            .options(selectinload(LessonModel.teacher), selectinload(LessonModel.school))
            .where(LessonModel.teacher_id == teacher_id)
            .order_by(LessonModel.created_at.desc())
        )

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )

    async def list_by_school(
        self,
        school_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List lessons by school."""
        query = (
            select(LessonModel)
            .options(selectinload(LessonModel.teacher), selectinload(LessonModel.school))
            .where(LessonModel.school_id == school_id)
            .order_by(LessonModel.created_at.desc())
        )

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )

    async def list_published(
        self,
        school_id: Optional[UUID] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List published lessons."""
        query = (
            select(LessonModel)
            .options(selectinload(LessonModel.teacher), selectinload(LessonModel.school))
            .where(LessonModel.status == LessonStatus.PUBLISHED)
        )

        if school_id:
            query = query.where(LessonModel.school_id == school_id)

        query = query.order_by(LessonModel.published_at.desc())

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )
