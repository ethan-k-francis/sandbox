"""Entry point for `python -m job_aggregator`.

Starts the FastAPI development server via uvicorn.
"""

import uvicorn

from job_aggregator.core.config import get_settings


def main() -> None:
    """Launch the uvicorn server with settings from environment."""
    settings = get_settings()
    uvicorn.run(
        "job_aggregator.api.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
