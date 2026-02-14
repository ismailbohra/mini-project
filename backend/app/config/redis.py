# app/core/redis.py
"""Centralized Redis connection management."""
from typing import Optional

import redis.asyncio as redis
from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Singleton Redis client manager."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._redis_url = settings.REDIS_URL

    async def connect(self) -> redis.Redis:
        """Establish Redis connection."""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self._redis_url,
                    decode_responses=True,
                    encoding="utf-8"
                )
                await self._client.ping()
                logger.info(f"Redis client connected to {self._redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._client = None
                raise
        return self._client

    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis client disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting Redis: {e}")
            finally:
                self._client = None

    def get_client(self) -> Optional[redis.Redis]:
        """Get the current Redis client instance."""
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if Redis client is connected."""
        return self._client is not None


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> redis.Redis:
    """Dependency to get Redis client."""
    client = redis_client.get_client()
    if client is None:
        raise RuntimeError("Redis client not connected")
    return client
