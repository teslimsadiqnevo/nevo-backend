"""Connection database model."""

from sqlalchemy import Column, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.core.config.constants import ConnectionStatus
from src.infrastructure.database.models.base import BaseModel


class ConnectionModel(BaseModel):
    """Connection database model - Student-teacher connections."""

    __tablename__ = "connections"
    __table_args__ = (
        UniqueConstraint("student_id", "teacher_id", name="uq_student_teacher"),
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(ConnectionStatus),
        default=ConnectionStatus.PENDING,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Connection(id={self.id}, student={self.student_id}, teacher={self.teacher_id}, status={self.status})>"
