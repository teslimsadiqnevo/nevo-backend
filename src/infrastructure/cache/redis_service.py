"""Redis cache service implementation."""

import json
from typing import Any, Optional

import httpx
import redis.asyncio as redis

from src.core.config.settings import settings
from src.domain.interfaces.services import ICacheService


class RedisCacheService(ICacheService):
    """Cache service implementation using Redis (supports standard Redis and Upstash REST API)."""

    def __init__(self):
        self.redis_url = settings.redis_url
        self.default_ttl = 3600  # 1 hour
        
        # Check if it's an Upstash REST API URL
        if self.redis_url.startswith("https://"):
            # Upstash REST API
            self.use_upstash = True
            # Extract token from URL if provided in format: https://endpoint.upstash.io?token=xxx
            # Or use separate env var
            self.upstash_token = settings.upstash_rest_token
            if not self.upstash_token:
                raise ValueError("UPSTASH_REST_TOKEN is required when using Upstash REST API")
            # Remove query params if any
            self.upstash_base_url = self.redis_url.split("?")[0]
            self.http_client = httpx.AsyncClient()
        else:
            # Standard Redis connection
            self.use_upstash = False
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def _upstash_request(self, command: str, *args: Any) -> Any:
        """Make a request to Upstash REST API."""
        # Upstash REST API format: POST to endpoint with command and args in body
        url = self.upstash_base_url
        headers = {
            "Authorization": f"Bearer {self.upstash_token}",
            "Content-Type": "application/json",
        }
        # Format: [command, arg1, arg2, ...]
        payload = [command] + list(args)
        
        response = await self.http_client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("result")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.use_upstash:
            value = await self._upstash_request("get", key)
        else:
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
            if self.use_upstash:
                await self._upstash_request("set", key, serialized, "EX", ttl or self.default_ttl)
            else:
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
        if self.use_upstash:
            result = await self._upstash_request("del", key)
            return result > 0
        else:
            result = await self.redis.delete(key)
            return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self.use_upstash:
            result = await self._upstash_request("exists", key)
            return result > 0
        else:
            return await self.redis.exists(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if self.use_upstash:
            # Upstash REST API doesn't support SCAN directly
            # This is a limitation - would need to use keys command (not recommended for production)
            return 0
        else:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self.use_upstash:
            await self.http_client.aclose()
        else:
            await self.redis.close()
