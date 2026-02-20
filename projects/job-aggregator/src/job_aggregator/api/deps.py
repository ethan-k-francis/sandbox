"""FastAPI dependency injection.

Centralizes all injectable dependencies so routes stay clean.
Import from here instead of reaching into db/ directly.

Usage:
    from job_aggregator.api.deps import DbSession, Cache

    @router.get("/jobs")
    async def list_jobs(db: DbSession, cache: Cache):
        ...
"""

from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from job_aggregator.db.engine import get_db_session
from job_aggregator.db.redis import get_redis

# Type aliases for cleaner route signatures
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
Cache = Annotated[aioredis.Redis, Depends(get_redis)]
