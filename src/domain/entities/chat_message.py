"""ChatMessage entity - Conversation messages between student and Nevo AI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ChatMessage:
    """
    ChatMessage entity for student-Nevo AI conversations.

    Stores both student questions and Nevo's AI responses.
    """

    student_id: UUID
    role: str  # "student" or "nevo"
    content: str
    id: UUID = field(default_factory=uuid4)
    lesson_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
