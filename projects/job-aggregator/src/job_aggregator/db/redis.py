"""Redis client for caching and deduplication.

Provides a thin wrapper around the redis-py async client with:
  - Connection pooling
  - Graceful startup/shutdown
  - Helper methods for common patterns (dedup checks, cached lookups)

Usage in FastAPI routes:
    @router.get("/jobs")
    async def list_jobs(cache: RedisClient = Depends(get_redis)):
        ...
"""

import redis.asyncio as aioredis

from job_aggregator.core.config import get_settings

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return the Redis client, creating it if needed.

    Also used as a FastAPI dependency.
    """
    global _client  # noqa: PLW0603
    if _client is None:
        settings = get_settings()
        _client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    """Close the Redis connection (call on app shutdown)."""
    global _client  # noqa: PLW0603
    if _client is not None:
        await _client.aclose()
        _client = None


# ---------------------------------------------------------------------------
# Deduplication helpers
# ---------------------------------------------------------------------------

SEEN_JOBS_KEY = "seen_jobs"


async def is_duplicate(url_hash: str) -> bool:
    """Check if a job URL hash has already been seen."""
    client = await get_redis()
    return await client.sismember(SEEN_JOBS_KEY, url_hash)


async def mark_seen(url_hash: str) -> None:
    """Mark a job URL hash as seen."""
    client = await get_redis()
    await client.sadd(SEEN_JOBS_KEY, url_hash)
