"""TrainingDataLog database model."""

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID

from src.infrastructure.database.models.base import BaseModel


class TrainingDataLogModel(BaseModel):
    """TrainingDataLog database model for AI training data collection."""

    __tablename__ = "training_data_logs"

    source_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_type = Column(String(50), nullable=False, index=True)

    # AI interaction data
    input_context = Column(JSON, default={}, nullable=False)
    model_output = Column(JSON, default={}, nullable=False)
    human_correction = Column(JSON, nullable=True)

    # Model information
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    prompt_template_version = Column(String(50), nullable=True)

    # Quality metrics
    metric_score = Column(Float, nullable=True)
    quality_rating = Column(Integer, nullable=True)
    was_accepted = Column(Boolean, default=True, nullable=False)

    # Correction metadata
    corrected_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    correction_type = Column(String(50), nullable=True)
    correction_notes = Column(String(1000), nullable=True)

    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    training_batch_id = Column(String(100), nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<TrainingDataLog(id={self.id}, source_type={self.source_type})>"
