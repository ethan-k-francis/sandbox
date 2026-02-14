"""Shared test fixtures.

Provides:
  - Override settings to use test-safe defaults
  - FastAPI TestClient (async) with mocked DB and Redis
  - Mock Redis and DB session for unit tests
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient

from job_aggregator.api.app import create_app
from job_aggregator.core.config import Settings, get_settings
from job_aggregator.db.engine import get_db_session
from job_aggregator.db.redis import get_redis

# ---------------------------------------------------------------------------
# Settings override — use test-safe defaults
# ---------------------------------------------------------------------------


def get_test_settings() -> Settings:
    """Return settings suitable for testing (no real DB/Redis needed for unit tests)."""
    return Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/test_job_aggregator",
        redis_url="redis://localhost:6379/1",
        api_reload=False,
        log_level="warning",
    )


# ---------------------------------------------------------------------------
# Mock Redis — for tests that don't need a real Redis server
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Return a mock Redis client."""
    mock = AsyncMock(spec=aioredis.Redis)
    mock.ping.return_value = True
    mock.sismember.return_value = False
    mock.sadd.return_value = 1
    return mock


# ---------------------------------------------------------------------------
# Mock DB session — for tests that don't need a real PostgreSQL
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db() -> AsyncMock:
    """Return a mock async database session.

    The mock handles two common patterns:
      1. Health check: execute(text("SELECT 1")) -> scalar() returns 1
      2. Job queries: execute(select(...)) -> scalar() returns 0 (count),
         unique().scalars().all() returns [] (empty results)
    """
    mock = AsyncMock()

    # Default result mock for queries
    result_mock = MagicMock()
    result_mock.scalar.return_value = 0  # Count queries return 0
    result_mock.scalar_one_or_none.return_value = None  # Single lookups return None
    result_mock.unique.return_value = result_mock
    result_mock.scalars.return_value = result_mock
    result_mock.all.return_value = []

    # Health check returns 1 for "SELECT 1", count queries return 0
    # We use side_effect to differentiate, but for simplicity just return
    # the same mock — scalar() returns 0 which is fine (health checks the exception)
    mock.execute.return_value = result_mock
    return mock


# ---------------------------------------------------------------------------
# FastAPI test client — uses mocked dependencies (no Docker needed)
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(mock_redis: AsyncMock, mock_db: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """Async test client with mocked dependencies.

    Uses mock Redis and DB so tests can run without Docker services.
    For full integration tests with real services, mark with @pytest.mark.integration.
    """
    app = create_app()

    # Override all external dependencies
    app.dependency_overrides[get_settings] = get_test_settings
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_db_session] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
