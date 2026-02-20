"""SQLAlchemy ORM models for the job aggregator database.

Tables:
    jobs       — Normalized job postings from all sources
    companies  — Verified company information for trust scoring
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class JobSource(enum.StrEnum):
    """Where the job listing was sourced from."""

    BLOOMBERRY = "bloomberry"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    RSS = "rss"
    DIRECT = "direct"  # Scraped from company career page


class EmploymentType(enum.StrEnum):
    """Classification of employment arrangement."""

    W2_FULLTIME = "w2_fulltime"
    W2_CONTRACT = "w2_contract"
    C2C = "c2c"
    CONTRACTOR_1099 = "1099"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


class Company(Base):
    """A company that has job listings.

    Used for trust scoring: verified companies with LinkedIn presence,
    a real careers page, and >10 employees score higher.
    """

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    domain: Mapped[str | None] = mapped_column(String(255))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    employee_count: Mapped[int | None] = mapped_column(Integer)
    has_careers_page: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    jobs: Mapped[list["Job"]] = relationship(back_populates="company", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Company {self.name!r}>"


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


class Job(Base):
    """A normalized job posting from any source.

    Each job has a trust_score (0.0 - 1.0) computed from multiple signals:
    source reliability, company verification, freshness, and description quality.
    """

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Source tracking ---
    source: Mapped[JobSource] = mapped_column(Enum(JobSource, name="job_source"), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    url_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # --- Job details ---
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(500), nullable=False)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    location: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)

    # --- Classification ---
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType, name="employment_type"),
        default=EmploymentType.UNKNOWN,
    )

    # --- Trust scoring ---
    trust_score: Mapped[float] = mapped_column(Float, default=0.5)
    flags: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # --- Timestamps ---
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company: Mapped[Company | None] = relationship(back_populates="jobs", lazy="joined")

    # Indexes for common query patterns
    __table_args__ = (
        Index("ix_jobs_trust_score", "trust_score"),
        Index("ix_jobs_posted_at", "posted_at"),
        Index("ix_jobs_employment_type", "employment_type"),
        Index("ix_jobs_source_scraped", "source", "scraped_at"),
    )

    def __repr__(self) -> str:
        return f"<Job {self.title!r} at {self.company_name!r}>"
