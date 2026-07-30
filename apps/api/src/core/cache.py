"""
Axorks OS — Redis Cache Client

Async Redis client for caching, sessions, and rate limiting.
Uses Upstash Redis in production, local Redis for development.
"""

import redis.asyncio as redis

from src.core.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.upstash_redis_rest_url,
    decode_responses=True,
)


async def get_redis() -> redis.Redis:  # type: ignore[type-arg]
    """FastAPI dependency — returns the Redis client."""
    return redis_client


async def cache_get(key: str) -> str | None:
    """Get a cached value by key."""
    return await redis_client.get(key)


async def cache_set(key: str, value: str, ttl: int = 60) -> None:
    """Set a cached value with TTL in seconds."""
    await redis_client.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    """Delete a cached value."""
    await redis_client.delete(key)


async def rate_limit_check(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Sliding window rate limiter.
    Returns True if the request is allowed, False if rate limited.
    """
    pipe = redis_client.pipeline()
    await pipe.incr(key)
    await pipe.expire(key, window_seconds)
    results = await pipe.execute()
    current_count = results[0]
    return int(current_count) <= max_requests
