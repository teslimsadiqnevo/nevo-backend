"""Progress tracking schemas with OpenAPI examples."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class UpdateProgressRequest(BaseModel):
    """Update progress request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
                "blocks_completed": 4,
                "time_spent_seconds": 480,
                "quiz_score": 85.5,
                "is_completed": False
            }
        }
    )

    lesson_id: UUID = Field(
        ...,
        description="UUID of the lesson being tracked"
    )
    blocks_completed: int = Field(
        ...,
        ge=0,
        description="Number of content blocks the student has viewed/completed",
        examples=[4]
    )
    time_spent_seconds: int = Field(
        ...,
        ge=0,
        description="Total time spent on this lesson in seconds",
        examples=[480]
    )
    quiz_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Quiz score as percentage (0-100). Only include when quiz is answered.",
        examples=[85.5]
    )
    is_completed: bool = Field(
        default=False,
        description="Set to true when student finishes the lesson"
    )


class UpdateProgressResponse(BaseModel):
    """Update progress response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "updated",
                "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
                "is_completed": False,
            }
        }
    )

    status: str = Field(..., description="Status: 'updated'")
    lesson_id: str = Field(..., description="UUID of the lesson whose progress was updated")
    is_completed: bool = Field(..., description="Whether the lesson is now marked as completed")


class StudentProgressSummary(BaseModel):
    """Student progress summary schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_lessons_started": 15,
                "total_lessons_completed": 12,
                "total_time_spent_seconds": 14400,
                "average_quiz_score": 82.5,
                "current_streak": 5,
                "longest_streak": 12,
                "last_activity": "2024-01-15T10:30:00Z",
                "recent_lessons": [
                    {
                        "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
                        "lesson_title": "Introduction to Photosynthesis",
                        "completion_percentage": 100,
                        "quiz_score": 90,
                        "completed_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }
    )

    student_id: str = Field(..., description="Student UUID")
    total_lessons_started: int = Field(..., description="Number of lessons started")
    total_lessons_completed: int = Field(..., description="Number of lessons completed")
    total_time_spent_seconds: int = Field(..., description="Total learning time in seconds")
    average_quiz_score: float = Field(..., description="Average quiz score percentage")
    current_streak: int = Field(..., description="Current consecutive learning days")
    longest_streak: int = Field(..., description="Longest streak achieved")
    last_activity: Optional[str] = Field(None, description="ISO timestamp of last activity")
    recent_lessons: list = Field(default=[], description="Recent lesson progress")
