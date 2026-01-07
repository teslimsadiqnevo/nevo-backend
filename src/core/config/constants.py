"""Application constants and enums shared across the application."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    STUDENT = "student"
    TEACHER = "teacher"
    SCHOOL_ADMIN = "school_admin"
    PARENT = "parent"
    SUPER_ADMIN = "super_admin"


class ContentBlockType(str, Enum):
    """Types of content blocks in adapted lessons."""

    HEADING = "heading"
    TEXT = "text"
    IMAGE = "image"
    IMAGE_PROMPT = "image_prompt"
    VIDEO = "video"
    QUIZ = "quiz"
    QUIZ_CHECK = "quiz_check"
    ACTIVITY = "activity"
    SUMMARY = "summary"


class LearningStyle(str, Enum):
    """Learning style preferences."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"


class ReadingLevel(str, Enum):
    """Reading level classifications."""

    PRE_K = "pre_k"
    GRADE_1 = "grade_1"
    GRADE_2 = "grade_2"
    GRADE_3 = "grade_3"
    GRADE_4 = "grade_4"
    GRADE_5 = "grade_5"
    GRADE_6 = "grade_6"
    GRADE_7 = "grade_7"
    GRADE_8 = "grade_8"
    HIGH_SCHOOL = "high_school"


class ComplexityTolerance(str, Enum):
    """Complexity tolerance levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SensoryTrigger(str, Enum):
    """Sensory triggers for neurodivergent students."""

    LOUD_SOUNDS = "loud_sounds"
    BRIGHT_LIGHTS = "bright_lights"
    CROWDED_VISUALS = "crowded_visuals"
    RAPID_TRANSITIONS = "rapid_transitions"
    FLASHING_CONTENT = "flashing_content"


class AssessmentStatus(str, Enum):
    """Assessment completion status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PROCESSING = "processing"


class LessonStatus(str, Enum):
    """Lesson status."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AdaptedLessonStatus(str, Enum):
    """Status of adapted lesson generation."""

    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class ProgressStatus(str, Enum):
    """Student progress status for a lesson."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuestionType(str, Enum):
    """Assessment question types."""

    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT_INPUT = "text_input"
    SCALE = "scale"
    YES_NO = "yes_no"


# Database constraints
MAX_EMAIL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TITLE_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 1000
MAX_URL_LENGTH = 2048

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# AI constraints
MAX_LESSON_CONTENT_LENGTH = 50000
MAX_PROFILE_INTERESTS = 10
DEFAULT_ATTENTION_SPAN_MINUTES = 15
