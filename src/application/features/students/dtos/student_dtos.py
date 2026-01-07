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
