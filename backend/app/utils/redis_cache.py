import json
from typing import Any, Optional

import redis.asyncio as redis
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache wrapper using shared Redis client."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize with existing Redis client from core.
        
        Args:
            redis_client: Shared Redis client instance from core.redis
        """
        self.redis_client = redis_client

    async def get_cache(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            return None

    async def set_cache(
        self, key: str, value: Any, expire: Optional[int] = None
    ) -> bool:
        if not self.redis_client:
            return False
        try:
            serialized = json.dumps(value, default=str)
            if expire:
                await self.redis_client.setex(key, expire, serialized)
            else:
                await self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")
            return False

    async def delete_cache(self, key: str) -> bool:
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        if not self.redis_client:
            return 0
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete pattern error for {pattern}: {e}")
            return 0


redis_cache: Optional[RedisCache] = None
