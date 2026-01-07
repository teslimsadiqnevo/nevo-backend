"""Lesson schemas with OpenAPI examples."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CreateLessonRequest(BaseModel):
    """Create lesson request schema (used with multipart/form-data)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Introduction to Photosynthesis",
                "content": "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen. This amazing process happens in the chloroplasts of plant cells...",
                "description": "Learn how plants make their own food using sunlight",
                "subject": "Science",
                "topic": "Biology - Plants",
                "target_grade_level": 5,
                "tags": ["biology", "plants", "photosynthesis"]
            }
        }
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Lesson title",
        examples=["Introduction to Photosynthesis"]
    )
    content: str = Field(
        ...,
        description="Full lesson text content that will be adapted by AI",
        examples=["Photosynthesis is the process by which plants convert sunlight..."]
    )
    description: Optional[str] = Field(
        None,
        description="Short lesson description for preview",
        examples=["Learn how plants make their own food using sunlight"]
    )
    subject: Optional[str] = Field(
        None,
        description="Subject area",
        examples=["Science", "Mathematics", "English", "History"]
    )
    topic: Optional[str] = Field(
        None,
        description="Specific topic within the subject",
        examples=["Biology - Plants"]
    )
    target_grade_level: int = Field(
        default=3,
        ge=1,
        le=12,
        description="Target grade level (1-12)",
        examples=[5]
    )
    tags: List[str] = Field(
        default=[],
        description="Tags for categorization and search",
        examples=[["biology", "plants", "photosynthesis"]]
    )


class CreateLessonResponse(BaseModel):
    """Create lesson response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lesson_id": "550e8400-e29b-41d4-a716-446655440003",
                "status": "draft",
                "message": "Lesson uploaded successfully"
            }
        }
    )

    lesson_id: str = Field(..., description="Created lesson UUID")
    status: str = Field(..., description="Lesson status: draft, published, or archived")
    message: str = Field(default="Lesson uploaded successfully", description="Status message")


class LessonSchema(BaseModel):
    """Lesson schema for list responses."""

    id: str
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    target_grade_level: int
    estimated_duration_minutes: int
    status: str
    created_at: Optional[str] = None


class LessonResponse(BaseModel):
    """Single lesson response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "title": "Introduction to Photosynthesis",
                "description": "Learn how plants make their own food using sunlight",
                "subject": "Science",
                "topic": "Biology - Plants",
                "target_grade_level": 5,
                "estimated_duration_minutes": 15,
                "status": "published",
                "media_url": "https://nevo-lessons.s3.amazonaws.com/lessons/image.jpg",
                "teacher_id": "550e8400-e29b-41d4-a716-446655440004",
                "teacher_name": "Jane Smith",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )

    id: str
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    target_grade_level: int
    estimated_duration_minutes: int
    status: str
    media_url: Optional[str] = None
    teacher_id: str
    teacher_name: Optional[str] = None
    created_at: Optional[str] = None


class LessonListResponse(BaseModel):
    """Lesson list response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lessons": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "title": "Introduction to Photosynthesis",
                        "description": "Learn how plants make their own food",
                        "subject": "Science",
                        "topic": "Biology - Plants",
                        "target_grade_level": 5,
                        "estimated_duration_minutes": 15,
                        "status": "published",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 25,
                "page": 1,
                "page_size": 20,
                "total_pages": 2
            }
        }
    )

    lessons: List[Dict[str, Any]] = Field(..., description="List of lessons")
    total: int = Field(..., description="Total count of lessons matching filter")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ContentBlockSchema(BaseModel):
    """Content block schema for adapted lessons."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "block_1",
                "type": "text",
                "content": "Plants are amazing! They can make their own food using just sunlight, water, and air.",
                "order": 0,
                "emphasis": ["sunlight", "water", "air"],
                "ai_generated_url": None,
                "question": None,
                "options": [],
                "correct_index": None
            }
        }
    )

    id: str = Field(..., description="Unique block identifier")
    type: str = Field(
        ...,
        description="Block type: heading, text, image, image_prompt, quiz, activity, summary"
    )
    content: str = Field(..., description="Block content (text, heading, or description)")
    order: int = Field(default=0, description="Display order (0-indexed)")
    emphasis: List[str] = Field(default=[], description="Words/phrases to emphasize in UI")
    ai_generated_url: Optional[str] = Field(None, description="URL if image was generated")
    question: Optional[str] = Field(None, description="Quiz question (for quiz type)")
    options: List[str] = Field(default=[], description="Quiz options (for quiz type)")
    correct_index: Optional[int] = Field(None, description="Correct answer index (for quiz type)")


class PlayLessonResponse(BaseModel):
    """Play lesson response schema (adapted content) - THE CORE AI FEATURE."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lesson_title": "Introduction to Photosynthesis",
                "adaptation_style": "Visual learning style with medium complexity, chunked for 15-minute attention span. Avoiding: loud_sounds, bright_lights",
                "blocks": [
                    {
                        "id": "block_1",
                        "type": "heading",
                        "content": "How Plants Make Food",
                        "order": 0
                    },
                    {
                        "id": "block_2",
                        "type": "image_prompt",
                        "content": "A colorful, friendly diagram showing a smiling plant with arrows: yellow sunlight coming from above, blue water droplets coming from roots, and small CO2 molecules floating in. Green glucose molecules and O2 bubbles coming out.",
                        "order": 1
                    },
                    {
                        "id": "block_3",
                        "type": "text",
                        "content": "Plants are amazing! They can make their own food using just **sunlight**, **water**, and **air**. This special process is called **photosynthesis** (say it: foto-SIN-thuh-sis).",
                        "order": 2,
                        "emphasis": ["sunlight", "water", "air", "photosynthesis"]
                    },
                    {
                        "id": "block_4",
                        "type": "activity",
                        "content": "Draw a plant and use arrows to show: 1) Where sunlight enters (leaves) 2) Where water comes from (roots) 3) Where food is made (leaves)",
                        "order": 3
                    },
                    {
                        "id": "block_5",
                        "type": "quiz",
                        "content": "Quick Check!",
                        "question": "What three things do plants need to make food?",
                        "options": [
                            "Sunlight, water, and air",
                            "Soil, fertilizer, and rain",
                            "Seeds, dirt, and sunshine",
                            "Nothing - plants don't need food"
                        ],
                        "correct_index": 0,
                        "order": 4
                    },
                    {
                        "id": "block_6",
                        "type": "summary",
                        "content": "**Key Takeaway**: Plants use sunlight + water + air to make their own food through a process called photosynthesis!",
                        "order": 5
                    }
                ],
                "adapted_lesson_id": "550e8400-e29b-41d4-a716-446655440005",
                "original_lesson_id": "550e8400-e29b-41d4-a716-446655440003"
            }
        }
    )

    lesson_title: str = Field(..., description="Original lesson title")
    adaptation_style: str = Field(
        ...,
        description="Description of how the content was adapted (learning style, complexity, etc.)"
    )
    blocks: List[Dict[str, Any]] = Field(
        ...,
        description="Ordered list of content blocks to render. See ContentBlockSchema for structure."
    )
    adapted_lesson_id: str = Field(..., description="UUID of the adapted lesson (for progress tracking)")
    original_lesson_id: str = Field(..., description="UUID of the original lesson")


class SubmitFeedbackRequest(BaseModel):
    """Submit feedback request schema for AI training."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "adapted_lesson_id": "550e8400-e29b-41d4-a716-446655440005",
                "block_id": "block_3",
                "correction": "Plants are amazing! They create their own food using **sunlight**, **water**, and **carbon dioxide** from the air. This special process is called **photosynthesis** (say it: foto-SIN-thuh-sis).",
                "correction_type": "content",
                "notes": "Added 'carbon dioxide' for scientific accuracy"
            }
        }
    )

    adapted_lesson_id: UUID = Field(..., description="UUID of the adapted lesson being corrected")
    block_id: str = Field(..., description="ID of the content block being corrected")
    correction: str = Field(..., description="The corrected content")
    correction_type: str = Field(
        default="content",
        description="Type of correction: content, complexity, accuracy, formatting"
    )
    notes: Optional[str] = Field(None, description="Optional notes explaining the correction")
