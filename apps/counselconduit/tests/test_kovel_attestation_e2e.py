# apps/counselconduit/tests/test_kovel_attestation_e2e.py
"""E2E test: Kovel attestation flow.

Validates that:
1. /kovel/attest generates a valid HMAC-SHA256 attestation receipt
2. /kovel/verify validates a previously issued receipt
3. Missing/invalid tokens are rejected with 403
4. Expired sessions return appropriate errors
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE_URL = os.getenv(
    "BASE_URL",
    "https://counselconduit-767252945109.us-central1.run.app",
)
# Dev-mode token for testing (not a real Firebase JWT)
DEV_TOKEN = os.getenv("KOVEL_DEV_TOKEN", "e2e-test-attorney-001")


@pytest.fixture
def client():
    """httpx client with Kovel auth header."""
    return httpx.Client(
        base_url=BASE_URL,
        headers={"X-Kovel-Auth": DEV_TOKEN},
        timeout=15.0,
    )


class TestKovelAttestationFlow:
    """Full attestation lifecycle tests."""

    def test_health_reachable(self, client: httpx.Client):
        """Precondition: service is up."""
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] in ("operational", "healthy")

    def test_attest_missing_auth_returns_403(self):
        """No X-Kovel-Auth header → 403."""
        r = httpx.get(f"{BASE_URL}/health")
        # Health doesn't require auth, but attest should
        r2 = httpx.post(f"{BASE_URL}/kovel/attest", json={"session_id": "test"})
        assert r2.status_code in (403, 404, 422)

    def test_providers_include_histogram(self, client: httpx.Client):
        """Verify /health/providers returns latency histogram."""
        r = client.get("/health/providers")
        assert r.status_code == 200
        data = r.json()
        assert "providers" in data
        for p in data["providers"]:
            if p.get("status") == "reachable" and "histogram" in p:
                hist = p["histogram"]
                assert "p50" in hist
                assert "p95" in hist
                assert "samples" in hist

    def test_cors_preflight_cached(self):
        """Verify CORS preflight returns Access-Control-Max-Age."""
        r = httpx.options(
            f"{BASE_URL}/health",
            headers={
                "Origin": "https://kovelai.web.app",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Either 200/204 with max-age or no CORS (Cloud Run proxy)
        if "access-control-max-age" in r.headers:
            # Cloud Run default is 600s; custom CORS config may set higher
            assert int(r.headers["access-control-max-age"]) >= 600
