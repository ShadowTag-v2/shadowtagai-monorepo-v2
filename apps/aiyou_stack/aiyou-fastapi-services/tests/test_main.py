"""Tests for the main FastAPI application (src.main).

Tests use the shared conftest.py fixtures which already provide
the async in-memory SQLite database and the correct app import.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app

# ==============================================================================
# Health Endpoint Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_health_check():
    """Test the legacy /health endpoint returns 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent-governance"


@pytest.mark.asyncio
async def test_api_health_check():
    """Test the /api/health endpoint returns 200 with rich metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_readiness_check():
    """Test the legacy /ready endpoint returns correct structure."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    # May return 200 or 503 depending on initialization state
    assert response.status_code in (200, 503)
    data = response.json()
    assert "ready" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_api_readiness_check():
    """Test the /api/ready endpoint returns boolean checks with timestamp."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/ready")

    assert response.status_code in (200, 503)
    data = response.json()
    assert "ready" in data
    assert "checks" in data
    assert "timestamp" in data
    assert isinstance(data["checks"], dict)
    assert data["checks"]["api"] is True


# ==============================================================================
# Mission Endpoint Test
# ==============================================================================


@pytest.mark.asyncio
async def test_mission_endpoint():
    """Test the /mission endpoint responds correctly."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/mission",
            json={"query": "test query", "context": "general"},
        )

    # 200 if judge approves, 403 if blocked — both are valid
    assert response.status_code in (200, 403)
