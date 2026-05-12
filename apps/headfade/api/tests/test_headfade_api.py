"""
HeadFade API tests — Arbiter + HDI Telemetry endpoints.

Tests the FastAPI routes without live Firebase/Gemini connections.
Mock injection is handled by conftest.py (shared fixtures).
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app  # noqa: E402 — conftest patches sys.modules first

_client = TestClient(app)


@pytest.fixture
def client():
    return _client


class TestHealthCheck:
    """Health endpoint tests."""

    def test_health_root(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["service"] == "headfade-api"

    def test_health_api_prefix(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"


class TestArbiter:
    """Forensic arbiter endpoint tests."""

    def test_analyze_missing_fields(self, client):
        """POST /api/analyze with empty video_uri should 400."""
        response = client.post(
            "/api/analyze",
            json={
                "video_id": "",
                "video_uri": "",
                "actual_truth": "AI",
                "user_vote": "HUMAN",
                "vote_latency_ms": 500,
            },
        )
        assert response.status_code == 400

    @patch("routers.arbiter._get_genai_client")
    def test_analyze_success(self, mock_genai, client):
        """POST /api/analyze with valid payload should succeed."""
        # Mock the GenAI response
        mock_part = MagicMock()
        mock_part.thought = True
        mock_part.text = "I detect temporal inconsistencies in frame 42."

        mock_verdict_part = MagicMock()
        mock_verdict_part.thought = False
        mock_verdict_part.text = "VERDICT: This video is AI-generated."

        mock_content = MagicMock()
        mock_content.parts = [mock_part, mock_verdict_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_genai.return_value = mock_client_instance

        # Reset the module-level _client so _get_genai_client is called fresh
        import routers.arbiter

        routers.arbiter._client = None

        response = client.post(
            "/api/analyze",
            json={
                "video_id": "video_001",
                "video_uri": "gs://headfade-cdn-origin/test.mp4",
                "actual_truth": "AI",
                "user_vote": "HUMAN",
                "vote_latency_ms": 1200,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "gemini_thoughts" in data
        assert "gemini_verdict" in data


class TestHDITelemetry:
    """Human Deception Index telemetry tests."""

    @patch("routers.hdi_telemetry._get_db")
    def test_vote_records_juked(self, mock_get_db, client):
        """Voting incorrectly should record juked=True."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_doc = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc

        response = client.post(
            "/api/vote",
            params={
                "video_id": "video_001",
                "user_vote": "HUMAN",
                "actual_truth": "AI",
                "latency_ms": 800,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_fooled"] is True

        # Verify Firestore was called with juked=True
        call_args = mock_doc.set.call_args[0][0]
        assert call_args["juked"] is True
        assert call_args["user_vote"] == "HUMAN"
        assert call_args["actual_truth"] == "AI"

    @patch("routers.hdi_telemetry._get_db")
    def test_vote_records_not_juked(self, mock_get_db, client):
        """Voting correctly should record juked=False."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_doc = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc

        response = client.post(
            "/api/vote",
            params={
                "video_id": "video_002",
                "user_vote": "AI",
                "actual_truth": "AI",
                "latency_ms": 300,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_fooled"] is False


class TestAppCheck:
    """Firebase App Check middleware tests."""

    def test_health_bypasses_app_check(self, client):
        """Health endpoints should never require App Check tokens."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_api_health_bypasses_app_check(self, client):
        """API health should also bypass App Check."""
        response = client.get("/api/health")
        assert response.status_code == 200

    @patch("middleware.app_check._ENFORCE", True)
    def test_missing_token_rejected_when_enforced(self, client):
        """POST /api/vote without App Check token should 401 when enforced."""
        response = client.post(
            "/api/vote",
            params={
                "video_id": "video_001",
                "user_vote": "HUMAN",
                "actual_truth": "AI",
                "latency_ms": 500,
            },
        )
        assert response.status_code == 401
        assert "App Check" in response.json()["detail"]

    @patch("middleware.app_check._ENFORCE", False)
    @patch("routers.hdi_telemetry._get_db")
    def test_missing_token_allowed_when_not_enforced(self, mock_get_db, client):
        """POST /api/vote without App Check token should pass in dev mode."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.collection.return_value.document.return_value = MagicMock()

        response = client.post(
            "/api/vote",
            params={
                "video_id": "video_001",
                "user_vote": "HUMAN",
                "actual_truth": "AI",
                "latency_ms": 500,
            },
        )
        assert response.status_code == 200


class TestRateLimiter:
    """Rate limiter burst traffic tests."""

    @patch("routers.hdi_telemetry._get_db")
    def test_burst_traffic_triggers_429(self, mock_get_db, client):
        """Exceeding 30 votes in 60s window should return 429."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.collection.return_value.document.return_value = MagicMock()

        # Reset the rate store for a clean test
        import main as main_mod

        main_mod._rate_store.clear()

        # Fire 30 votes (should all succeed)
        for i in range(30):
            resp = client.post(
                "/api/vote",
                params={
                    "video_id": f"burst_{i}",
                    "user_vote": "HUMAN",
                    "actual_truth": "AI",
                    "latency_ms": 100,
                },
            )
            assert resp.status_code == 200, f"Vote {i} failed unexpectedly"

        # 31st vote should be rate-limited
        resp = client.post(
            "/api/vote",
            params={
                "video_id": "burst_overflow",
                "user_vote": "HUMAN",
                "actual_truth": "AI",
                "latency_ms": 100,
            },
        )
        assert resp.status_code == 429
        assert "Rate limit" in resp.json()["detail"]

        # Cleanup
        main_mod._rate_store.clear()

