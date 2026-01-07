"""Teacher schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TeacherDashboardResponse(BaseModel):
    """Teacher dashboard response schema."""

    teacher_id: str = Field(..., description="Teacher ID")
    teacher_name: str = Field(..., description="Teacher name")
    total_students: int = Field(..., description="Total students")
    total_lessons: int = Field(..., description="Total lessons created")
    active_students_today: int = Field(..., description="Students active today")
    average_class_score: float = Field(..., description="Average class score")
    students_needing_attention: int = Field(..., description="Students needing attention")
    lesson_engagement_rate: float = Field(default=0.0, description="Lesson engagement rate")


class StudentSummarySchema(BaseModel):
    """Student summary for teacher view."""

    id: str
    email: str
    first_name: str
    last_name: str
    has_profile: bool
    lessons_completed: int
    average_score: float
    last_activity_at: Optional[str] = None


class StudentListResponse(BaseModel):
    """Student list response schema."""

    students: List[Dict[str, Any]] = Field(..., description="List of students")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")
