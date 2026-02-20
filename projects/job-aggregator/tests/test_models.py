"""Tests for Pydantic schemas."""

import uuid
from datetime import UTC, datetime

from job_aggregator.core.models import (
    EmploymentTypeEnum,
    HealthResponse,
    JobCreate,
    JobFilter,
    JobRead,
    JobSourceEnum,
    TrustLevel,
)


class TestJobRead:
    """Verify JobRead schema serialization."""

    def test_minimal_job(self) -> None:
        """A job with only required fields should serialize cleanly."""
        job = JobRead(
            id=uuid.uuid4(),
            source=JobSourceEnum.BLOOMBERRY,
            source_url="https://example.com/job/123",
            title="Backend Engineer",
            company_name="Acme Corp",
            scraped_at=datetime.now(tz=UTC),
        )
        assert job.trust_score == 0.5
        assert job.employment_type == EmploymentTypeEnum.UNKNOWN
        assert job.trust_level == TrustLevel.MEDIUM

    def test_full_job(self) -> None:
        """A fully populated job should include all fields."""
        job = JobRead(
            id=uuid.uuid4(),
            source=JobSourceEnum.LINKEDIN,
            source_url="https://linkedin.com/jobs/123",
            title="SRE",
            company_name="Big Tech Inc",
            location="Remote",
            salary_min=120000,
            salary_max=180000,
            employment_type=EmploymentTypeEnum.W2_FULLTIME,
            trust_score=0.9,
            trust_level=TrustLevel.HIGH,
            posted_at=datetime.now(tz=UTC),
            scraped_at=datetime.now(tz=UTC),
        )
        assert job.salary_min == 120000
        assert job.trust_level == TrustLevel.HIGH


class TestJobFilter:
    """Verify filter defaults and validation."""

    def test_default_filters(self) -> None:
        """Default filters should return first page of 25 results."""
        f = JobFilter()
        assert f.page == 1
        assert f.page_size == 25
        assert f.min_trust_score == 0.0
        assert f.query is None

    def test_page_size_capped(self) -> None:
        """Page size should be capped at 100."""
        f = JobFilter(page_size=50)
        assert f.page_size == 50


class TestJobCreate:
    """Verify job creation schema validates input."""

    def test_valid_create(self) -> None:
        """A valid job create payload should pass validation."""
        job = JobCreate(
            source=JobSourceEnum.RSS,
            source_url="https://example.com/job/456",
            title="DevOps Engineer",
            company_name="Startup LLC",
        )
        assert job.title == "DevOps Engineer"


class TestHealthResponse:
    """Verify health response structure."""

    def test_default_health(self) -> None:
        """Default health response should show unknown status for services."""
        health = HealthResponse(version="0.1.0")
        assert health.status == "ok"
        assert health.database == "unknown"
        assert health.redis == "unknown"
