"""StudentProgress database model."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from src.infrastructure.database.models.base import BaseModel


class StudentProgressModel(BaseModel):
    """StudentProgress database model."""

    __tablename__ = "student_progress"

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Lesson progress stored as JSON (keyed by lesson_id)
    lesson_progress = Column(JSON, default=dict, nullable=False)

    # Skill progress stored as JSON (keyed by skill_name)
    skill_progress = Column(JSON, default=dict, nullable=False)

    # Overall stats
    total_lessons_completed = Column(Integer, default=0, nullable=False)
    total_time_spent_seconds = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)
    current_streak_days = Column(Integer, default=0, nullable=False)
    longest_streak_days = Column(Integer, default=0, nullable=False)

    # Activity tracking
    last_activity_at = Column(DateTime, nullable=True)
    last_lesson_id = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    student = relationship("UserModel", back_populates="progress")

    def __repr__(self) -> str:
        return f"<StudentProgress(id={self.id}, student_id={self.student_id})>"
