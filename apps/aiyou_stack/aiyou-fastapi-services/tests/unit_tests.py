from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the /health endpoint returns 200 and correct structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["ingestion"] == "operational"


def test_root_endpoint():
    """Test the root endpoint returns operational status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "quick_start" in data


@patch("app.routes.ingestion.ingestion_service")
def test_submit_item(mock_service):
    """Test submitting an item for ingestion."""
    # Mock the service response
    mock_service.submit_item.return_value = "ing_mock_123"

    payload = {
        "source": {"type": "news_api", "url": "https://example.com/test", "domain": "example.com"},
        "content": {
            "title": "Test Article",
            "full_text": "This is a test article.",
            "published_at": "2025-01-01T12:00:00Z",
        },
        "metadata": {"tags": ["test"], "priority": "medium"},
    }

    response = client.post("/api/v1/ingestion/submit", json=payload)

    assert response.status_code == 202
    data = response.json()
    assert data["item_id"] == "ing_mock_123"
    assert data["status"] == "accepted"


@patch("app.routes.ingestion.ingestion_service")
def test_get_item_found(mock_service):
    """Test retrieving an existing item."""
    mock_service.get_item.return_value = {
        "item_id": "ing_mock_123",
        "status": "completed",
        "classification": {
            "tier": 1,
            "confidence": 0.95,
            "reasoning": "High value",
            "tags": ["urgent"],
        },
    }

    response = client.get("/api/v1/ingestion/items/ing_mock_123")
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == "ing_mock_123"
    assert data["status"] == "completed"
    assert data["classification"]["tier"] == 1


@patch("app.routes.ingestion.ingestion_service")
def test_get_item_not_found(mock_service):
    """Test retrieving a non-existent item."""
    mock_service.get_item.return_value = None

    response = client.get("/api/v1/ingestion/items/non_existent")
    assert response.status_code == 404
