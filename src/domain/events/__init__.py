"""Domain events - Events for cross-aggregate communication."""

from src.domain.events.base import DomainEvent
from src.domain.events.user_events import (
    UserCreated,
    UserVerified,
    UserLoggedIn,
)
from src.domain.events.assessment_events import (
    AssessmentStarted,
    AssessmentCompleted,
    ProfileGenerated,
)
from src.domain.events.lesson_events import (
    LessonCreated,
    LessonPublished,
    LessonAdapted,
)

__all__ = [
    "DomainEvent",
    "UserCreated",
    "UserVerified",
    "UserLoggedIn",
    "AssessmentStarted",
    "AssessmentCompleted",
    "ProfileGenerated",
    "LessonCreated",
    "LessonPublished",
    "LessonAdapted",
]
