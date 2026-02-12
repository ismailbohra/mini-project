import json
from typing import Any, Optional

import app.utils.redis_cache as redis_cache_module
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def get_cache(key: str) -> Optional[Any]:
    try:
        if redis_cache_module.redis_cache:
            return await redis_cache_module.redis_cache.get_cache(key)
        return None
    except Exception as e:
        logger.warning(f"Redis get_cache error for key {key}: {e}")
        return None


async def set_cache(key: str, value: Any, expire: Optional[int] = None) -> bool:
    try:
        if redis_cache_module.redis_cache:
            # ensure serializable
            serializable = value
            # allow passing Pydantic-model-exported dicts or raw lists/dicts
            if hasattr(value, "model_dump"):
                serializable = value.model_dump(mode="json")
            return await redis_cache_module.redis_cache.set_cache(
                key, serializable, expire
            )
        return False
    except Exception as e:
        logger.warning(f"Redis set_cache error for key {key}: {e}")
        return False


async def delete_cache(key: str) -> bool:
    try:
        if redis_cache_module.redis_cache:
            return await redis_cache_module.redis_cache.delete_cache(key)
        return False
    except Exception as e:
        logger.warning(f"Redis delete_cache error for key {key}: {e}")
        return False


async def delete_pattern(pattern: str) -> int:
    try:
        if redis_cache_module.redis_cache:
            return await redis_cache_module.redis_cache.delete_pattern(pattern)
        return 0
    except Exception as e:
        logger.warning(f"Redis delete_pattern error for pattern {pattern}: {e}")
        return 0
