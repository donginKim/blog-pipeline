# Redis configuration
import redis.asyncio as redis
from redis.asyncio import Redis
from .config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)

# Redis client
redis_client: Redis = redis.Redis(connection_pool=redis_pool)


async def get_redis() -> Redis:
    """Dependency to get Redis client"""
    return redis_client


async def close_redis():
    """Close Redis connections"""
    await redis_client.close()

