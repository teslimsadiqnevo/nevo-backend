"""ChatMessage database model."""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.database.models.base import BaseModel


class ChatMessageModel(BaseModel):
    """ChatMessage database model - Student-Nevo AI conversations."""

    __tablename__ = "chat_messages"

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(10), nullable=False)  # "student" or "nevo"
    content = Column(Text, nullable=False)
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, student={self.student_id}, role={self.role})>"
