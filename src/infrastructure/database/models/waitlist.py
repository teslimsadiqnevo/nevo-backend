"""Waitlist database model."""

from sqlalchemy import Column, String

from src.infrastructure.database.models.base import BaseModel


class WaitlistModel(BaseModel):
    """Waitlist database model for pre-launch signups."""

    __tablename__ = "waitlist"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(String(50), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Waitlist(id={self.id}, email={self.email}, role={self.role})>"
