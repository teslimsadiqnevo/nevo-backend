"""Repository interfaces - Data access contracts."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.core.config.constants import UserRole
from src.domain.entities.user import User
from src.domain.entities.school import School
from src.domain.entities.lesson import Lesson
from src.domain.entities.adapted_lesson import AdaptedLesson
from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.entities.assessment import Assessment
from src.domain.entities.progress import StudentProgress
from src.domain.entities.training_data import TrainingDataLog
from src.domain.entities.teacher_feedback import TeacherFeedback
from src.domain.entities.chat_message import ChatMessage
from src.domain.entities.connection import Connection
from src.core.config.constants import ConnectionStatus
from src.domain.value_objects.pagination import PaginationParams, PaginatedResult


class IUserRepository(ABC):
    """User repository interface."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        pass

    @abstractmethod
    async def list_by_school(
        self,
        school_id: UUID,
        role: Optional[UserRole] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[User]:
        """List users by school."""
        pass

    @abstractmethod
    async def list_students_by_teacher(
        self,
        teacher_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[User]:
        """List students assigned to a teacher."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass

    @abstractmethod
    async def get_by_nevo_id(self, nevo_id: str) -> Optional[User]:
        """Get user by Nevo ID."""
        pass

    @abstractmethod
    async def exists_by_nevo_id(self, nevo_id: str) -> bool:
        """Check if a Nevo ID already exists."""
        pass

    @abstractmethod
    async def get_by_class_code(self, class_code: str) -> Optional[User]:
        """Get teacher by class code."""
        pass

    @abstractmethod
    async def exists_by_class_code(self, class_code: str) -> bool:
        """Check if a class code already exists."""
        pass


class ISchoolRepository(ABC):
    """School repository interface."""

    @abstractmethod
    async def create(self, school: School) -> School:
        """Create a new school."""
        pass

    @abstractmethod
    async def get_by_id(self, school_id: UUID) -> Optional[School]:
        """Get school by ID."""
        pass

    @abstractmethod
    async def update(self, school: School) -> School:
        """Update school."""
        pass

    @abstractmethod
    async def delete(self, school_id: UUID) -> bool:
        """Delete school."""
        pass

    @abstractmethod
    async def list_all(
        self,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[School]:
        """List all schools."""
        pass


class ILessonRepository(ABC):
    """Lesson repository interface."""

    @abstractmethod
    async def create(self, lesson: Lesson) -> Lesson:
        """Create a new lesson."""
        pass

    @abstractmethod
    async def get_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        """Get lesson by ID."""
        pass

    @abstractmethod
    async def update(self, lesson: Lesson) -> Lesson:
        """Update lesson."""
        pass

    @abstractmethod
    async def delete(self, lesson_id: UUID) -> bool:
        """Delete lesson."""
        pass

    @abstractmethod
    async def list_by_teacher(
        self,
        teacher_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List lessons by teacher."""
        pass

    @abstractmethod
    async def list_by_school(
        self,
        school_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List lessons by school."""
        pass

    @abstractmethod
    async def list_published(
        self,
        school_id: Optional[UUID] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Lesson]:
        """List published lessons."""
        pass


class IAdaptedLessonRepository(ABC):
    """Adapted lesson repository interface."""

    @abstractmethod
    async def create(self, adapted_lesson: AdaptedLesson) -> AdaptedLesson:
        """Create a new adapted lesson."""
        pass

    @abstractmethod
    async def get_by_id(self, adapted_lesson_id: UUID) -> Optional[AdaptedLesson]:
        """Get adapted lesson by ID."""
        pass

    @abstractmethod
    async def get_by_lesson_and_student(
        self,
        lesson_id: UUID,
        student_id: UUID,
    ) -> Optional[AdaptedLesson]:
        """Get adapted lesson for a specific student and lesson combination."""
        pass

    @abstractmethod
    async def update(self, adapted_lesson: AdaptedLesson) -> AdaptedLesson:
        """Update adapted lesson."""
        pass

    @abstractmethod
    async def list_by_student(
        self,
        student_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[AdaptedLesson]:
        """List adapted lessons for a student."""
        pass


class INeuroProfileRepository(ABC):
    """Neuro profile repository interface."""

    @abstractmethod
    async def create(self, profile: NeuroProfile) -> NeuroProfile:
        """Create a new neuro profile."""
        pass

    @abstractmethod
    async def get_by_id(self, profile_id: UUID) -> Optional[NeuroProfile]:
        """Get profile by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[NeuroProfile]:
        """Get profile by user ID."""
        pass

    @abstractmethod
    async def update(self, profile: NeuroProfile) -> NeuroProfile:
        """Update profile."""
        pass

    @abstractmethod
    async def delete(self, profile_id: UUID) -> bool:
        """Delete profile."""
        pass


class IAssessmentRepository(ABC):
    """Assessment repository interface."""

    @abstractmethod
    async def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment."""
        pass

    @abstractmethod
    async def get_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID."""
        pass

    @abstractmethod
    async def get_by_student_id(self, student_id: UUID) -> Optional[Assessment]:
        """Get assessment by student ID."""
        pass

    @abstractmethod
    async def update(self, assessment: Assessment) -> Assessment:
        """Update assessment."""
        pass


class IProgressRepository(ABC):
    """Student progress repository interface."""

    @abstractmethod
    async def create(self, progress: StudentProgress) -> StudentProgress:
        """Create progress record."""
        pass

    @abstractmethod
    async def get_by_student_id(self, student_id: UUID) -> Optional[StudentProgress]:
        """Get progress by student ID."""
        pass

    @abstractmethod
    async def update(self, progress: StudentProgress) -> StudentProgress:
        """Update progress."""
        pass

    @abstractmethod
    async def get_aggregated_by_school(
        self,
        school_id: UUID,
    ) -> dict:
        """Get aggregated progress stats for a school."""
        pass

    @abstractmethod
    async def get_aggregated_by_teacher(
        self,
        teacher_id: UUID,
    ) -> dict:
        """Get aggregated progress stats for a teacher's students."""
        pass


class ITrainingDataRepository(ABC):
    """Training data repository interface."""

    @abstractmethod
    async def create(self, log: TrainingDataLog) -> TrainingDataLog:
        """Create a training data log."""
        pass

    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> Optional[TrainingDataLog]:
        """Get log by ID."""
        pass

    @abstractmethod
    async def update(self, log: TrainingDataLog) -> TrainingDataLog:
        """Update log."""
        pass

    @abstractmethod
    async def list_unprocessed(
        self,
        limit: int = 100,
    ) -> List[TrainingDataLog]:
        """List unprocessed logs for training."""
        pass

    @abstractmethod
    async def list_with_corrections(
        self,
        limit: int = 100,
    ) -> List[TrainingDataLog]:
        """List logs that have human corrections."""
        pass

    @abstractmethod
    async def mark_batch_processed(
        self,
        log_ids: List[UUID],
        batch_id: str,
    ) -> int:
        """Mark a batch of logs as processed."""
        pass


class ITeacherFeedbackRepository(ABC):
    """Teacher feedback repository interface."""

    @abstractmethod
    async def create(self, feedback: TeacherFeedback) -> TeacherFeedback:
        """Create a new feedback."""
        pass

    @abstractmethod
    async def get_by_id(self, feedback_id: UUID) -> Optional[TeacherFeedback]:
        """Get feedback by ID."""
        pass

    @abstractmethod
    async def list_by_student(
        self, student_id: UUID, limit: int = 5
    ) -> List[TeacherFeedback]:
        """List recent feedback for a student."""
        pass


class IChatMessageRepository(ABC):
    """Chat message repository interface."""

    @abstractmethod
    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    async def list_by_student(
        self, student_id: UUID, limit: int = 50
    ) -> List[ChatMessage]:
        """List recent chat messages for a student."""
        pass


class IConnectionRepository(ABC):
    """Student-teacher connection repository interface."""

    @abstractmethod
    async def create(self, connection: Connection) -> Connection:
        """Create a new connection."""
        pass

    @abstractmethod
    async def get_by_id(self, connection_id: UUID) -> Optional[Connection]:
        """Get connection by ID."""
        pass

    @abstractmethod
    async def update(self, connection: Connection) -> Connection:
        """Update connection."""
        pass

    @abstractmethod
    async def delete(self, connection_id: UUID) -> bool:
        """Delete connection."""
        pass

    @abstractmethod
    async def list_by_student(self, student_id: UUID) -> List[Connection]:
        """List all connections for a student."""
        pass

    @abstractmethod
    async def list_by_teacher(
        self, teacher_id: UUID, status: Optional[ConnectionStatus] = None
    ) -> List[Connection]:
        """List connections for a teacher, optionally filtered by status."""
        pass

    @abstractmethod
    async def get_by_student_and_teacher(
        self, student_id: UUID, teacher_id: UUID
    ) -> Optional[Connection]:
        """Get connection between a specific student and teacher."""
        pass
