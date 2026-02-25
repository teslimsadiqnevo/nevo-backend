"""Teacher sign-up data transfer objects."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class TeacherSignUpInput:
    """Input DTO for teacher sign-up."""

    full_name: str
    school_name: str
    email: str
    password: str


@dataclass
class TeacherSignUpOutput:
    """Output DTO for teacher sign-up."""

    access_token: str
    refresh_token: str
    user_id: UUID
    email: str
    name: str
    school_id: UUID
    school_name: str
    class_code: str
