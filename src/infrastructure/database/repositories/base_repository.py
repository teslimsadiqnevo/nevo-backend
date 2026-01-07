"""Base repository with common CRUD operations."""

from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.infrastructure.database.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
EntityType = TypeVar("EntityType")


class BaseRepository(Generic[ModelType, EntityType]):
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model_class = model_class

    async def _get_by_id(self, entity_id: UUID) -> Optional[ModelType]:
        """Get model by ID."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def _create(self, model: ModelType) -> ModelType:
        """Create a new model."""
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def _update(self, model: ModelType) -> ModelType:
        """Update an existing model."""
        await self.session.merge(model)
        await self.session.flush()
        return model

    async def _delete(self, entity_id: UUID) -> bool:
        """Delete a model by ID."""
        model = await self._get_by_id(entity_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def _paginate(
        self,
        query,
        pagination: Optional[PaginationParams] = None,
    ) -> tuple[List[ModelType], int]:
        """Execute a query with pagination."""
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total
