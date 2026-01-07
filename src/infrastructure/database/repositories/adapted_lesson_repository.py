"""Adapted lesson repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.adapted_lesson import AdaptedLesson, ContentBlock
from src.domain.interfaces.repositories import IAdaptedLessonRepository
from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.core.config.constants import AdaptedLessonStatus, ContentBlockType
from src.infrastructure.database.models.adapted_lesson import AdaptedLessonModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class AdaptedLessonRepository(BaseRepository[AdaptedLessonModel, AdaptedLesson], IAdaptedLessonRepository):
    """Adapted lesson repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AdaptedLessonModel)

    def _to_entity(self, model: AdaptedLessonModel) -> AdaptedLesson:
        """Convert model to entity."""
        entity = AdaptedLesson(
            id=model.id,
            lesson_id=model.lesson_id,
            student_id=model.student_id,
            lesson_title=model.lesson_title,
            adaptation_style=model.adaptation_style or "",
            content_blocks_json=model.content_blocks or [],
            status=model.status,
            is_active=model.is_active,
            ai_model_used=model.ai_model_used,
            generation_prompt_hash=model.generation_prompt_hash,
            generation_duration_ms=model.generation_duration_ms,
            created_at=model.created_at,
            updated_at=model.updated_at,
            view_count=model.view_count,
            completion_count=model.completion_count,
            average_time_spent_seconds=model.average_time_spent_seconds,
        )

        # Parse content blocks
        if model.content_blocks:
            entity.content_blocks = [
                ContentBlock(
                    type=ContentBlockType(block.get("type", "text")),
                    content=block.get("content", ""),
                    order=idx,
                    emphasis=block.get("emphasis", []),
                    ai_generated_url=block.get("ai_generated_url"),
                    question=block.get("question"),
                    options=block.get("options", []),
                    correct_index=block.get("correct_index"),
                    metadata=block.get("metadata", {}),
                )
                for idx, block in enumerate(model.content_blocks)
            ]

        return entity

    def _to_model(self, entity: AdaptedLesson) -> AdaptedLessonModel:
        """Convert entity to model."""
        return AdaptedLessonModel(
            id=entity.id,
            lesson_id=entity.lesson_id,
            student_id=entity.student_id,
            lesson_title=entity.lesson_title,
            adaptation_style=entity.adaptation_style,
            content_blocks=entity.content_blocks_json,
            status=entity.status,
            is_active=entity.is_active,
            ai_model_used=entity.ai_model_used,
            generation_prompt_hash=entity.generation_prompt_hash,
            generation_duration_ms=entity.generation_duration_ms,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            view_count=entity.view_count,
            completion_count=entity.completion_count,
            average_time_spent_seconds=entity.average_time_spent_seconds,
        )

    async def create(self, adapted_lesson: AdaptedLesson) -> AdaptedLesson:
        """Create a new adapted lesson."""
        model = self._to_model(adapted_lesson)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, adapted_lesson_id: UUID) -> Optional[AdaptedLesson]:
        """Get adapted lesson by ID."""
        model = await self._get_by_id(adapted_lesson_id)
        return self._to_entity(model) if model else None

    async def get_by_lesson_and_student(
        self,
        lesson_id: UUID,
        student_id: UUID,
    ) -> Optional[AdaptedLesson]:
        """Get adapted lesson for a specific student and lesson."""
        result = await self.session.execute(
            select(AdaptedLessonModel).where(
                and_(
                    AdaptedLessonModel.lesson_id == lesson_id,
                    AdaptedLessonModel.student_id == student_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, adapted_lesson: AdaptedLesson) -> AdaptedLesson:
        """Update adapted lesson."""
        model = await self._get_by_id(adapted_lesson.id)
        if model:
            model.lesson_title = adapted_lesson.lesson_title
            model.adaptation_style = adapted_lesson.adaptation_style
            model.content_blocks = adapted_lesson.content_blocks_json
            model.status = adapted_lesson.status
            model.is_active = adapted_lesson.is_active
            model.ai_model_used = adapted_lesson.ai_model_used
            model.generation_duration_ms = adapted_lesson.generation_duration_ms
            model.view_count = adapted_lesson.view_count
            model.completion_count = adapted_lesson.completion_count
            model.average_time_spent_seconds = adapted_lesson.average_time_spent_seconds
            model.updated_at = adapted_lesson.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return adapted_lesson

    async def list_by_student(
        self,
        student_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[AdaptedLesson]:
        """List adapted lessons for a student."""
        query = select(AdaptedLessonModel).where(
            AdaptedLessonModel.student_id == student_id
        ).order_by(AdaptedLessonModel.created_at.desc())

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )
