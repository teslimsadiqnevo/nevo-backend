"""Assessment entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.core.config.constants import AssessmentStatus, QuestionType


@dataclass
class AssessmentQuestion:
    """A single assessment question."""

    text: str
    question_type: QuestionType
    id: int = 0  # Numeric ID for simplicity in assessment flow
    category: str = "general"  # learning_style, sensory, interests, etc.
    options: List[str] = field(default_factory=list)
    scale_min: int = 1
    scale_max: int = 5
    is_required: bool = True
    order: int = 0

    # Metadata for AI processing
    maps_to_attribute: Optional[str] = None  # Which profile attribute this affects
    weight: float = 1.0  # Weight for scoring

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "id": self.id,
            "text": self.text,
            "type": self.question_type.value,
            "category": self.category,
            "is_required": self.is_required,
            "order": self.order,
        }

        if self.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_CHOICE]:
            result["options"] = self.options
        elif self.question_type == QuestionType.SCALE:
            result["scale_min"] = self.scale_min
            result["scale_max"] = self.scale_max

        return result


@dataclass
class AssessmentAnswer:
    """A student's answer to an assessment question."""

    question_id: int
    value: Any  # Can be string, int, list depending on question type
    id: UUID = field(default_factory=uuid4)
    answered_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "value": self.value,
        }


@dataclass
class Assessment:
    """
    Assessment entity representing a student's onboarding assessment.

    Contains the answers that generate the NeuroProfile.
    """

    student_id: UUID
    id: UUID = field(default_factory=uuid4)

    # Status tracking
    status: AssessmentStatus = AssessmentStatus.NOT_STARTED

    # Answers
    answers: List[AssessmentAnswer] = field(default_factory=list)
    answers_json: List[Dict[str, Any]] = field(default_factory=list)

    # Progress tracking
    current_question_index: int = 0
    total_questions: int = 0

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Generated profile reference
    generated_profile_id: Optional[UUID] = None

    def start(self, total_questions: int) -> None:
        """Start the assessment."""
        self.status = AssessmentStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.total_questions = total_questions
        self.updated_at = datetime.utcnow()

    def add_answer(self, question_id: int, value: Any) -> None:
        """Add an answer to the assessment."""
        answer = AssessmentAnswer(question_id=question_id, value=value)
        self.answers.append(answer)
        self.answers_json.append(answer.to_dict())
        self.current_question_index += 1
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark assessment as completed."""
        self.status = AssessmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_processing(self) -> None:
        """Mark assessment as being processed by AI."""
        self.status = AssessmentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def get_raw_data(self) -> Dict[str, Any]:
        """Get raw assessment data for AI processing."""
        return {
            "student_id": str(self.student_id),
            "answers": self.answers_json,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.current_question_index / self.total_questions) * 100

    @property
    def is_complete(self) -> bool:
        return self.status == AssessmentStatus.COMPLETED
