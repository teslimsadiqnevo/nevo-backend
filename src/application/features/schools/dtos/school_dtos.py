"""School data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True)
class CreateSchoolInput:
    """Input DTO for creating a school."""

    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Nigeria"
    phone_number: Optional[str] = None
    email: Optional[str] = None


@dataclass
class SchoolOutput:
    """Output DTO for school data."""

    id: UUID
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: str
    phone_number: Optional[str]
    email: Optional[str]
    is_active: bool
    teacher_count: int
    student_count: int
    created_at: datetime


@dataclass
class TeacherSummary:
    """Summary of teacher for school dashboard."""

    teacher_id: UUID
    teacher_name: str
    student_count: int
    lesson_count: int
    active_students: int


@dataclass
class SchoolDashboardOutput:
    """Output DTO for school admin dashboard."""

    school_id: UUID
    school_name: str
    total_teachers: int
    total_students: int
    total_lessons: int
    active_students_today: int
    average_school_score: float
    teachers: List[TeacherSummary] = field(default_factory=list)
    students_completed_assessment: int = 0
    lessons_delivered_today: int = 0
