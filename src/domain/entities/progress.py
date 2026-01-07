"""Student progress entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.core.config.constants import ProgressStatus


@dataclass
class LessonProgress:
    """Progress for a single lesson."""

    lesson_id: UUID
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: int = 0
    score: Optional[float] = None  # Quiz score if applicable
    blocks_completed: int = 0
    total_blocks: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lesson_id": str(self.lesson_id),
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_spent_seconds": self.time_spent_seconds,
            "score": self.score,
            "progress_percentage": self.progress_percentage,
        }

    @property
    def progress_percentage(self) -> float:
        if self.total_blocks == 0:
            return 0.0
        return (self.blocks_completed / self.total_blocks) * 100


@dataclass
class SkillProgress:
    """Progress for a skill area."""

    skill_name: str
    mastery_level: float = 0.0  # 0-100
    lessons_completed: int = 0
    total_lessons: int = 0
    average_score: float = 0.0
    last_activity_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "mastery_level": self.mastery_level,
            "lessons_completed": self.lessons_completed,
            "total_lessons": self.total_lessons,
            "average_score": self.average_score,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
        }


@dataclass
class StudentProgress:
    """
    StudentProgress entity tracking overall student learning progress.

    Aggregates progress across lessons and skill areas.
    """

    student_id: UUID
    id: UUID = field(default_factory=uuid4)

    # Lesson progress
    lesson_progress: Dict[str, LessonProgress] = field(default_factory=dict)

    # Skill progress
    skill_progress: Dict[str, SkillProgress] = field(default_factory=dict)

    # Overall stats
    total_lessons_completed: int = 0
    total_time_spent_seconds: int = 0
    average_score: float = 0.0
    current_streak_days: int = 0
    longest_streak_days: int = 0

    # Activity tracking
    last_activity_at: Optional[datetime] = None
    last_lesson_id: Optional[UUID] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def start_lesson(self, lesson_id: UUID, total_blocks: int) -> None:
        """Record starting a lesson."""
        lesson_key = str(lesson_id)
        if lesson_key not in self.lesson_progress:
            self.lesson_progress[lesson_key] = LessonProgress(
                lesson_id=lesson_id,
                total_blocks=total_blocks,
            )

        progress = self.lesson_progress[lesson_key]
        progress.status = ProgressStatus.IN_PROGRESS
        progress.started_at = datetime.utcnow()

        self.last_activity_at = datetime.utcnow()
        self.last_lesson_id = lesson_id
        self.updated_at = datetime.utcnow()

    def update_lesson_progress(
        self,
        lesson_id: UUID,
        blocks_completed: int,
        time_spent_seconds: int,
    ) -> None:
        """Update progress on a lesson."""
        lesson_key = str(lesson_id)
        if lesson_key not in self.lesson_progress:
            return

        progress = self.lesson_progress[lesson_key]
        progress.blocks_completed = blocks_completed
        progress.time_spent_seconds += time_spent_seconds

        self.total_time_spent_seconds += time_spent_seconds
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete_lesson(
        self,
        lesson_id: UUID,
        score: Optional[float] = None,
        skill_name: Optional[str] = None,
    ) -> None:
        """Mark a lesson as completed."""
        lesson_key = str(lesson_id)
        if lesson_key not in self.lesson_progress:
            return

        progress = self.lesson_progress[lesson_key]
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = datetime.utcnow()
        progress.score = score
        progress.blocks_completed = progress.total_blocks

        self.total_lessons_completed += 1
        self._update_average_score(score)
        self._update_streak()

        if skill_name:
            self._update_skill_progress(skill_name, score)

        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def _update_average_score(self, score: Optional[float]) -> None:
        """Update overall average score."""
        if score is None:
            return

        if self.total_lessons_completed == 1:
            self.average_score = score
        else:
            total = self.average_score * (self.total_lessons_completed - 1)
            self.average_score = (total + score) / self.total_lessons_completed

    def _update_streak(self) -> None:
        """Update activity streak."""
        # Simplified streak logic - can be enhanced
        self.current_streak_days += 1
        if self.current_streak_days > self.longest_streak_days:
            self.longest_streak_days = self.current_streak_days

    def _update_skill_progress(self, skill_name: str, score: Optional[float]) -> None:
        """Update skill progress after lesson completion."""
        if skill_name not in self.skill_progress:
            self.skill_progress[skill_name] = SkillProgress(skill_name=skill_name)

        skill = self.skill_progress[skill_name]
        skill.lessons_completed += 1
        skill.last_activity_at = datetime.utcnow()

        if score is not None:
            total = skill.average_score * (skill.lessons_completed - 1)
            skill.average_score = (total + score) / skill.lessons_completed
            skill.mastery_level = min(100, skill.average_score)

    def get_lesson_progress(self, lesson_id: UUID) -> Optional[LessonProgress]:
        """Get progress for a specific lesson."""
        return self.lesson_progress.get(str(lesson_id))

    def to_summary_dict(self) -> Dict[str, Any]:
        """Get progress summary for API response."""
        return {
            "student_id": str(self.student_id),
            "total_lessons_completed": self.total_lessons_completed,
            "total_time_spent_minutes": self.total_time_spent_seconds // 60,
            "average_score": round(self.average_score, 1),
            "current_streak_days": self.current_streak_days,
            "longest_streak_days": self.longest_streak_days,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "skills": [s.to_dict() for s in self.skill_progress.values()],
        }
