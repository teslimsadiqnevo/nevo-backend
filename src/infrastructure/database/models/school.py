"""School database model."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.infrastructure.database.models.base import BaseModel


class SchoolModel(BaseModel):
    """School database model."""

    __tablename__ = "schools"

    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Nigeria", nullable=False)
    postal_code = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(2048), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(String(50), default="free", nullable=False)
    max_teachers = Column(Integer, default=5, nullable=False)
    max_students = Column(Integer, default=100, nullable=False)
    teacher_count = Column(Integer, default=0, nullable=False)
    student_count = Column(Integer, default=0, nullable=False)

    # Relationships
    users = relationship("UserModel", back_populates="school")
    lessons = relationship("LessonModel", back_populates="school")

    def __repr__(self) -> str:
        return f"<School(id={self.id}, name={self.name})>"
