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


class TeacherHomeResponse(BaseModel):
    """Teacher home dashboard cards response."""

    teacher_name: str = Field(..., description="Teacher's full name")
    total_classes: int = Field(..., description="Number of classes")
    total_lessons_assigned: int = Field(..., description="Total lessons assigned to students")
    students_needing_help: int = Field(..., description="Students needing help")
    total_students: int = Field(..., description="Total connected students")
    total_lessons: int = Field(..., description="Total lessons created")
    published_lessons: int = Field(..., description="Published lesson count")
    draft_lessons: int = Field(..., description="Draft lesson count")


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


class AssignableStudentSchema(BaseModel):
    """Student that can be assigned a lesson."""

    id: str
    first_name: str
    last_name: str
    email: str


class AssignableStudentsResponse(BaseModel):
    """Response for assignable students list."""

    students: List[AssignableStudentSchema] = Field(..., description="Assignable students")
    total: int = Field(..., description="Total count")


class AssignLessonRequest(BaseModel):
    """Request to assign a lesson to students."""

    target: str = Field(
        ...,
        description="Assignment target: 'class' (all connected students) or 'individual'",
    )
    student_ids: List[str] = Field(
        default=[],
        description="Student UUIDs (required if target is 'individual')",
    )


class AssignLessonResponse(BaseModel):
    """Response for lesson assignment."""

    lesson_id: str = Field(..., description="Assigned lesson ID")
    assigned_count: int = Field(..., description="Number of students assigned")
    skipped_count: int = Field(..., description="Number of students skipped (already assigned)")
    message: str = Field(..., description="Status message")


class PublishLessonResponse(BaseModel):
    """Response for publishing a lesson."""

    lesson_id: str = Field(..., description="Published lesson ID")
    status: str = Field(..., description="New status")
    message: str = Field(..., description="Status message")


class TeacherLessonSchema(BaseModel):
    """Lesson item in teacher's lesson management view."""

    id: str
    title: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    status: str
    target_grade_level: int
    estimated_duration_minutes: int
    created_at: str
    published_at: Optional[str] = None
    assignment_count: int = 0


class TeacherLessonListResponse(BaseModel):
    """Response for teacher lesson list with filtering."""

    lessons: List[TeacherLessonSchema] = Field(..., description="Lessons")
    total: int = Field(..., description="Total count matching filters")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")
