"""Authentication data transfer objects."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.core.config.constants import UserRole


@dataclass(frozen=True)
class LoginInput:
    """Input DTO for login."""

    email: str
    password: str


@dataclass
class LoginOutput:
    """Output DTO for login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID = None
    email: str = ""
    role: UserRole = UserRole.STUDENT
    name: str = ""
    school_id: Optional[UUID] = None


@dataclass(frozen=True)
class RegisterInput:
    """Input DTO for user registration."""

    email: str
    password: str
    first_name: str
    last_name: str
    role: UserRole
    school_id: Optional[UUID] = None
    phone_number: Optional[str] = None


@dataclass
class RegisterOutput:
    """Output DTO for registration."""

    user_id: UUID
    email: str
    role: UserRole
    message: str = "Registration successful"


@dataclass(frozen=True)
class RefreshTokenInput:
    """Input DTO for token refresh."""

    refresh_token: str


@dataclass
class RefreshTokenOutput:
    """Output DTO for token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True)
class ChangePasswordInput:
    """Input DTO for password change."""

    user_id: UUID
    current_password: str
    new_password: str


@dataclass(frozen=True)
class ForgotPasswordInput:
    """Input DTO for forgot password."""

    email: str


@dataclass(frozen=True)
class ResetPasswordInput:
    """Input DTO for password reset."""

    reset_token: str
    new_password: str
