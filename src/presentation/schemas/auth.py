"""Authentication schemas with OpenAPI examples."""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.core.config.constants import UserRole


class LoginRequest(BaseModel):
    """Login request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "password": "securepassword123"
            }
        }
    )

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["student@example.com"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
        examples=["securepassword123"]
    )


class LoginResponse(BaseModel):
    """Login response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA1MzI0MjAwfQ.xxx",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNTkyODAwMH0.yyy",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@example.com",
                    "role": "student",
                    "name": "John Doe",
                    "school_id": "550e8400-e29b-41d4-a716-446655440001"
                }
            }
        }
    )

    token: str = Field(..., description="JWT access token (expires in 30 minutes)")
    refresh_token: str = Field(..., description="JWT refresh token (expires in 7 days)")
    user: Dict[str, Any] = Field(..., description="User information including id, email, role, name, school_id")


class RegisterRequest(BaseModel):
    """Registration request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newstudent@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "role": "student",
                "school_id": "550e8400-e29b-41d4-a716-446655440001",
                "phone_number": "+2341234567890"
            }
        }
    )

    email: EmailStr = Field(
        ...,
        description="User email address (must be unique)",
        examples=["newstudent@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepassword123"]
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's first name",
        examples=["John"]
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's last name",
        examples=["Doe"]
    )
    age: Optional[int] = Field(
        None,
        ge=5,
        le=120,
        description="User's age (optional, typically for students)",
        examples=[10]
    )
    role: UserRole = Field(
        ...,
        description="User role: student, teacher, school_admin, parent, or super_admin"
    )
    school_id: Optional[UUID] = Field(
        None,
        description="School ID (required for student, teacher, school_admin roles)"
    )
    phone_number: Optional[str] = Field(
        None,
        description="Phone number with country code",
        examples=["+2341234567890"]
    )


class RegisterResponse(BaseModel):
    """Registration response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "newstudent@example.com",
                "role": "student",
                "message": "User registered successfully"
            }
        }
    )

    user_id: str = Field(..., description="Created user's UUID")
    email: str = Field(..., description="User's email address")
    role: str = Field(..., description="User's assigned role")
    message: str = Field(..., description="Success message")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNTkyODAwMH0.yyy"
            }
        }
    )

    refresh_token: str = Field(
        ...,
        description="Valid refresh token from login response"
    )


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA1MzI0MjAwfQ.xxx",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNTkyODAwMH0.yyy"
            }
        }
    )

    token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")


class NevoIdLoginRequest(BaseModel):
    """Nevo ID login request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nevo_id": "NEVO-7K3P2",
                "pin": "1234"
            }
        }
    )

    nevo_id: str = Field(
        ...,
        pattern=r"^NEVO-[23456789A-HJ-NP-Z]{5}$",
        description="Student's Nevo ID (format: NEVO-XXXXX)",
        examples=["NEVO-7K3P2"]
    )
    pin: str = Field(
        ...,
        pattern=r"^\d{4}$",
        description="4-digit PIN",
        examples=["1234"]
    )


class SetPinRequest(BaseModel):
    """Set PIN request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pin": "1234"
            }
        }
    )

    pin: str = Field(
        ...,
        pattern=r"^\d{4}$",
        description="4-digit PIN (numbers only)",
        examples=["1234"]
    )


class SetPinResponse(BaseModel):
    """Set PIN response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "PIN set successfully",
                "nevo_id": "NEVO-7K3P2"
            }
        }
    )

    success: bool = Field(..., description="Whether PIN was set successfully")
    message: str = Field(..., description="Status message")
    nevo_id: Optional[str] = Field(None, description="Student's Nevo ID")


class TeacherSignUpRequest(BaseModel):
    """Teacher sign-up request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Sarah Jenkins",
                "school_name": "Lincoln High School",
                "email": "sarah@school.edu",
                "password": "securepass123",
            }
        }
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Teacher's full name",
        examples=["Sarah Jenkins"],
    )
    school_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="School name (existing or new)",
        examples=["Lincoln High School"],
    )
    email: EmailStr = Field(
        ...,
        description="Work email address",
        examples=["sarah@school.edu"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepass123"],
    )


class TeacherSignUpResponse(BaseModel):
    """Teacher sign-up response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJ...",
                "refresh_token": "eyJ...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "sarah@school.edu",
                    "role": "teacher",
                    "name": "Sarah Jenkins",
                    "school_id": "550e8400-e29b-41d4-a716-446655440001",
                    "school_name": "Lincoln High School",
                },
                "class_code": "NEVO-CLASS-4K7",
            }
        }
    )

    token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: Dict[str, Any] = Field(..., description="Teacher info")
    class_code: str = Field(..., description="Auto-generated class code for student connections")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "teacher@school.edu"
            }
        }
    )

    email: EmailStr = Field(
        ...,
        description="Email address associated with the account",
        examples=["teacher@school.edu"],
    )


class ForgotPasswordResponse(BaseModel):
    """Forgot password response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "If an account with this email exists, a password reset link has been sent."
            }
        }
    )

    message: str = Field(..., description="Status message")


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reset_token": "eyJ...",
                "new_password": "newSecurePass123"
            }
        }
    )

    reset_token: str = Field(
        ...,
        description="Password reset token from email link",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)",
        examples=["newSecurePass123"],
    )


class ResetPasswordResponse(BaseModel):
    """Reset password response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password has been reset successfully. You can now log in."
            }
        }
    )

    message: str = Field(..., description="Status message")


class SchoolAdminSignUpRequest(BaseModel):
    """School admin workspace setup request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Adaobi Okafor",
                "school_name": "Greenfield Academy",
                "email": "admin@greenfield.edu.ng",
                "password": "securepass123",
                "school_address": "12 Education Lane",
                "school_city": "Lagos",
                "school_state": "Lagos",
            }
        }
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Admin's full name",
        examples=["Adaobi Okafor"],
    )
    school_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the school to create",
        examples=["Greenfield Academy"],
    )
    email: EmailStr = Field(
        ...,
        description="Admin email address",
        examples=["admin@greenfield.edu.ng"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepass123"],
    )
    school_address: Optional[str] = Field(
        None,
        max_length=500,
        description="School address (optional)",
        examples=["12 Education Lane"],
    )
    school_city: Optional[str] = Field(
        None,
        max_length=100,
        description="City (optional)",
        examples=["Lagos"],
    )
    school_state: Optional[str] = Field(
        None,
        max_length=100,
        description="State (optional)",
        examples=["Lagos"],
    )


class SchoolAdminSignUpResponse(BaseModel):
    """School admin workspace setup response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJ...",
                "refresh_token": "eyJ...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "admin@greenfield.edu.ng",
                    "role": "school_admin",
                    "name": "Adaobi Okafor",
                    "school_id": "550e8400-e29b-41d4-a716-446655440001",
                    "school_name": "Greenfield Academy",
                },
            }
        }
    )

    token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: Dict[str, Any] = Field(..., description="Admin info")
