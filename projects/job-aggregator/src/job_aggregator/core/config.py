"""Application settings loaded from environment variables.

Uses pydantic-settings to read from .env files and environment variables.
All settings have sensible defaults for local development.

Usage:
    from job_aggregator.core.config import get_settings
    settings = get_settings()
    print(settings.database_url)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    Values are loaded from environment variables (case-insensitive).
    A .env file in the project root is also read automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Silently ignore unknown env vars
    )

    # --- Database ---
    database_url: str = "postgresql+asyncpg://jobs:jobs_dev_password@localhost:5432/job_aggregator"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- API Server ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    log_level: str = "info"

    # --- External APIs (Phase 2+) ---
    bloomberry_api_key: str = ""
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    clearbit_api_key: str = ""

    # --- Scheduler ---
    fetch_interval_minutes: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()
