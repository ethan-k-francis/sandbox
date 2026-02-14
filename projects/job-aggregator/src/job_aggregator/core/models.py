"""Pydantic schemas for API request/response models.

These are separate from the SQLAlchemy ORM models in db/tables.py.
FastAPI uses these for automatic request validation and response serialization.

Naming convention:
    - *Create  — request body for creating a resource
    - *Read    — response body (what the API returns)
    - *Filter  — query parameters for filtering/searching
"""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl

# ---------------------------------------------------------------------------
# Enums (mirror the DB enums for API contracts)
# ---------------------------------------------------------------------------


class JobSourceEnum(StrEnum):
    """Job listing source."""

    BLOOMBERRY = "bloomberry"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    RSS = "rss"
    DIRECT = "direct"


class EmploymentTypeEnum(StrEnum):
    """Employment arrangement classification."""

    W2_FULLTIME = "w2_fulltime"
    W2_CONTRACT = "w2_contract"
    C2C = "c2c"
    CONTRACTOR_1099 = "1099"
    UNKNOWN = "unknown"


class TrustLevel(StrEnum):
    """Human-readable trust score buckets."""

    HIGH = "high"  # 0.7 - 1.0
    MEDIUM = "medium"  # 0.4 - 0.69
    LOW = "low"  # 0.0 - 0.39


# ---------------------------------------------------------------------------
# Company schemas
# ---------------------------------------------------------------------------


class CompanyRead(BaseModel):
    """Company data returned by the API."""

    id: uuid.UUID
    name: str
    domain: str | None = None
    linkedin_url: str | None = None
    employee_count: int | None = None
    has_careers_page: bool = False
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Job schemas
# ---------------------------------------------------------------------------


class JobRead(BaseModel):
    """A job posting as returned by the API."""

    id: uuid.UUID
    source: JobSourceEnum
    source_url: str
    title: str
    company_name: str
    company: CompanyRead | None = None
    location: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    employment_type: EmploymentTypeEnum = EmploymentTypeEnum.UNKNOWN
    trust_score: float = Field(ge=0.0, le=1.0, default=0.5)
    trust_level: TrustLevel = TrustLevel.MEDIUM
    flags: dict | None = None
    posted_at: datetime | None = None
    scraped_at: datetime

    model_config = {"from_attributes": True}


class JobFilter(BaseModel):
    """Query parameters for filtering jobs."""

    # Text search
    query: str | None = Field(None, description="Search title and description")

    # Classification filters
    employment_type: EmploymentTypeEnum | None = None
    source: JobSourceEnum | None = None
    min_trust_score: float = Field(0.0, ge=0.0, le=1.0)

    # Freshness
    max_age_days: int | None = Field(None, ge=1, description="Max age in days")

    # Salary
    min_salary: int | None = Field(None, ge=0)

    # Location
    location: str | None = None

    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(25, ge=1, le=100)


class JobCreate(BaseModel):
    """Schema for creating a job (used internally by source adapters)."""

    source: JobSourceEnum
    source_url: HttpUrl
    title: str
    company_name: str
    location: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    posted_at: datetime | None = None


# ---------------------------------------------------------------------------
# Pagination wrapper
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel):
    """Paginated list response."""

    items: list[JobRead]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str
    database: str = "unknown"
    redis: str = "unknown"
