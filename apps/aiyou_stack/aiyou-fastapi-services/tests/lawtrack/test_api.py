from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestLawTrackAPI:
    def test_get_rules_public(self):
        response = client.get("/api/v1/lawtrack/rules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_jurisdictions(self):
        response = client.get("/api/v1/lawtrack/rules/jurisdictions")
        assert response.status_code == 200
        data = response.json()
        assert "CA" in data
        assert "FEDERAL" in data

    def test_calculate_deadline_endpoint(self):
        payload = {
            "jurisdiction": "CA",
            "event_type": "summons_service",
            "trigger_date": "2023-10-01",
        }
        response = client.post("/api/v1/lawtrack/rules/calculate-deadline", json=payload)
        # If the endpoint is implemented to call the logic we tested above:
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2023-10-31"

    def test_invalid_jurisdiction(self):
        payload = {
            "jurisdiction": "MARS",
            "event_type": "summons_service",
            "trigger_date": "2023-10-01",
        }
        response = client.post("/api/v1/lawtrack/rules/calculate-deadline", json=payload)
        # Pydantic should validation error
        assert response.status_code == 422
