"""Lesson-related domain events."""

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class LessonCreated(DomainEvent):
    """Event raised when a new lesson is created."""

    lesson_id: UUID = field(default=None)
    teacher_id: UUID = field(default=None)
    school_id: UUID = field(default=None)
    title: str = ""


@dataclass
class LessonPublished(DomainEvent):
    """Event raised when a lesson is published."""

    lesson_id: UUID = field(default=None)
    teacher_id: UUID = field(default=None)


@dataclass
class LessonAdapted(DomainEvent):
    """Event raised when a lesson is adapted for a student."""

    lesson_id: UUID = field(default=None)
    student_id: UUID = field(default=None)
    adapted_lesson_id: UUID = field(default=None)
    ai_model_used: str = ""
    generation_time_ms: int = 0
