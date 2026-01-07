"""User database model."""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from src.core.config.constants import UserRole
from src.infrastructure.database.models.base import BaseModel


class UserModel(BaseModel):
    """User database model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(2048), nullable=True)
    phone_number = Column(String(20), nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    # For parents - linked student IDs stored as array
    linked_student_ids = Column(ARRAY(UUID(as_uuid=True)), default=[], nullable=True)

    # Relationships
    school = relationship("SchoolModel", back_populates="users")
    neuro_profile = relationship("NeuroProfileModel", back_populates="user", uselist=False)
    lessons = relationship("LessonModel", back_populates="teacher")
    assessments = relationship("AssessmentModel", back_populates="student")
    progress = relationship("StudentProgressModel", back_populates="student", uselist=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
