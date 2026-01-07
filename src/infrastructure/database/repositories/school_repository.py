"""School repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.school import School
from src.domain.interfaces.repositories import ISchoolRepository
from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.infrastructure.database.models.school import SchoolModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class SchoolRepository(BaseRepository[SchoolModel, School], ISchoolRepository):
    """School repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, SchoolModel)

    def _to_entity(self, model: SchoolModel) -> School:
        """Convert model to entity."""
        return School(
            id=model.id,
            name=model.name,
            address=model.address,
            city=model.city,
            state=model.state,
            country=model.country,
            postal_code=model.postal_code,
            phone_number=model.phone_number,
            email=model.email,
            website=model.website,
            logo_url=model.logo_url,
            is_active=model.is_active,
            subscription_tier=model.subscription_tier,
            max_teachers=model.max_teachers,
            max_students=model.max_students,
            teacher_count=model.teacher_count,
            student_count=model.student_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: School) -> SchoolModel:
        """Convert entity to model."""
        return SchoolModel(
            id=entity.id,
            name=entity.name,
            address=entity.address,
            city=entity.city,
            state=entity.state,
            country=entity.country,
            postal_code=entity.postal_code,
            phone_number=entity.phone_number,
            email=entity.email,
            website=entity.website,
            logo_url=entity.logo_url,
            is_active=entity.is_active,
            subscription_tier=entity.subscription_tier,
            max_teachers=entity.max_teachers,
            max_students=entity.max_students,
            teacher_count=entity.teacher_count,
            student_count=entity.student_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, school: School) -> School:
        """Create a new school."""
        model = self._to_model(school)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, school_id: UUID) -> Optional[School]:
        """Get school by ID."""
        model = await self._get_by_id(school_id)
        return self._to_entity(model) if model else None

    async def update(self, school: School) -> School:
        """Update school."""
        model = await self._get_by_id(school.id)
        if model:
            model.name = school.name
            model.address = school.address
            model.city = school.city
            model.state = school.state
            model.phone_number = school.phone_number
            model.email = school.email
            model.is_active = school.is_active
            model.teacher_count = school.teacher_count
            model.student_count = school.student_count
            model.updated_at = school.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return school

    async def delete(self, school_id: UUID) -> bool:
        """Delete school."""
        return await self._delete(school_id)

    async def list_all(
        self,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[School]:
        """List all schools."""
        query = select(SchoolModel).order_by(SchoolModel.created_at.desc())

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )
