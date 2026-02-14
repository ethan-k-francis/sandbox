"""API integration tests using FastAPI TestClient.

These tests use mocked dependencies (no real DB/Redis needed).
For full integration tests with real services, mark with @pytest.mark.integration.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client: AsyncClient) -> None:
    """Health endpoint should return 200 with version info."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_reports_database_connected(client: AsyncClient) -> None:
    """Health check should report database as connected (mocked session)."""
    response = await client.get("/health")
    data = response.json()
    assert data["database"] == "connected"
    # Redis status depends on whether the lifespan connected successfully.
    # In unit tests without Docker, it may report "disconnected" — that's fine.
    assert data["redis"] in ("connected", "disconnected")


@pytest.mark.asyncio
async def test_jobs_list_returns_paginated(client: AsyncClient) -> None:
    """Jobs endpoint should return a paginated response (empty with mock DB)."""
    response = await client.get("/api/jobs")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["items"] == []
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_jobs_list_accepts_filters(client: AsyncClient) -> None:
    """Jobs endpoint should accept query parameter filters."""
    response = await client.get(
        "/api/jobs",
        params={
            "employment_type": "w2_fulltime",
            "min_trust_score": 0.7,
            "max_age_days": 14,
            "page_size": 10,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_job_not_found_returns_404(client: AsyncClient) -> None:
    """Getting a non-existent job should return 404."""
    response = await client.get("/api/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
