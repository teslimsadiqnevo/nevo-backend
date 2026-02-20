"""Connection repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.constants import ConnectionStatus
from src.domain.entities.connection import Connection
from src.domain.interfaces.repositories import IConnectionRepository
from src.infrastructure.database.models.connection import ConnectionModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class ConnectionRepository(
    BaseRepository[ConnectionModel, Connection],
    IConnectionRepository,
):
    """Connection repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ConnectionModel)

    def _to_entity(self, model: ConnectionModel) -> Connection:
        """Convert model to entity."""
        return Connection(
            id=model.id,
            student_id=model.student_id,
            teacher_id=model.teacher_id,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Connection) -> ConnectionModel:
        """Convert entity to model."""
        return ConnectionModel(
            id=entity.id,
            student_id=entity.student_id,
            teacher_id=entity.teacher_id,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, connection: Connection) -> Connection:
        """Create a new connection."""
        model = self._to_model(connection)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, connection_id: UUID) -> Optional[Connection]:
        """Get connection by ID."""
        model = await self._get_by_id(connection_id)
        return self._to_entity(model) if model else None

    async def update(self, connection: Connection) -> Connection:
        """Update connection."""
        model = await self._get_by_id(connection.id)
        if model:
            model.status = connection.status
            model.updated_at = connection.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return connection

    async def delete(self, connection_id: UUID) -> bool:
        """Delete connection."""
        return await self._delete(connection_id)

    async def list_by_student(self, student_id: UUID) -> List[Connection]:
        """List all connections for a student."""
        result = await self.session.execute(
            select(ConnectionModel)
            .where(ConnectionModel.student_id == student_id)
            .order_by(ConnectionModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_teacher(
        self, teacher_id: UUID, status: Optional[ConnectionStatus] = None
    ) -> List[Connection]:
        """List connections for a teacher, optionally filtered by status."""
        query = select(ConnectionModel).where(
            ConnectionModel.teacher_id == teacher_id
        )
        if status:
            query = query.where(ConnectionModel.status == status)
        query = query.order_by(ConnectionModel.created_at.desc())
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_student_and_teacher(
        self, student_id: UUID, teacher_id: UUID
    ) -> Optional[Connection]:
        """Get connection between a specific student and teacher."""
        result = await self.session.execute(
            select(ConnectionModel).where(
                ConnectionModel.student_id == student_id,
                ConnectionModel.teacher_id == teacher_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
