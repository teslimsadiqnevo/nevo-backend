"""Lesson assignment entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.core.config.constants import AssignmentStatus, AssignmentTarget


@dataclass
class LessonAssignment:
    """
    Lesson assignment entity.

    Tracks when a teacher assigns a lesson to a student,
    either as part of a class-wide assignment or individually.
    """

    lesson_id: UUID
    student_id: UUID
    teacher_id: UUID
    assignment_type: AssignmentTarget = AssignmentTarget.CLASS
    status: AssignmentStatus = AssignmentStatus.ASSIGNED
    id: UUID = field(default_factory=uuid4)
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def start(self) -> None:
        """Mark assignment as started."""
        self.status = AssignmentStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark assignment as completed."""
        self.status = AssignmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
