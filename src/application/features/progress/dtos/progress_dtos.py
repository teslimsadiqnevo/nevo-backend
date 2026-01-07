"""Progress data transfer objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class LessonProgressOutput:
    """Output DTO for lesson progress."""

    lesson_id: UUID
    lesson_title: str
    status: str
    progress_percentage: float
    time_spent_minutes: int
    score: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


@dataclass
class SkillProgressOutput:
    """Output DTO for skill progress."""

    skill_name: str
    mastery_level: float
    lessons_completed: int
    total_lessons: int
    average_score: float


@dataclass
class StudentProgressOutput:
    """Output DTO for student progress summary."""

    student_id: UUID
    student_name: str
    total_lessons_completed: int
    total_time_spent_minutes: int
    average_score: float
    current_streak_days: int
    longest_streak_days: int
    last_activity_at: Optional[datetime]
    lessons: List[LessonProgressOutput] = field(default_factory=list)
    skills: List[SkillProgressOutput] = field(default_factory=list)


@dataclass(frozen=True)
class UpdateProgressInput:
    """Input DTO for updating progress."""

    student_id: UUID
    lesson_id: UUID
    blocks_completed: int
    time_spent_seconds: int
    quiz_score: Optional[float] = None
    is_completed: bool = False


@dataclass
class ProgressSummaryOutput:
    """Output DTO for aggregated progress (teacher/school view)."""

    total_students: int
    active_students: int
    average_completion_rate: float
    average_score: float
    total_lessons_completed: int
    students_by_progress: Dict[str, int] = field(default_factory=dict)
    top_performing_students: List[Dict[str, Any]] = field(default_factory=list)
    struggling_students: List[Dict[str, Any]] = field(default_factory=list)
