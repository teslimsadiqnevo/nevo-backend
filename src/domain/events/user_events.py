"""User-related domain events."""

from dataclasses import dataclass, field
from uuid import UUID

from src.core.config.constants import UserRole
from src.domain.events.base import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    """Event raised when a new user is created."""

    user_id: UUID = field(default=None)
    email: str = ""
    role: UserRole = UserRole.STUDENT
    school_id: UUID = field(default=None)


@dataclass
class UserVerified(DomainEvent):
    """Event raised when a user verifies their email."""

    user_id: UUID = field(default=None)
    email: str = ""


@dataclass
class UserLoggedIn(DomainEvent):
    """Event raised when a user logs in."""

    user_id: UUID = field(default=None)
    email: str = ""
    ip_address: str = ""
    user_agent: str = ""
