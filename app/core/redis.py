import redis.asyncio as redis
from loguru import logger
from app.core.config import settings

# Create a Redis connection pool using the url from settings
redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    socket_timeout=5.0,
    socket_connect_timeout=5.0
)

async def check_redis_connection() -> bool:
    """Check if Redis is accessible."""
    try:
        await redis_client.ping()
        return True
    except redis.ConnectionError:
        logger.error(f"Failed to connect to Redis at {settings.redis_url}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error when connecting to Redis: {e}")
        return False
