"""Waitlist repository implementation."""

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.waitlist import WaitlistEntry
from src.domain.interfaces.repositories import IWaitlistRepository
from src.infrastructure.database.models.waitlist import WaitlistModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class WaitlistRepository(BaseRepository[WaitlistModel, WaitlistEntry], IWaitlistRepository):
    """Waitlist repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, WaitlistModel)

    def _to_entity(self, model: WaitlistModel) -> WaitlistEntry:
        """Convert model to entity."""
        return WaitlistEntry(
            id=model.id,
            name=model.name,
            email=model.email,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: WaitlistEntry) -> WaitlistModel:
        """Convert entity to model."""
        return WaitlistModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            role=entity.role,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Create a waitlist entry."""
        model = self._to_model(entry)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_email(self, email: str) -> Optional[WaitlistEntry]:
        """Get waitlist entry by email."""
        result = await self.session.execute(
            select(WaitlistModel).where(
                func.lower(WaitlistModel.email) == email.lower()
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(
        self, limit: int = 100, offset: int = 0, role: Optional[str] = None
    ) -> List[WaitlistEntry]:
        """List waitlist entries with optional role filter."""
        query = select(WaitlistModel)
        if role:
            query = query.where(WaitlistModel.role == role)
        query = query.order_by(WaitlistModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count(self) -> int:
        """Count total waitlist entries."""
        result = await self.session.execute(
            select(func.count(WaitlistModel.id))
        )
        return result.scalar_one()

    async def count_by_role(self) -> Dict[str, int]:
        """Get counts grouped by role."""
        result = await self.session.execute(
            select(WaitlistModel.role, func.count(WaitlistModel.id))
            .group_by(WaitlistModel.role)
        )
        return {row[0]: row[1] for row in result.all()}
