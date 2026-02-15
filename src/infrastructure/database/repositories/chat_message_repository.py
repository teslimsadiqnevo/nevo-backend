"""ChatMessage repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.chat_message import ChatMessage
from src.domain.interfaces.repositories import IChatMessageRepository
from src.infrastructure.database.models.chat_message import ChatMessageModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class ChatMessageRepository(
    BaseRepository[ChatMessageModel, ChatMessage],
    IChatMessageRepository,
):
    """ChatMessage repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatMessageModel)

    def _to_entity(self, model: ChatMessageModel) -> ChatMessage:
        """Convert model to entity."""
        return ChatMessage(
            id=model.id,
            student_id=model.student_id,
            role=model.role,
            content=model.content,
            lesson_id=model.lesson_id,
            created_at=model.created_at,
        )

    def _to_model(self, entity: ChatMessage) -> ChatMessageModel:
        """Convert entity to model."""
        return ChatMessageModel(
            id=entity.id,
            student_id=entity.student_id,
            role=entity.role,
            content=entity.content,
            lesson_id=entity.lesson_id,
            created_at=entity.created_at,
        )

    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message."""
        model = self._to_model(message)
        created = await self._create(model)
        return self._to_entity(created)

    async def list_by_student(
        self, student_id: UUID, limit: int = 50
    ) -> List[ChatMessage]:
        """List recent chat messages for a student."""
        result = await self.session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.student_id == student_id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(limit)
        )
        # Return in chronological order
        return list(reversed([self._to_entity(m) for m in result.scalars().all()]))
