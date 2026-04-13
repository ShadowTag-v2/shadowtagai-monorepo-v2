"""
Tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint returns 200 and correct structure."""
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data
    assert "version" in data


def test_readiness_check():
    """Test the readiness check endpoint returns 200 and correct structure."""
    response = client.get("/api/ready")

    assert response.status_code == 200

    data = response.json()
    assert "ready" in data
    assert "checks" in data
    assert "timestamp" in data
    assert isinstance(data["checks"], dict)
    assert data["checks"]["api"] is True


def test_health_check_response_format():
    """Test that health check response includes all required fields."""
    response = client.get("/api/health")
    data = response.json()

    # Check all required fields are present
    required_fields = ["status", "timestamp", "environment", "version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_readiness_check_all_systems():
    """Test that readiness check validates all system checks."""
    response = client.get("/api/ready")
    data = response.json()

    # Verify checks structure
    assert isinstance(data["checks"], dict)
    assert len(data["checks"]) > 0

    # All checks should be boolean
    for check_name, check_status in data["checks"].items():
        assert isinstance(check_status, bool), f"Check {check_name} is not boolean"

    # Ready should be true if all checks pass
    all_checks_pass = all(data["checks"].values())
    assert data["ready"] == all_checks_pass
