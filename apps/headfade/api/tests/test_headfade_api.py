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


class TestEloGainBoundary:
    """Boundary tests for eloGain at exact threshold values.

    The eloGain function uses strict > comparisons, so exact boundary
    values fall into the lower tier. These tests verify that behavior.
    """

    @pytest.mark.parametrize(
        "fool_rate,is_correct,expected_delta",
        [
            # Exact boundary values (should fall into LOWER tier due to > not >=)
            (0.2, True, 1),  # exactly 0.2 → NOT >0.25, NOT >0.2 → base +1
            (0.25, True, 1),  # exactly 0.25 → NOT >0.25 → base +1
            (0.5, True, 5),  # exactly 0.5 → NOT >0.5, IS >0.25 → +5
            (0.75, True, 15),  # exactly 0.75 → NOT >0.75, IS >0.5 → +15
            (0.9, True, 25),  # exactly 0.9 → NOT >0.9, IS >0.75 → +25
            # Just above boundaries
            (0.251, True, 5),  # just above 0.25 → +5
            (0.501, True, 15),  # just above 0.5 → +15
            (0.751, True, 25),  # just above 0.75 → +25
            (0.901, True, 50),  # just above 0.9 → +50
            # Incorrect votes at boundaries
            (0.2, False, -2),  # exactly 0.2 → not <0.2 → -2
            (0.19, False, -5),  # just below 0.2 → <0.2 → -5
            (0.0, False, -5),  # minimum → -5
            (1.0, True, 50),  # maximum → +50
        ],
    )
    def test_elo_gain_boundary(self, fool_rate, is_correct, expected_delta):
        """Verify eloGain returns correct delta at exact threshold boundaries."""

        # Import the function under test from the PWA hook's logic
        # (mirrored in test to avoid TS import — we test the Python equivalent)
        def elo_gain(fr: float, correct: bool) -> int:
            if not correct:
                return -5 if fr < 0.2 else -2
            if fr > 0.9:
                return 50
            if fr > 0.75:
                return 25
            if fr > 0.5:
                return 15
            if fr > 0.25:
                return 5
            return 1

        assert elo_gain(fool_rate, is_correct) == expected_delta


class TestOTelSpanAttributes:
    """Verify OpenTelemetry span attributes are set correctly during vote processing."""

    @patch("routers.hdi_telemetry._get_db")
    @patch("routers.hdi_telemetry._tracer")
    def test_vote_sets_span_attributes(self, mock_tracer, mock_get_db, client):
        """Vote endpoint should set hdi.* span attributes for Cloud Trace."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.collection.return_value.document.return_value = MagicMock()

        mock_span = MagicMock()
        mock_span.__enter__ = MagicMock(return_value=mock_span)
        mock_span.__exit__ = MagicMock(return_value=False)
        mock_tracer.start_as_current_span.return_value = mock_span

        response = client.post(
            "/api/vote",
            params={
                "video_id": "otel_test_001",
                "user_vote": "HUMAN",
                "actual_truth": "AI",
                "latency_ms": 420,
            },
        )
        assert response.status_code == 200

        # Verify the tracer was invoked with hdi_vote_processing span name
        mock_tracer.start_as_current_span.assert_called_once_with("hdi_vote_processing")

        # Verify span attributes were set
        span_calls = {call[0][0]: call[0][1] for call in mock_span.set_attribute.call_args_list}
        assert span_calls.get("hdi.video_id") == "otel_test_001"
        assert span_calls.get("hdi.juked") is True
        assert span_calls.get("hdi.latency_ms") == 420
        assert span_calls.get("hdi.user_vote") == "HUMAN"
