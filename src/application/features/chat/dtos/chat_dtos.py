"""Chat data transfer objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True)
class AskNevoInput:
    """Input DTO for asking Nevo a question."""

    student_id: UUID
    message: str
    lesson_id: Optional[UUID] = None


@dataclass
class AskNevoOutput:
    """Output DTO for Nevo's response."""

    response: str
    message_id: UUID


@dataclass
class ChatMessageOutput:
    """Output DTO for a single chat message."""

    id: UUID
    role: str
    content: str
    created_at: datetime


@dataclass
class ChatHistoryOutput:
    """Output DTO for chat history."""

    messages: List[ChatMessageOutput]
