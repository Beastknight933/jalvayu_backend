import json
from typing import Any, Dict, Optional
from loguru import logger

from redis.asyncio import Redis

class TwinCacheService:
    """
    Event-driven caching for Digital Twin states and predictions.
    Uses Redis to serve quick dashboard queries and avoid constant DB/Disk reads.
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.DEFAULT_TTL = 3600 * 24 # 24 hours

    def _generate_key(self, domain: str, identifier: str) -> str:
        return f"twin:{domain}:{identifier}"

    async def set_state(self, domain: str, identifier: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Stores a state object in the cache (e.g., domain='current_climate', identifier='rainfall')."""
        key = self._generate_key(domain, identifier)
        try:
            await self.redis.setex(
                key,
                ttl or self.DEFAULT_TTL,
                json.dumps(data)
            )
            logger.debug(f"Cached {key}")
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")

    async def get_state(self, domain: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached state."""
        key = self._generate_key(domain, identifier)
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to fetch cache for {key}: {e}")
        return None

    async def invalidate(self, domain: str, identifier: str) -> None:
        """Invalidates a specific cached state (called when new data is ingested or predicted)."""
        key = self._generate_key(domain, identifier)
        try:
            await self.redis.delete(key)
            logger.info(f"Invalidated cache {key}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache {key}: {e}")
