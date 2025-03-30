from redis import asyncio as aioredis

from app.config import settings

redis = None


async def init_redis():
    """Initialize the Redis connection pool."""
    global redis
    redis = aioredis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def close_redis():
    """Close the Redis connection pool."""
    global redis
    if redis:
        redis.close()
        await redis.wait_closed()


async def get_redis():
    global redis
    yield redis
