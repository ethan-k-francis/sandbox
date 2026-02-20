"""Tests for application configuration."""

from job_aggregator.core.config import Settings


class TestSettings:
    """Verify settings load correctly with defaults and overrides."""

    def test_default_settings(self) -> None:
        """Default settings should have sensible development values."""
        settings = Settings()
        assert "localhost" in settings.database_url
        assert settings.api_port == 8000
        assert settings.log_level == "info"
        assert settings.fetch_interval_minutes == 60

    def test_override_from_kwargs(self) -> None:
        """Settings should accept overrides via keyword arguments."""
        settings = Settings(api_port=9000, log_level="debug")
        assert settings.api_port == 9000
        assert settings.log_level == "debug"

    def test_empty_api_keys_by_default(self) -> None:
        """External API keys should be empty by default (not pre-filled)."""
        settings = Settings()
        assert settings.bloomberry_api_key == ""
        assert settings.linkedin_client_id == ""
        assert settings.clearbit_api_key == ""
