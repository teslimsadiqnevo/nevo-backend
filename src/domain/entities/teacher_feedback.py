"""TeacherFeedback entity - Teacher encouragement messages to students."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class TeacherFeedback:
    """
    TeacherFeedback entity for teacher-to-student encouragement messages.

    These appear on the student's Home dashboard as motivational messages.
    """

    teacher_id: UUID
    student_id: UUID
    message: str
    id: UUID = field(default_factory=uuid4)
    lesson_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
