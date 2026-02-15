"""Chat schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class AskNevoRequest(BaseModel):
    """Ask Nevo request schema."""

    message: str = Field(
        ..., min_length=1, max_length=1000, description="Student's question"
    )
    lesson_id: Optional[str] = Field(
        None, description="Current lesson ID for context (optional)"
    )


class AskNevoResponse(BaseModel):
    """Ask Nevo response schema."""

    response: str = Field(..., description="Nevo's response")
    message_id: str = Field(..., description="Saved message ID")


class ChatMessageSchema(BaseModel):
    """Chat message schema."""

    id: str
    role: str = Field(..., description="'student' or 'nevo'")
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Chat history response schema."""

    messages: List[ChatMessageSchema] = Field(
        ..., description="Chat messages in chronological order"
    )
