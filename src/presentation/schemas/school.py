"""School schemas with OpenAPI examples."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CreateSchoolRequest(BaseModel):
    """Create school request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Lagos International School",
                "address": "123 Victoria Island",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "phone_number": "+234-1-234-5678",
                "email": "admin@lagosintl.edu.ng"
            }
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="School name",
        examples=["Lagos International School"]
    )
    address: Optional[str] = Field(
        None,
        description="School street address",
        examples=["123 Victoria Island"]
    )
    city: Optional[str] = Field(
        None,
        description="City",
        examples=["Lagos"]
    )
    state: Optional[str] = Field(
        None,
        description="State or Province",
        examples=["Lagos"]
    )
    country: str = Field(
        default="Nigeria",
        description="Country",
        examples=["Nigeria"]
    )
    phone_number: Optional[str] = Field(
        None,
        description="School phone number",
        examples=["+234-1-234-5678"]
    )
    email: Optional[EmailStr] = Field(
        None,
        description="School administrative email",
        examples=["admin@lagosintl.edu.ng"]
    )


class SchoolResponse(BaseModel):
    """School response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "name": "Lagos International School",
                "address": "123 Victoria Island",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "is_active": True,
                "teacher_count": 15,
                "student_count": 250,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )

    id: str = Field(..., description="School UUID")
    name: str = Field(..., description="School name")
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    is_active: bool = Field(..., description="Whether school is active")
    teacher_count: int = Field(..., description="Number of registered teachers")
    student_count: int = Field(..., description="Number of registered students")
    created_at: str = Field(..., description="ISO timestamp of creation")


class SchoolDashboardResponse(BaseModel):
    """School dashboard response schema for school admins."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "school_id": "550e8400-e29b-41d4-a716-446655440006",
                "school_name": "Lagos International School",
                "total_teachers": 15,
                "total_students": 250,
                "total_lessons": 45,
                "active_students_today": 180,
                "average_school_score": 78.5,
                "students_completed_assessment": 230,
                "lessons_delivered_today": 320
            }
        }
    )

    school_id: str = Field(..., description="School UUID")
    school_name: str = Field(..., description="School name")
    total_teachers: int = Field(..., description="Total registered teachers")
    total_students: int = Field(..., description="Total registered students")
    total_lessons: int = Field(..., description="Total lessons uploaded by teachers")
    active_students_today: int = Field(..., description="Students who accessed the platform today")
    average_school_score: float = Field(..., description="Average quiz score across all students")
    students_completed_assessment: int = Field(..., description="Students with completed assessments/profiles")
    lessons_delivered_today: int = Field(..., description="Lesson views today")


class TeacherSummarySchema(BaseModel):
    """Teacher summary for school view."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440007",
                "email": "jane.smith@school.edu",
                "first_name": "Jane",
                "last_name": "Smith",
                "lesson_count": 12,
                "created_at": "2024-01-10T09:00:00Z"
            }
        }
    )

    id: str = Field(..., description="Teacher UUID")
    email: str = Field(..., description="Teacher email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    lesson_count: int = Field(..., description="Number of lessons created")
    created_at: str = Field(..., description="ISO timestamp of registration")


class TeacherListResponse(BaseModel):
    """Teacher list response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "teachers": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440007",
                        "email": "jane.smith@school.edu",
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "lesson_count": 12,
                        "created_at": "2024-01-10T09:00:00Z"
                    },
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440008",
                        "email": "john.doe@school.edu",
                        "first_name": "John",
                        "last_name": "Doe",
                        "lesson_count": 8,
                        "created_at": "2024-01-12T14:00:00Z"
                    }
                ],
                "total": 15,
                "page": 1,
                "page_size": 20,
                "total_pages": 1
            }
        }
    )

    teachers: List[Dict[str, Any]] = Field(..., description="List of teachers")
    total: int = Field(..., description="Total count of teachers")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
