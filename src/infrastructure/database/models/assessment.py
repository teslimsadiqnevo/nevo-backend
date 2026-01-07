"""Assessment database model."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import AssessmentStatus
from src.infrastructure.database.models.base import BaseModel


class AssessmentModel(BaseModel):
    """Assessment database model."""

    __tablename__ = "assessments"

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Status
    status = Column(
        Enum(AssessmentStatus),
        default=AssessmentStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )

    # Answers stored as JSON
    answers = Column(JSON, default=[], nullable=False)

    # Progress tracking
    current_question_index = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Generated profile reference
    generated_profile_id = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    student = relationship("UserModel", back_populates="assessments")

    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, student_id={self.student_id}, status={self.status})>"
