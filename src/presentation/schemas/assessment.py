"""Assessment schemas with OpenAPI examples."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class QuestionSchema(BaseModel):
    """Assessment question schema."""

    id: int = Field(..., description="Question ID", examples=[1])
    text: str = Field(..., description="Question text", examples=["How do you prefer to learn new things?"])
    type: str = Field(..., description="Question type: SINGLE_CHOICE, MULTIPLE_CHOICE, SCALE", examples=["SINGLE_CHOICE"])
    category: str = Field(..., description="Question category", examples=["learning_style"])
    options: List[str] = Field(
        default=[],
        description="Available options for choice questions",
        examples=[["Watching videos", "Listening to explanations", "Doing hands-on activities", "Reading and writing"]]
    )
    scale_min: int = Field(default=1, description="Minimum value for SCALE type", examples=[1])
    scale_max: int = Field(default=5, description="Maximum value for SCALE type", examples=[5])
    is_required: bool = Field(default=True, description="Whether the question must be answered")


class AssessmentQuestionsResponse(BaseModel):
    """Assessment questions response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "questions": [
                    {
                        "id": 1,
                        "text": "How do you prefer to learn new things?",
                        "type": "SINGLE_CHOICE",
                        "category": "learning_style",
                        "options": [
                            "Watching videos or looking at pictures",
                            "Listening to explanations",
                            "Doing hands-on activities",
                            "Reading and writing notes"
                        ],
                        "scale_min": 1,
                        "scale_max": 5,
                        "is_required": True
                    },
                    {
                        "id": 2,
                        "text": "Which of these things bother you when learning? (Select all that apply)",
                        "type": "MULTIPLE_CHOICE",
                        "category": "sensory_triggers",
                        "options": [
                            "Loud sounds",
                            "Bright or flashing lights",
                            "Crowded or busy visuals",
                            "Fast-changing content",
                            "None of these"
                        ],
                        "is_required": True
                    },
                    {
                        "id": 3,
                        "text": "How confident do you feel when trying something new?",
                        "type": "SCALE",
                        "category": "confidence",
                        "options": [],
                        "scale_min": 1,
                        "scale_max": 5,
                        "is_required": True
                    }
                ],
                "total_questions": 8,
                "categories": [
                    "learning_style",
                    "sensory_triggers",
                    "attention_span",
                    "complexity_preference",
                    "interests",
                    "reading_level",
                    "confidence"
                ]
            }
        }
    )

    questions: List[QuestionSchema] = Field(..., description="List of assessment questions")
    total_questions: int = Field(..., description="Total number of questions")
    categories: List[str] = Field(..., description="Question categories for grouping in UI")


class AnswerSchema(BaseModel):
    """Single answer schema."""

    question_id: int = Field(..., description="Question ID being answered", examples=[1])
    value: Any = Field(
        ...,
        description="Answer value - string for SINGLE_CHOICE, list for MULTIPLE_CHOICE, int for SCALE",
        examples=["Watching videos or looking at pictures"]
    )


class SubmitAssessmentRequest(BaseModel):
    """Submit assessment request schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answers": [
                    {"question_id": 1, "value": "Watching videos or looking at pictures"},
                    {"question_id": 2, "value": ["Loud sounds", "Bright or flashing lights"]},
                    {"question_id": 3, "value": "10-20 minutes"},
                    {"question_id": 4, "value": "medium"},
                    {"question_id": 5, "value": ["science", "art", "music"]},
                    {"question_id": 6, "value": "grade_3_5"},
                    {"question_id": 7, "value": 4},
                    {"question_id": 8, "value": 3}
                ]
            }
        }
    )

    answers: List[Dict[str, Any]] = Field(
        ...,
        description="List of answers with question_id and value for each question"
    )


class SubmitAssessmentResponse(BaseModel):
    """Submit assessment response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "message": "Assessment completed and profile generated successfully",
                "assessment_id": "550e8400-e29b-41d4-a716-446655440001",
                "profile_id": "550e8400-e29b-41d4-a716-446655440002"
            }
        }
    )

    status: str = Field(
        ...,
        description="Processing status: completed, processing, or failed",
        examples=["completed"]
    )
    message: str = Field(
        ...,
        description="Status message with details",
        examples=["Assessment completed and profile generated successfully"]
    )
    assessment_id: Optional[str] = Field(
        None,
        description="Created assessment UUID"
    )
    profile_id: Optional[str] = Field(
        None,
        description="Generated NeuroProfile UUID (available when status is 'completed')"
    )
