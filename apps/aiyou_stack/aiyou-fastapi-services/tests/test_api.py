"""Tests for API endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "sandbox_enabled" in data


def test_execute_code_success(client: TestClient) -> None:
    """Test successful code execution."""
    code = """
print("Hello, World!")
result = 2 + 2
print(f"Result: {result}")
"""

    response = client.post(
        "/api/v1/execute",
        json={"code": code, "timeout": 10},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "Hello, World!" in data["output"]
    assert "Result: 4" in data["output"]
    assert data["error"] is None
    assert data["execution_time"] > 0


def test_execute_code_with_math(client: TestClient) -> None:
    """Test code execution with math operations."""
    code = """
import math
result = math.sqrt(16)
print(f"Square root of 16 is {result}")
"""

    response = client.post(
        "/api/v1/execute",
        json={"code": code},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "Square root of 16 is 4.0" in data["output"]


def test_execute_code_blocked_import(client: TestClient) -> None:
    """Test that blocked imports are rejected."""
    code = "import os\nprint(os.listdir('/'))"

    response = client.post(
        "/api/v1/execute",
        json={"code": code},
    )

    # Should be rejected during validation
    assert response.status_code == 422


def test_execute_code_blocked_builtin(client: TestClient) -> None:
    """Test that blocked builtins fail."""
    code = "eval('print(\"This should fail\")')"

    response = client.post(
        "/api/v1/execute",
        json={"code": code},
    )

    # Validation should catch this
    assert response.status_code == 422


def test_execute_code_timeout(client: TestClient) -> None:
    """Test code execution timeout."""
    code = """
import time
time.sleep(100)
print("This should not print")
"""

    response = client.post(
        "/api/v1/execute",
        json={"code": code, "timeout": 1},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert "timeout" in data["error"].lower()


def test_get_sandbox_stats(client: TestClient) -> None:
    """Test sandbox statistics endpoint."""
    # First execute some code
    client.post(
        "/api/v1/execute",
        json={"code": "print('test')"},
    )

    # Get stats
    response = client.get("/api/v1/sandbox/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total_executions" in data
    assert "successful_executions" in data
    assert "failed_executions" in data
    assert data["total_executions"] >= 1


def test_reset_sandbox_stats(client: TestClient) -> None:
    """Test resetting sandbox statistics."""
    # Execute some code
    client.post(
        "/api/v1/execute",
        json={"code": "print('test')"},
    )

    # Reset stats
    response = client.post("/api/v1/sandbox/reset-stats")
    assert response.status_code == 200
    assert "message" in response.json()

    # Verify stats are reset
    stats_response = client.get("/api/v1/sandbox/stats")
    data = stats_response.json()
    assert data["total_executions"] == 0


def test_invalid_code_too_long(client: TestClient) -> None:
    """Test that code exceeding max length is rejected."""
    code = "print('x')" * 10000  # Create very long code

    response = client.post(
        "/api/v1/execute",
        json={"code": code},
    )

    assert response.status_code == 422


def test_invalid_timeout(client: TestClient) -> None:
    """Test invalid timeout values."""
    code = "print('test')"

    # Timeout too large
    response = client.post(
        "/api/v1/execute",
        json={"code": code, "timeout": 100},
    )
    assert response.status_code == 422

    # Timeout too small
    response = client.post(
        "/api/v1/execute",
        json={"code": code, "timeout": 0},
    )
    assert response.status_code == 422
