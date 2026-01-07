"""Lesson data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass(frozen=True)
class CreateLessonInput:
    """Input DTO for creating a lesson."""

    teacher_id: UUID
    title: str
    original_text_content: str
    description: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    target_grade_level: int = 3
    estimated_duration_minutes: int = 30
    tags: List[str] = field(default_factory=list)
    media_url: Optional[str] = None
    media_type: Optional[str] = None


@dataclass
class CreateLessonOutput:
    """Output DTO for lesson creation."""

    lesson_id: UUID
    status: str
    message: str = "Lesson uploaded successfully"


@dataclass
class LessonOutput:
    """Output DTO for a single lesson."""

    id: UUID
    title: str
    description: Optional[str]
    subject: Optional[str]
    topic: Optional[str]
    target_grade_level: int
    estimated_duration_minutes: int
    status: str
    media_url: Optional[str]
    media_type: Optional[str]
    tags: List[str]
    teacher_id: UUID
    teacher_name: Optional[str] = None
    created_at: Optional[datetime] = None
    view_count: int = 0
    adaptation_count: int = 0


@dataclass
class LessonListOutput:
    """Output DTO for lesson list."""

    lessons: List[LessonOutput]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class ContentBlockOutput:
    """Output DTO for a content block."""

    id: str
    type: str
    content: str
    order: int
    emphasis: List[str] = field(default_factory=list)
    ai_generated_url: Optional[str] = None
    question: Optional[str] = None
    options: List[str] = field(default_factory=list)
    correct_index: Optional[int] = None


@dataclass
class PlayLessonOutput:
    """Output DTO for playing a lesson (adapted content)."""

    lesson_title: str
    adaptation_style: str
    blocks: List[Dict[str, Any]]
    adapted_lesson_id: UUID
    original_lesson_id: UUID
    student_id: UUID


@dataclass(frozen=True)
class SubmitFeedbackInput:
    """Input DTO for teacher feedback on adapted content."""

    lesson_id: UUID
    adapted_lesson_id: UUID
    block_id: str
    teacher_id: UUID
    correction: str
    correction_type: str = "content"  # content, structure, style
    notes: Optional[str] = None
