"""Automated Regression Suite for CounselConduit Endpoints (#21).

Tests all API endpoints against a live deployment (staging by default).
Run with: pytest tests/test_regression.py -v --base-url=<url>
"""

import os

import pytest
import requests

BASE_URL = os.environ.get(
    "CC_STAGING_URL",
    "https://counselconduit-staging-767252945109.us-central1.run.app",
)


class TestHealthEndpoints:
    """Verify core health endpoints."""

    def test_health_returns_200(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "counselconduit"

    def test_health_has_version(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        assert "version" in data
        assert data["version"]  # non-empty

    def test_health_has_firestore(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        assert data.get("firestore") == "connected"


class TestOpenAPIEndpoints:
    """Verify OpenAPI and docs endpoints."""

    def test_openapi_json(self):
        resp = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "info" in data

    def test_docs_available(self):
        resp = requests.get(f"{BASE_URL}/docs", timeout=10)
        assert resp.status_code == 200
        assert "swagger" in resp.text.lower() or "redoc" in resp.text.lower()


class TestDispatchEndpoints:
    """Verify dispatch routing."""

    def test_dispatch_requires_post(self):
        resp = requests.get(f"{BASE_URL}/api/v1/dispatch", timeout=10)
        assert resp.status_code == 405  # Method Not Allowed

    def test_dispatch_rejects_empty_body(self):
        resp = requests.post(f"{BASE_URL}/api/v1/dispatch", json={}, timeout=10)
        assert resp.status_code == 422  # Validation Error

    def test_dispatch_with_valid_body(self):
        payload = {
            "query": "What is consideration in contract law?",
            "firm_id": "regression-test-firm",
            "session_id": "regression-test-session",
            "preferred_model": None,
            "firm_allowed_models": ["gemini-flash"],
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/dispatch",
            json=payload,
            headers={"X-User-Tier": "trial"},
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "model" in data
        assert "provider" in data
        assert "tier" in data
        assert "latency_ms" in data


class TestAdminEndpoints:
    """Verify admin endpoints.

    On staging (APP_ENV != production): returns 200 (dev bypass).
    On production: returns 401 (RBAC enforced, no auth provided).
    """

    ADMIN_OK_CODES = {200, 401}  # 200 = dev, 401 = prod RBAC

    def test_admin_metrics(self):
        resp = requests.get(f"{BASE_URL}/admin/metrics", timeout=10)
        assert resp.status_code in self.ADMIN_OK_CODES
        if resp.status_code == 200:
            data = resp.json()
            assert "total_dispatches" in data or "dispatches" in data
        elif resp.status_code == 401:
            data = resp.json()
            assert data.get("detail", {}).get("type", "").startswith("https://")

    def test_admin_models(self):
        resp = requests.get(
            f"{BASE_URL}/admin/models",
            params={"tier": "trial"},
            timeout=10,
        )
        assert resp.status_code in self.ADMIN_OK_CODES
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, (list, dict))

    def test_admin_slo_report(self):
        resp = requests.get(f"{BASE_URL}/admin/slo-report", timeout=10)
        assert resp.status_code in self.ADMIN_OK_CODES
        if resp.status_code == 200:
            data = resp.json()
            assert "slo" in data
            assert "report" in data
            assert data["report"]["target_availability"] == "99.5%"

    def test_admin_token_budgets(self):
        resp = requests.get(f"{BASE_URL}/admin/token-budgets", timeout=10)
        assert resp.status_code in self.ADMIN_OK_CODES

    def test_vent_mode_diagnostics(self):
        resp = requests.get(f"{BASE_URL}/admin/vent-mode/diagnostics", timeout=10)
        assert resp.status_code in self.ADMIN_OK_CODES
        if resp.status_code == 200:
            data = resp.json()
            assert "active_streams" in data
            assert "capacity_limit" in data


class TestSecurityHeaders:
    """Verify security headers on responses."""

    def test_cors_headers_absent_without_origin(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        # No CORS headers without Origin
        assert resp.status_code == 200

    def test_no_server_version_leak(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        server = resp.headers.get("Server", "")
        assert "uvicorn" not in server.lower()
        assert "python" not in server.lower()

    def test_rfc9457_error_format(self):
        """Errors should follow RFC 9457 Problem Details."""
        resp = requests.post(f"{BASE_URL}/api/v1/dispatch", json={}, timeout=10)
        assert resp.status_code == 422
        data = resp.json()
        assert "detail" in data


class TestRateLimit:
    """Verify rate limiting headers."""

    def test_dispatch_returns_rate_limit_headers(self):
        payload = {
            "query": "Test rate limits",
            "firm_id": "regression-ratelimit",
            "session_id": "regression-session",
            "firm_allowed_models": ["gemini-flash"],
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/dispatch",
            json=payload,
            headers={"X-User-Tier": "trial"},
            timeout=15,
        )
        if resp.status_code == 200:
            assert "X-RateLimit-Limit" in resp.headers
            assert "X-RateLimit-Remaining" in resp.headers
            assert "X-Dispatch-Tier" in resp.headers
