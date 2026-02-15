"""TeacherFeedback database model."""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.database.models.base import BaseModel


class TeacherFeedbackModel(BaseModel):
    """TeacherFeedback database model - Teacher encouragement messages."""

    __tablename__ = "teacher_feedbacks"

    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
    message = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<TeacherFeedback(id={self.id}, teacher={self.teacher_id}, student={self.student_id})>"
