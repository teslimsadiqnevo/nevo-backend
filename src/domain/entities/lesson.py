"""Lesson entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.core.config.constants import LessonStatus


@dataclass
class Lesson:
    """
    Lesson entity representing original teacher-uploaded content.

    This is the source material that gets adapted for each student.
    """

    title: str
    teacher_id: UUID
    id: UUID = field(default_factory=uuid4)
    school_id: Optional[UUID] = None

    # Content
    description: Optional[str] = None
    original_text_content: str = ""
    media_url: Optional[str] = None
    media_type: Optional[str] = None  # pdf, video, worksheet

    # Metadata
    subject: Optional[str] = None
    topic: Optional[str] = None
    target_grade_level: int = 3
    estimated_duration_minutes: int = 30

    # Tags for categorization
    tags: List[str] = field(default_factory=list)

    # Status
    status: LessonStatus = LessonStatus.DRAFT

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

    # Stats
    view_count: int = 0
    adaptation_count: int = 0

    def publish(self) -> None:
        """Publish the lesson."""
        self.status = LessonStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the lesson."""
        self.status = LessonStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def increment_adaptation_count(self) -> None:
        """Increment adaptation count."""
        self.adaptation_count += 1
        self.updated_at = datetime.utcnow()

    @property
    def is_published(self) -> bool:
        return self.status == LessonStatus.PUBLISHED

    @property
    def has_media(self) -> bool:
        return bool(self.media_url)
