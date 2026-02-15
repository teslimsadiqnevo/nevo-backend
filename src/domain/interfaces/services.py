"""Service interfaces - External service contracts."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.entities.lesson import Lesson


class IAIService(ABC):
    """AI service interface for LLM operations."""

    @abstractmethod
    async def generate_student_profile(
        self,
        assessment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a student profile from assessment data.

        Args:
            assessment_data: Raw assessment answers

        Returns:
            Generated profile dictionary
        """
        pass

    @abstractmethod
    async def adapt_lesson(
        self,
        lesson: Lesson,
        profile: NeuroProfile,
    ) -> Dict[str, Any]:
        """
        Adapt a lesson for a specific student profile.

        Args:
            lesson: Original lesson content
            profile: Student's neuro profile

        Returns:
            Adapted lesson with content blocks
        """
        pass

    @abstractmethod
    async def generate_quiz_questions(
        self,
        lesson_content: str,
        profile: NeuroProfile,
        num_questions: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a lesson.

        Args:
            lesson_content: The lesson text
            profile: Student's profile for difficulty adjustment
            num_questions: Number of questions to generate

        Returns:
            List of quiz question dictionaries
        """
        pass

    @abstractmethod
    async def generate_image_prompt(
        self,
        concept: str,
        profile: NeuroProfile,
    ) -> str:
        """
        Generate an image prompt for visual content.

        Args:
            concept: The concept to illustrate
            profile: Student's profile

        Returns:
            Image generation prompt
        """
        pass

    @abstractmethod
    async def generate_chat_response(
        self,
        question: str,
        profile: NeuroProfile,
        chat_history: List[Dict[str, str]],
        lesson_context: Optional[str] = None,
    ) -> str:
        """
        Generate a conversational response as Nevo AI tutor.

        Args:
            question: Student's question
            profile: Student's neuro profile
            chat_history: Recent chat messages [{"role": ..., "content": ...}]
            lesson_context: Optional current lesson text for context

        Returns:
            Nevo's response text
        """
        pass


class IStorageService(ABC):
    """Storage service interface for file operations."""

    @abstractmethod
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        folder: str = "lessons",
    ) -> str:
        """
        Upload a file to storage.

        Args:
            file_content: File bytes
            file_name: Original file name
            content_type: MIME type
            folder: Storage folder/prefix

        Returns:
            URL of uploaded file
        """
        pass

    @abstractmethod
    async def download_file(self, file_url: str) -> bytes:
        """
        Download a file from storage.

        Args:
            file_url: URL of the file

        Returns:
            File content as bytes
        """
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_url: URL of the file

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_signed_url(
        self,
        file_url: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Get a signed URL for temporary access.

        Args:
            file_url: URL of the file
            expires_in: Expiration time in seconds

        Returns:
            Signed URL
        """
        pass


class IEmailService(ABC):
    """Email service interface."""

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    async def send_welcome_email(self, to: str, name: str) -> bool:
        """Send welcome email to new user."""
        pass

    @abstractmethod
    async def send_password_reset_email(
        self,
        to: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        pass

    @abstractmethod
    async def send_verification_email(
        self,
        to: str,
        verification_token: str,
    ) -> bool:
        """Send email verification link."""
        pass


class ICacheService(ABC):
    """Cache service interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        pass
