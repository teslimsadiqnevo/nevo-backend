"""Waitlist entry entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class WaitlistEntry:
    """WaitlistEntry entity for pre-launch signups."""

    name: str
    email: str
    role: str  # student, teacher, parent, school_admin
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
