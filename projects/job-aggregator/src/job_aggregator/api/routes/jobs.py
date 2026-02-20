"""Job listing endpoints.

Phase 1: Basic CRUD and filtered listing.
Phase 2: Will add source-specific ingestion triggers and bulk operations.
"""

import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from job_aggregator.api.deps import DbSession
from job_aggregator.core.models import JobFilter, JobRead, PaginatedResponse, TrustLevel
from job_aggregator.db.tables import Job

# Use Annotated to avoid B008 (function call in default arg)
JobFilters = Annotated[JobFilter, Depends(JobFilter)]

router = APIRouter(tags=["jobs"])


def _trust_level(score: float) -> TrustLevel:
    """Convert a numeric trust score to a human-readable level."""
    if score >= 0.7:
        return TrustLevel.HIGH
    if score >= 0.4:
        return TrustLevel.MEDIUM
    return TrustLevel.LOW


@router.get("/jobs", response_model=PaginatedResponse)
async def list_jobs(db: DbSession, filters: JobFilters) -> PaginatedResponse:  # type: ignore[type-arg]
    """List jobs with optional filters and pagination.

    Supports filtering by:
      - Text search (title/description)
      - Employment type (W2, C2C, etc.)
      - Source (bloomberry, linkedin, etc.)
      - Minimum trust score
      - Maximum age in days
      - Minimum salary
      - Location keyword
    """
    query = select(Job).options(joinedload(Job.company))

    # --- Apply filters ---
    if filters.query:
        search_term = f"%{filters.query}%"
        query = query.where(Job.title.ilike(search_term) | Job.description.ilike(search_term))

    if filters.employment_type is not None:
        query = query.where(Job.employment_type == filters.employment_type.value)

    if filters.source is not None:
        query = query.where(Job.source == filters.source.value)

    if filters.min_trust_score > 0:
        query = query.where(Job.trust_score >= filters.min_trust_score)

    if filters.max_age_days is not None:
        query = query.where(
            Job.posted_at >= func.now() - func.make_interval(0, 0, 0, filters.max_age_days)
        )

    if filters.min_salary is not None:
        query = query.where(
            (Job.salary_min >= filters.min_salary) | (Job.salary_max >= filters.min_salary)
        )

    if filters.location:
        query = query.where(Job.location.ilike(f"%{filters.location}%"))

    # --- Count total matching rows ---
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # --- Pagination ---
    offset = (filters.page - 1) * filters.page_size
    query = query.order_by(Job.trust_score.desc(), Job.posted_at.desc().nullslast())
    query = query.offset(offset).limit(filters.page_size)

    result = await db.execute(query)
    rows = result.unique().scalars().all()

    # --- Serialize ---
    items = []
    for job in rows:
        job_data = JobRead.model_validate(job)
        job_data.trust_level = _trust_level(job.trust_score)
        items.append(job_data)

    return PaginatedResponse(
        items=items,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=max(1, math.ceil(total / filters.page_size)),
    )


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(db: DbSession, job_id: uuid.UUID) -> JobRead:
    """Get a single job by ID."""
    query = select(Job).where(Job.id == job_id).options(joinedload(Job.company))
    result = await db.execute(query)
    job = result.unique().scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    job_data = JobRead.model_validate(job)
    job_data.trust_level = _trust_level(job.trust_score)
    return job_data
