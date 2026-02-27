"""Lesson assignment database model."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import AssignmentStatus, AssignmentTarget
from src.infrastructure.database.models.base import BaseModel


class LessonAssignmentModel(BaseModel):
    """Lesson assignment database model."""

    __tablename__ = "lesson_assignments"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student"),
    )

    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_type = Column(
        Enum(AssignmentTarget, name="assignment_target"),
        nullable=False,
        default=AssignmentTarget.CLASS,
    )
    status = Column(
        Enum(AssignmentStatus, name="assignment_status"),
        nullable=False,
        default=AssignmentStatus.ASSIGNED,
        index=True,
    )
    assigned_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    lesson = relationship("LessonModel", backref="assignments")
    student = relationship("UserModel", foreign_keys=[student_id])
    teacher = relationship("UserModel", foreign_keys=[teacher_id])

    def __repr__(self) -> str:
        return f"<LessonAssignment(id={self.id}, lesson={self.lesson_id}, student={self.student_id})>"
