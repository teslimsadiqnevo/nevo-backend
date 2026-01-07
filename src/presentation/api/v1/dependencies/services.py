"""Service dependencies."""

from src.domain.interfaces.services import IAIService, IStorageService
from src.infrastructure.external.ai.gemini_service import GeminiAIService
from src.infrastructure.external.storage.s3_service import S3StorageService


def get_ai_service() -> IAIService:
    """Get AI service dependency."""
    return GeminiAIService()


def get_storage_service() -> IStorageService:
    """Get storage service dependency."""
    return S3StorageService()
