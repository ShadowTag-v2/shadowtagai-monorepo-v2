"""Agent Router Tests"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_models():
    """Test list models endpoint"""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    assert any(m["id"] == "claude-sonnet-4-5-20250929" for m in data["models"])


@pytest.mark.skipif(
    True,  # Skip by default as it requires API key
    reason="Requires ANTHROPIC_API_KEY environment variable",
)
def test_query_agent():
    """Test agent query endpoint (requires API key)"""
    response = client.post(
        "/api/v1/query", json={"prompt": "Hello, what is 2+2?", "temperature": 0.7},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
