"""NeuroProfile database model."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import ComplexityTolerance, LearningStyle, ReadingLevel
from src.infrastructure.database.models.base import BaseModel


class NeuroProfileModel(BaseModel):
    """NeuroProfile database model - The AI context for personalization."""

    __tablename__ = "neuro_profiles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Assessment data
    assessment_raw_data = Column(JSON, default=dict, nullable=False)

    # Generated profile attributes
    learning_style = Column(
        Enum(LearningStyle),
        default=LearningStyle.VISUAL,
        nullable=False,
    )
    reading_level = Column(
        Enum(ReadingLevel),
        default=ReadingLevel.GRADE_3,
        nullable=False,
    )
    complexity_tolerance = Column(
        Enum(ComplexityTolerance),
        default=ComplexityTolerance.MEDIUM,
        nullable=False,
    )
    attention_span_minutes = Column(Integer, default=15, nullable=False)

    # Sensory triggers stored as JSON array of strings
    sensory_triggers = Column(JSON, default=list, nullable=False)

    # Interests and preferences
    interests = Column(ARRAY(String), default=list, nullable=True)
    preferred_subjects = Column(ARRAY(String), default=list, nullable=True)

    # Full generated profile from AI
    generated_profile = Column(JSON, default=dict, nullable=False)

    # Confidence scores
    confidence_scores = Column(JSON, default=dict, nullable=False)

    # Last updated and version
    last_updated = Column(DateTime, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="neuro_profile")

    def __repr__(self) -> str:
        return f"<NeuroProfile(id={self.id}, user_id={self.user_id})>"
