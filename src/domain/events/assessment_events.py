"""Assessment-related domain events."""

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class AssessmentStarted(DomainEvent):
    """Event raised when a student starts an assessment."""

    student_id: UUID = field(default=None)
    assessment_id: UUID = field(default=None)
    total_questions: int = 0


@dataclass
class AssessmentCompleted(DomainEvent):
    """Event raised when a student completes an assessment."""

    student_id: UUID = field(default=None)
    assessment_id: UUID = field(default=None)
    duration_seconds: int = 0


@dataclass
class ProfileGenerated(DomainEvent):
    """Event raised when a student profile is generated from assessment."""

    student_id: UUID = field(default=None)
    profile_id: UUID = field(default=None)
    assessment_id: UUID = field(default=None)
    ai_model_used: str = ""
