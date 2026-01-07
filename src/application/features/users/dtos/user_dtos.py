"""User data transfer objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class UserOutput:
    """Output DTO for user data."""

    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    school_id: Optional[UUID]
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime]


@dataclass(frozen=True)
class UserUpdateInput:
    """Input DTO for updating user."""

    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
