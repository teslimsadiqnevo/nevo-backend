"""Service dependencies."""

from functools import lru_cache

from src.core.config.settings import settings
from src.domain.interfaces.services import IAIService, ICacheService, IEmailService, IStorageService


@lru_cache()
def get_cache_service() -> ICacheService:
    """Get cache service dependency (singleton)."""
    if settings.redis_enabled:
        from src.infrastructure.cache.redis_service import RedisCacheService
        return RedisCacheService()
    from src.infrastructure.cache.noop_cache import NoOpCacheService
    return NoOpCacheService()


def get_ai_service() -> IAIService:
    """Get AI service dependency (Gemini or Ollama based on configuration)."""
    if settings.local_ai_enabled:
        from src.infrastructure.external.ai.ollama_service import OllamaAIService
        return OllamaAIService()
    from src.infrastructure.external.ai.gemini_service import GeminiAIService
    return GeminiAIService()


def get_storage_service() -> IStorageService:
    """Get storage service dependency."""
    from src.infrastructure.external.storage.s3_service import S3StorageService
    return S3StorageService()


@lru_cache()
def get_email_service() -> IEmailService:
    """Get email service dependency (singleton)."""
    from src.infrastructure.external.email.resend_service import ResendEmailService
    return ResendEmailService()
