"""Teacher data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class TeacherOutput:
    """Output DTO for teacher data."""

    id: UUID
    email: str
    first_name: str
    last_name: str
    school_id: Optional[UUID]
    school_name: Optional[str]
    is_active: bool
    created_at: datetime
    lesson_count: int = 0
    student_count: int = 0


@dataclass
class StudentSummary:
    """Summary of student progress for teacher dashboard."""

    student_id: UUID
    student_name: str
    lessons_completed: int
    average_score: float
    last_activity: Optional[datetime]
    needs_attention: bool = False


@dataclass
class TeacherDashboardOutput:
    """Output DTO for teacher dashboard."""

    teacher_id: UUID
    teacher_name: str
    total_students: int
    total_lessons: int
    active_students_today: int
    average_class_score: float
    students_needing_attention: int
    recent_students: List[StudentSummary] = field(default_factory=list)
    lesson_engagement_rate: float = 0.0


@dataclass
class TeacherHomeOutput:
    """Output DTO for teacher home dashboard cards."""

    teacher_name: str
    total_classes: int
    total_lessons_assigned: int
    students_needing_help: int
    total_students: int
    total_lessons: int
    published_lessons: int
    draft_lessons: int


@dataclass
class AssignableStudentOutput:
    """Output DTO for a student that can be assigned a lesson."""

    id: UUID
    first_name: str
    last_name: str
    email: str


@dataclass(frozen=True)
class AssignLessonInput:
    """Input DTO for assigning a lesson."""

    lesson_id: UUID
    teacher_id: UUID
    target: str  # "class" or "individual"
    student_ids: List[UUID] = field(default_factory=list)


@dataclass
class AssignLessonOutput:
    """Output DTO for lesson assignment result."""

    lesson_id: UUID
    assigned_count: int
    skipped_count: int
    message: str
