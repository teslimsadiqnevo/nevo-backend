"""No-op cache service for when Redis is disabled."""

from typing import Any, Optional

from src.domain.interfaces.services import ICacheService


class NoOpCacheService(ICacheService):
    """No-op cache service that doesn't cache anything."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (always returns None)."""
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache (no-op)."""
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache (no-op)."""
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache (always returns False)."""
        return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (no-op)."""
        return 0

