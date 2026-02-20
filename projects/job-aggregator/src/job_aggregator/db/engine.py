"""Async database engine and session factory.

Provides the SQLAlchemy async engine and a session dependency for FastAPI.
The engine is created once at startup and disposed on shutdown.

Usage in FastAPI routes:
    @router.get("/jobs")
    async def list_jobs(db: AsyncSession = Depends(get_db_session)):
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from job_aggregator.core.config import get_settings

# ---------------------------------------------------------------------------
# Engine (created lazily on first import, or explicitly via init_engine)
# ---------------------------------------------------------------------------

_engine = None
_session_factory = None


def get_engine():
    """Return the async engine, creating it if needed."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.log_level == "debug",
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, creating it if needed."""
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session.

    The session is automatically closed after the request completes.
    """
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def dispose_engine() -> None:
    """Dispose the engine (call on app shutdown)."""
    global _engine, _session_factory  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
