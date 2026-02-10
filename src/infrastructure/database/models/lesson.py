"""Lesson database model."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import LessonStatus
from src.infrastructure.database.models.base import BaseModel


class LessonModel(BaseModel):
    """Lesson database model - Original teacher content."""

    __tablename__ = "lessons"

    title = Column(String(255), nullable=False)
    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    school_id = Column(
        UUID(as_uuid=True),
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Content
    description = Column(Text, nullable=True)
    original_text_content = Column(Text, nullable=False)
    media_url = Column(String(2048), nullable=True)
    media_type = Column(String(50), nullable=True)

    # Metadata
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    target_grade_level = Column(Integer, default=3, nullable=False)
    estimated_duration_minutes = Column(Integer, default=30, nullable=False)

    # Tags
    tags = Column(ARRAY(String), default=list, nullable=True)

    # Status
    status = Column(Enum(LessonStatus), default=LessonStatus.DRAFT, nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)

    # Stats
    view_count = Column(Integer, default=0, nullable=False)
    adaptation_count = Column(Integer, default=0, nullable=False)

    # Relationships
    teacher = relationship("UserModel", back_populates="lessons")
    school = relationship("SchoolModel", back_populates="lessons")
    adapted_lessons = relationship("AdaptedLessonModel", back_populates="lesson")

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title={self.title})>"
