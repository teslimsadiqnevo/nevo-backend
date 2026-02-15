"""Student data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class StudentOutput:
    """Output DTO for student data."""

    id: UUID
    email: str
    first_name: str
    last_name: str
    school_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    has_profile: bool = False
    assessment_completed: bool = False
    lessons_completed: int = 0
    last_activity_at: Optional[datetime] = None


@dataclass
class StudentListOutput:
    """Output DTO for student list."""

    students: List[StudentOutput]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class StudentProfileOutput:
    """Output DTO for student's neuro profile."""

    student_id: UUID
    student_name: str
    learning_style: str
    reading_level: str
    complexity_tolerance: str
    attention_span_minutes: int
    sensory_triggers: List[str]
    interests: List[str]
    profile_version: int
    last_updated: datetime


@dataclass(frozen=True)
class AddStudentInput:
    """Input DTO for adding a student to teacher/school."""

    email: str
    first_name: str
    last_name: str
    school_id: UUID
    teacher_id: Optional[UUID] = None
    password: Optional[str] = None


@dataclass
class CurrentLessonOutput:
    """Output DTO for the current lesson card on the dashboard."""

    lesson_id: UUID
    title: str
    subject: Optional[str]
    topic: Optional[str]
    current_step: int
    total_steps: int


@dataclass
class RecentFeedbackOutput:
    """Output DTO for a recent teacher feedback item."""

    message: str
    teacher_name: str
    created_at: datetime


@dataclass
class DashboardStatsOutput:
    """Output DTO for dashboard statistics."""

    total_lessons_completed: int
    current_streak_days: int
    average_score: float


@dataclass
class StudentDashboardOutput:
    """Output DTO for the student home dashboard."""

    student_name: str
    current_lesson: Optional[CurrentLessonOutput]
    recent_feedback: List[RecentFeedbackOutput]
    stats: DashboardStatsOutput
    attention_span_minutes: int


@dataclass(frozen=True)
class SendFeedbackInput:
    """Input DTO for sending teacher feedback."""

    teacher_id: UUID
    student_id: UUID
    message: str
    lesson_id: Optional[UUID] = None


@dataclass
class SendFeedbackOutput:
    """Output DTO for send feedback result."""

    feedback_id: UUID
    message: str
