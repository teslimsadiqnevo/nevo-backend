"""Domain interfaces - Repository and service contracts."""

from src.domain.interfaces.repositories import (
    IUserRepository,
    ISchoolRepository,
    ILessonRepository,
    IAdaptedLessonRepository,
    INeuroProfileRepository,
    IAssessmentRepository,
    IProgressRepository,
    ITrainingDataRepository,
)
from src.domain.interfaces.services import (
    IAIService,
    IStorageService,
    IEmailService,
    ICacheService,
)

__all__ = [
    # Repositories
    "IUserRepository",
    "ISchoolRepository",
    "ILessonRepository",
    "IAdaptedLessonRepository",
    "INeuroProfileRepository",
    "IAssessmentRepository",
    "IProgressRepository",
    "ITrainingDataRepository",
    # Services
    "IAIService",
    "IStorageService",
    "IEmailService",
    "ICacheService",
]
