"""Health check endpoint.

Reports the status of the API server and its dependencies (PostgreSQL, Redis).
Useful for monitoring, load balancers, and Docker health checks.
"""

from fastapi import APIRouter
from sqlalchemy import text

from job_aggregator import __version__
from job_aggregator.api.deps import Cache, DbSession
from job_aggregator.core.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: DbSession, cache: Cache) -> HealthResponse:
    """Check API, database, and cache connectivity."""
    response = HealthResponse(version=__version__)

    # Check PostgreSQL
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        response.database = "connected"
    except Exception:
        response.database = "disconnected"

    # Check Redis
    try:
        await cache.ping()
        response.redis = "connected"
    except Exception:
        response.redis = "disconnected"

    return response
