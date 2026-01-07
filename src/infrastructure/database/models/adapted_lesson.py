"""AdaptedLesson database model."""

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import AdaptedLessonStatus
from src.infrastructure.database.models.base import BaseModel


class AdaptedLessonModel(BaseModel):
    """AdaptedLesson database model - Personalized content for students."""

    __tablename__ = "adapted_lessons"

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Adaptation metadata
    lesson_title = Column(String(255), nullable=False)
    adaptation_style = Column(String(255), nullable=True)

    # Content blocks stored as JSON
    content_blocks = Column(JSON, default=[], nullable=False)

    # Status
    status = Column(
        Enum(AdaptedLessonStatus),
        default=AdaptedLessonStatus.PENDING,
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # AI generation metadata
    ai_model_used = Column(String(100), nullable=True)
    generation_prompt_hash = Column(String(64), nullable=True)
    generation_duration_ms = Column(Integer, nullable=True)

    # Interaction stats
    view_count = Column(Integer, default=0, nullable=False)
    completion_count = Column(Integer, default=0, nullable=False)
    average_time_spent_seconds = Column(Integer, default=0, nullable=False)

    # Relationships
    lesson = relationship("LessonModel", back_populates="adapted_lessons")

    # Unique constraint on lesson_id + student_id
    __table_args__ = (
        {"postgresql_partition_by": None},  # Placeholder for future partitioning
    )

    def __repr__(self) -> str:
        return f"<AdaptedLesson(id={self.id}, lesson_id={self.lesson_id}, student_id={self.student_id})>"
