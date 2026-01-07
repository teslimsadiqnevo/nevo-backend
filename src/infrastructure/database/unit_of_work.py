"""Unit of Work implementation."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.unit_of_work import IUnitOfWork
from src.infrastructure.database.repositories import (
    UserRepository,
    SchoolRepository,
    LessonRepository,
    AdaptedLessonRepository,
    NeuroProfileRepository,
    AssessmentRepository,
    ProgressRepository,
    TrainingDataRepository,
)


class UnitOfWork(IUnitOfWork):
    """Unit of Work implementation for managing database transactions."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> "UnitOfWork":
        """Enter the context manager and initialize repositories."""
        self.users = UserRepository(self._session)
        self.schools = SchoolRepository(self._session)
        self.lessons = LessonRepository(self._session)
        self.adapted_lessons = AdaptedLessonRepository(self._session)
        self.neuro_profiles = NeuroProfileRepository(self._session)
        self.assessments = AssessmentRepository(self._session)
        self.progress = ProgressRepository(self._session)
        self.training_data = TrainingDataRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        """Commit the transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self._session.rollback()
