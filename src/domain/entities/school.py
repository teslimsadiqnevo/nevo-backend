"""School entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class School:
    """School entity representing educational institutions."""

    name: str
    id: UUID = field(default_factory=uuid4)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Nigeria"
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    subscription_tier: str = "free"  # free, basic, premium
    max_teachers: int = 5
    max_students: int = 100
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Aggregate counts (denormalized for performance)
    teacher_count: int = 0
    student_count: int = 0

    def can_add_teacher(self) -> bool:
        """Check if school can add more teachers."""
        return self.teacher_count < self.max_teachers

    def can_add_student(self) -> bool:
        """Check if school can add more students."""
        return self.student_count < self.max_students

    def increment_teacher_count(self) -> None:
        """Increment teacher count."""
        self.teacher_count += 1
        self.updated_at = datetime.utcnow()

    def increment_student_count(self) -> None:
        """Increment student count."""
        self.student_count += 1
        self.updated_at = datetime.utcnow()
