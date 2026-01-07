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
