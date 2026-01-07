"""User entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.core.config.constants import UserRole


@dataclass
class User:
    """User entity representing all user types in the system."""

    email: str
    password_hash: str
    role: UserRole
    first_name: str
    last_name: str
    id: UUID = field(default_factory=uuid4)
    school_id: Optional[UUID] = None
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    # For parents - linked student IDs
    linked_student_ids: list[UUID] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER

    @property
    def is_school_admin(self) -> bool:
        return self.role == UserRole.SCHOOL_ADMIN

    @property
    def is_parent(self) -> bool:
        return self.role == UserRole.PARENT

    def can_access_student(self, student_id: UUID) -> bool:
        """Check if user can access a specific student's data."""
        if self.role == UserRole.SUPER_ADMIN:
            return True
        if self.role == UserRole.PARENT:
            return student_id in self.linked_student_ids
        return False

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
