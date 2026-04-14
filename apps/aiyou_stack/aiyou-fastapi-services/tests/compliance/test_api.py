"""Tests for Compliance API Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def api_key():
    """Test API key"""
    return "test_api_key_12345"


class TestComplianceAPI:
    """Test cases for Compliance API endpoints"""

    def test_health_check(self, client):
        """Health endpoint should return status"""
        response = client.get("/api/v1/compliance/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    def test_list_modules(self, client):
        """Should list available modules"""
        response = client.get("/api/v1/compliance/modules")
        assert response.status_code == 200

        data = response.json()
        assert "modules" in data
        assert data["total_count"] >= 5

    def test_list_modules_filter_jurisdiction(self, client):
        """Should filter modules by jurisdiction"""
        response = client.get("/api/v1/compliance/modules?jurisdiction=eu")
        assert response.status_code == 200

        data = response.json()
        assert all(m["jurisdiction"] == "eu" for m in data["modules"])

    def test_get_module_detail(self, client):
        """Should get module details"""
        response = client.get("/api/v1/compliance/modules/eu_ai_act")
        assert response.status_code == 200

        data = response.json()
        assert data["metadata"]["id"] == "eu_ai_act"
        assert data["controls_count"] > 0

    def test_get_module_not_found(self, client):
        """Should return 404 for unknown module"""
        response = client.get("/api/v1/compliance/modules/unknown_module")
        assert response.status_code == 404

    def test_generate_blueprint(self, client, api_key):
        """Should generate compliance blueprint"""
        response = client.post(
            "/api/v1/compliance/blueprint",
            headers={"X-API-Key": api_key},
            json={
                "jurisdictions": ["eu"],
                "regulations": ["eu_ai_act", "gdpr"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["selected_modules"]) == 2
        assert data["total_controls"] > 0
        assert data["estimated_monthly_cost_usd"] > 0

    def test_run_assessment(self, client, api_key):
        """Should run compliance assessment"""
        response = client.post(
            "/api/v1/compliance/assess",
            headers={"X-API-Key": api_key},
            json={
                "content_type": "ai_chatbot",
                "is_ai_generated": True,
                "modules": ["eu_ai_act"],
                "metadata": {"ai_disclosure": True},
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["assessment_id"] is not None
        assert "overall_status" in data
        assert "overall_score" in data
        assert len(data["modules_assessed"]) == 1

    def test_validate_content(self, client, api_key):
        """Should validate content"""
        response = client.post(
            "/api/v1/compliance/validate",
            headers={"X-API-Key": api_key},
            json={
                "response_text": "This is an AI assistant response.",
                "modules": ["eu_ai_act"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["validation_id"] is not None
        assert "is_compliant" in data

    def test_batch_assessment(self, client, api_key):
        """Should run batch assessment"""
        response = client.post(
            "/api/v1/compliance/batch",
            headers={"X-API-Key": api_key},
            json={
                "inputs": [
                    {"content_type": "ai_chatbot", "modules": ["eu_ai_act"]},
                    {"content_type": "ai_chatbot", "modules": ["eu_ai_act"]},
                ],
                "max_concurrent": 2,
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["batch_id"] is not None
        assert data["total_submitted"] == 2

    def test_get_module_checklist(self, client):
        """Should get module checklist"""
        response = client.get("/api/v1/compliance/modules/eu_ai_act/checklist")
        assert response.status_code == 200

        data = response.json()
        assert data["regulation"] == "eu_ai_act"
        assert "checklist" in data
        assert len(data["checklist"]) > 0

    def test_single_module_assessment(self, client, api_key):
        """Should assess single module"""
        response = client.post(
            "/api/v1/compliance/modules/gdpr/assess",
            headers={"X-API-Key": api_key},
            json={
                "content_type": "user_data",
                "contains_pii": True,
                "metadata": {"lawful_basis": "consent"},
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["modules_assessed"]) == 1
        assert data["modules_assessed"][0]["module_id"] == "gdpr"
