"""Assessment data transfer objects."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.core.config.constants import AssessmentStatus


@dataclass
class QuestionDTO:
    """DTO for an assessment question."""

    id: int
    text: str
    type: str
    category: str
    options: List[str] = field(default_factory=list)
    scale_min: int = 1
    scale_max: int = 5
    is_required: bool = True
    order: int = 0


@dataclass
class GetQuestionsOutput:
    """Output DTO for getting assessment questions."""

    questions: List[QuestionDTO]
    total_questions: int
    categories: List[str]


@dataclass
class AnswerInput:
    """Input for a single answer."""

    question_id: int
    value: Any


@dataclass(frozen=True)
class SubmitAssessmentInput:
    """Input DTO for submitting assessment answers."""

    student_id: UUID
    answers: List[Dict[str, Any]]


@dataclass
class SubmitAssessmentOutput:
    """Output DTO for assessment submission."""

    status: str
    message: str
    assessment_id: Optional[UUID] = None
    profile_id: Optional[UUID] = None
    nevo_id: Optional[str] = None


@dataclass
class AssessmentStatusOutput:
    """Output DTO for assessment status check."""

    status: AssessmentStatus
    progress_percentage: float
    current_question: int
    total_questions: int
    completed_at: Optional[str] = None
    profile_generated: bool = False
