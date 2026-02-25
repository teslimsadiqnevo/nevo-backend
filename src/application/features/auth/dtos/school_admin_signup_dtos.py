"""School admin sign-up DTOs."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class SchoolAdminSignUpInput:
    """Input DTO for school admin workspace setup."""

    full_name: str
    school_name: str
    email: str
    password: str
    school_address: Optional[str] = None
    school_city: Optional[str] = None
    school_state: Optional[str] = None


@dataclass
class SchoolAdminSignUpOutput:
    """Output DTO for school admin workspace setup."""

    access_token: str
    refresh_token: str
    user_id: UUID
    email: str
    name: str
    school_id: UUID
    school_name: str
