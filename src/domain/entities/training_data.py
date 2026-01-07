"""Training data log entity for AI model improvement."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class TrainingDataLog:
    """
    TrainingDataLog entity for capturing AI training data.

    Stores input/output pairs with teacher corrections for RLHF.
    Used to fine-tune the Small Language Model (SLM).
    """

    source_id: UUID  # FK to AdaptedLesson or NeuroProfile
    source_type: str  # "adapted_lesson" or "neuro_profile"
    id: UUID = field(default_factory=uuid4)

    # AI interaction data
    input_context: Dict[str, Any] = field(default_factory=dict)  # Prompt/data sent to AI
    model_output: Dict[str, Any] = field(default_factory=dict)  # What AI produced
    human_correction: Optional[Dict[str, Any]] = None  # Teacher's edit

    # Model information
    model_name: str = ""
    model_version: str = ""
    prompt_template_version: str = ""

    # Quality metrics
    metric_score: Optional[float] = None  # Implicit feedback (time spent, completion)
    quality_rating: Optional[int] = None  # Explicit rating 1-5
    was_accepted: bool = True  # Whether output was used without changes

    # Correction metadata
    corrected_by_user_id: Optional[UUID] = None
    correction_type: Optional[str] = None  # "content", "structure", "style"
    correction_notes: Optional[str] = None

    # Processing status
    is_processed: bool = False  # Has been used in training
    processed_at: Optional[datetime] = None
    training_batch_id: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_correction(
        self,
        correction: Dict[str, Any],
        user_id: UUID,
        correction_type: str = "content",
        notes: Optional[str] = None,
    ) -> None:
        """Add a human correction to this training sample."""
        self.human_correction = correction
        self.corrected_by_user_id = user_id
        self.correction_type = correction_type
        self.correction_notes = notes
        self.was_accepted = False

    def add_implicit_feedback(self, score: float) -> None:
        """Add implicit feedback metric (e.g., engagement score)."""
        self.metric_score = score

    def add_explicit_rating(self, rating: int) -> None:
        """Add explicit quality rating."""
        self.quality_rating = max(1, min(5, rating))

    def mark_processed(self, batch_id: str) -> None:
        """Mark as processed for training."""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        self.training_batch_id = batch_id

    def to_training_format(self) -> Dict[str, Any]:
        """
        Convert to format suitable for model fine-tuning.

        Returns (input, bad_output, good_output) triplet if correction exists,
        or (input, good_output) pair if accepted.
        """
        if self.human_correction and not self.was_accepted:
            return {
                "input": self.input_context,
                "rejected": self.model_output,
                "chosen": self.human_correction,
                "correction_type": self.correction_type,
            }
        else:
            return {
                "input": self.input_context,
                "output": self.model_output,
                "quality_score": self.metric_score or self.quality_rating,
            }

    @property
    def has_correction(self) -> bool:
        """Check if this sample has a human correction."""
        return self.human_correction is not None
