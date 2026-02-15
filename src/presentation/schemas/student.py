"""Student schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StudentProfileResponse(BaseModel):
    """Student profile response schema."""

    student_id: str = Field(..., description="Student ID")
    student_name: str = Field(..., description="Student name")
    learning_style: str = Field(..., description="Learning style preference")
    reading_level: str = Field(..., description="Reading level")
    complexity_tolerance: str = Field(..., description="Complexity tolerance")
    attention_span_minutes: int = Field(..., description="Attention span in minutes")
    sensory_triggers: List[str] = Field(..., description="Sensory triggers to avoid")
    interests: List[str] = Field(..., description="Student interests")
    profile_version: int = Field(..., description="Profile version number")
    last_updated: str = Field(..., description="Last update timestamp")


class LessonProgressSchema(BaseModel):
    """Lesson progress schema."""

    lesson_id: str
    lesson_title: str
    status: str
    progress_percentage: float
    score: Optional[float] = None


class SkillProgressSchema(BaseModel):
    """Skill progress schema."""

    skill_name: str
    mastery_level: float
    lessons_completed: int


class StudentProgressResponse(BaseModel):
    """Student progress response schema."""

    student_id: str = Field(..., description="Student ID")
    student_name: str = Field(..., description="Student name")
    total_lessons_completed: int = Field(..., description="Total lessons completed")
    total_time_spent_minutes: int = Field(..., description="Total time spent learning")
    average_score: float = Field(..., description="Average score")
    current_streak_days: int = Field(..., description="Current learning streak")
    longest_streak_days: int = Field(..., description="Longest learning streak")
    last_activity_at: Optional[str] = Field(None, description="Last activity timestamp")
    lessons: List[Dict[str, Any]] = Field(..., description="Lesson progress list")
    skills: List[Dict[str, Any]] = Field(..., description="Skill progress list")


class CurrentLessonSchema(BaseModel):
    """Current lesson card schema."""

    lesson_id: str
    title: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    current_step: int
    total_steps: int


class RecentFeedbackSchema(BaseModel):
    """Recent teacher feedback schema."""

    message: str
    teacher_name: str
    created_at: str


class DashboardStatsSchema(BaseModel):
    """Dashboard statistics schema."""

    total_lessons_completed: int
    current_streak_days: int
    average_score: float


class StudentDashboardResponse(BaseModel):
    """Student home dashboard response."""

    student_name: str = Field(..., description="Student's first name")
    current_lesson: Optional[CurrentLessonSchema] = Field(
        None, description="Current/last lesson in progress"
    )
    recent_feedback: List[RecentFeedbackSchema] = Field(
        ..., description="Recent teacher feedback messages"
    )
    stats: DashboardStatsSchema = Field(..., description="Learning statistics")
    attention_span_minutes: int = Field(
        ..., description="Recommended break timer duration"
    )


class SendFeedbackRequest(BaseModel):
    """Send feedback request schema."""

    student_id: str = Field(..., description="Target student ID")
    message: str = Field(..., min_length=1, max_length=500, description="Feedback message")
    lesson_id: Optional[str] = Field(None, description="Related lesson ID (optional)")


class SendFeedbackResponse(BaseModel):
    """Send feedback response schema."""

    feedback_id: str = Field(..., description="Created feedback ID")
    message: str = Field(..., description="Status message")
