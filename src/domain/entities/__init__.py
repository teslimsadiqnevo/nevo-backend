"""Domain entities - Core business objects."""

from src.domain.entities.base import Entity, AggregateRoot
from src.domain.entities.user import User
from src.domain.entities.school import School
from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.entities.lesson import Lesson
from src.domain.entities.adapted_lesson import AdaptedLesson, ContentBlock
from src.domain.entities.assessment import Assessment, AssessmentQuestion, AssessmentAnswer
from src.domain.entities.progress import StudentProgress
from src.domain.entities.training_data import TrainingDataLog

__all__ = [
    "Entity",
    "AggregateRoot",
    "User",
    "School",
    "NeuroProfile",
    "Lesson",
    "AdaptedLesson",
    "ContentBlock",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentAnswer",
    "StudentProgress",
    "TrainingDataLog",
]
