"""Redis cache service implementation."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from src.core.config.settings import settings
from src.domain.interfaces.services import ICacheService


class RedisCacheService(ICacheService):
    """Cache service implementation using Redis."""

    def __init__(self):
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self.redis.set(
                key,
                serialized,
                ex=ttl or self.default_ttl,
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self.redis.exists(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()
