"""Unit of Work pattern interface."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.interfaces.repositories import (
        IUserRepository,
        ISchoolRepository,
        ILessonRepository,
        IAdaptedLessonRepository,
        INeuroProfileRepository,
        IAssessmentRepository,
        IProgressRepository,
        ITrainingDataRepository,
        ITeacherFeedbackRepository,
        IChatMessageRepository,
        IConnectionRepository,
    )


class IUnitOfWork(ABC):
    """Unit of Work interface for managing transactions."""

    users: "IUserRepository"
    schools: "ISchoolRepository"
    lessons: "ILessonRepository"
    adapted_lessons: "IAdaptedLessonRepository"
    neuro_profiles: "INeuroProfileRepository"
    assessments: "IAssessmentRepository"
    progress: "IProgressRepository"
    training_data: "ITrainingDataRepository"
    teacher_feedbacks: "ITeacherFeedbackRepository"
    chat_messages: "IChatMessageRepository"
    connections: "IConnectionRepository"

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enter the context manager."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        pass
