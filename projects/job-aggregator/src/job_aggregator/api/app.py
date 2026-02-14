"""FastAPI application factory.

Creates and configures the FastAPI app with:
  - CORS middleware (for React frontend)
  - Lifespan events (DB + Redis startup/shutdown)
  - Route registration

Usage:
    app = create_app()           # Called by uvicorn
    uvicorn.run(app, ...)        # Or use: python -m job_aggregator
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_aggregator import __version__
from job_aggregator.api.routes import health, jobs
from job_aggregator.db.engine import dispose_engine, get_engine
from job_aggregator.db.redis import close_redis, get_redis


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: startup and shutdown."""
    # --- Startup ---
    # Eagerly create connections so we fail fast if services are down
    get_engine()
    await get_redis()

    yield

    # --- Shutdown ---
    await close_redis()
    await dispose_engine()


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="Job Aggregator",
        description="Scam-free job aggregation with verified sources and trust scoring",
        version=__version__,
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alt frontend port
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------
    app.include_router(health.router)
    app.include_router(jobs.router, prefix="/api")

    return app
