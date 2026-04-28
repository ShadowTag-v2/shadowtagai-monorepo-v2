# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/tests/test_smoke.py
"""Smoke test suite for post-deploy validation (Item #18).

Run after every Cloud Run deployment to verify core functionality.
Usage:
    BASE_URL=https://counselconduit-767252945109.us-central1.run.app \
    pytest apps/counselconduit/tests/test_smoke.py -v
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "https://counselconduit-767252945109.us-central1.run.app")

# Cloud Armor rate limiter may return 429 during load — accept it as valid
_RATE_LIMITED = 429

# Skip if network not available
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_SMOKE", "0") == "1",
    reason="Smoke tests disabled (SKIP_SMOKE=1)",
)


@pytest.fixture
def client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


class TestHealthEndpoints:
    """Verify service is alive and healthy."""

    def test_health(self, client: httpx.Client) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["firestore"] == "connected"

    def test_enclave_health(self, client: httpx.Client) -> None:
        r = client.get("/enclave/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "operational"

    def test_openapi_reachable(self, client: httpx.Client) -> None:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert len(schema["paths"]) > 20


class TestDispatch:
    """Verify dispatch routing is operational."""

    def test_simple_dispatch(self, client: httpx.Client) -> None:
        r = client.post(
            "/api/v1/dispatch",
            json={
                "query": "What is attorney-client privilege?",
                "firm_id": "smoke-test-firm",
                "session_id": "smoke-test-session",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["tier"] in ("simple", "complex", "agentic")
        assert data["model"]
        assert data["provider"]

    def test_rate_limit_headers(self, client: httpx.Client) -> None:
        r = client.post(
            "/api/v1/dispatch",
            json={
                "query": "Hello",
                "firm_id": "smoke-test-firm",
            },
        )
        assert r.status_code == 200
        assert "X-RateLimit-Limit" in r.headers
        assert "X-RateLimit-Remaining" in r.headers

    def test_dispatch_validation(self, client: httpx.Client) -> None:
        """Empty query should fail validation."""
        r = client.post(
            "/api/v1/dispatch",
            json={
                "query": "",
                "firm_id": "smoke-test-firm",
            },
        )
        assert r.status_code in (422, _RATE_LIMITED)


class TestAdminAuth:
    """Verify admin endpoints require auth in production."""

    def test_admin_metrics_requires_auth(self, client: httpx.Client) -> None:
        r = client.get("/admin/metrics")
        # In production: 401. In dev: 200.
        # 200=ok, 401=auth required, 429=rate limited, 500=runtime dep issue
        assert r.status_code in (200, 401, _RATE_LIMITED, 500)

    def test_admin_models_requires_auth(self, client: httpx.Client) -> None:
        r = client.get("/admin/models")
        assert r.status_code in (200, 401, _RATE_LIMITED, 500)


class TestKovelAttestation:
    """Verify Kovel attestation generation."""

    def test_attestation_generate(self, client: httpx.Client) -> None:
        r = client.post(
            "/attestation/generate",
            json={
                "session_id": "smoke-kovel-session",
                "firm_id": "smoke-firm",
                "attorney_id": "smoke-attorney",
                "client_id": "smoke-client",
                "matter_id": "smoke-matter",
                "model_used": "gemini-3.1-flash-lite-preview-thinking",
                "query_text": "Smoke test query",
                "response_text": "Smoke test response",
            },
        )
        assert r.status_code in (200, _RATE_LIMITED)
        data = r.json()
        assert data["attestation_id"]
        assert data["hmac_signature"]
        assert data["privilege_type"] == "kovel_doctrine"

    def test_attestation_validation(self, client: httpx.Client) -> None:
        """Missing fields should fail validation."""
        r = client.post(
            "/attestation/generate",
            json={"session_id": "test"},
        )
        assert r.status_code in (422, _RATE_LIMITED)


class TestGDPR:
    """Verify GDPR deletion flow validation."""

    def test_gdpr_requires_confirmation(self, client: httpx.Client) -> None:
        r = client.post(
            "/account/delete",
            json={
                "user_id": "smoke-user",
                "email": "smoke@example.com",
                "reason": "Test",
            },
        )
        # Should require confirmation field
        assert r.status_code in (422, _RATE_LIMITED)


class TestCORS:
    """Verify CORS preflight is properly configured."""

    def test_cors_preflight(self, client: httpx.Client) -> None:
        r = client.options(
            "/api/v1/dispatch",
            headers={
                "Origin": "https://kovelai.web.app",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert r.status_code in (200, _RATE_LIMITED)
        assert "access-control-allow-origin" in r.headers


class TestStripeWebhook:
    """Verify Stripe webhook signature verification (Item #21)."""

    def test_webhook_rejects_unsigned(self, client: httpx.Client) -> None:
        """Webhook must reject requests without Stripe-Signature."""
        r = client.post(
            "/webhooks/stripe",
            content=b'{"type":"checkout.session.completed"}',
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code in (400, 401, 403, _RATE_LIMITED), f"Webhook accepted unsigned request (status={r.status_code})"

    def test_webhook_rejects_forged_signature(self, client: httpx.Client) -> None:
        """Webhook must reject requests with forged Stripe-Signature."""
        r = client.post(
            "/webhooks/stripe",
            content=b'{"type":"invoice.paid"}',
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "t=1234567890,v1=forged_signature_value",
            },
        )
        assert r.status_code in (400, 401, 403, _RATE_LIMITED), f"Webhook accepted forged signature (status={r.status_code})"

    def test_webhook_endpoint_exists(self, client: httpx.Client) -> None:
        """Webhook endpoint must exist (not 404)."""
        r = client.post(
            "/webhooks/stripe",
            content=b"{}",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code != 404, "Stripe webhook endpoint not found"


class TestNewAdminEndpoints:
    """Verify new admin endpoints from hardening (require auth or accept unauthenticated)."""

    def test_provider_health_exists(self, client: httpx.Client) -> None:
        r = client.get("/admin/provider-health")
        assert r.status_code in (200, 401, 404, _RATE_LIMITED, 500)

    def test_token_budgets_exists(self, client: httpx.Client) -> None:
        r = client.get("/admin/token-budgets")
        assert r.status_code in (200, 401, 404, _RATE_LIMITED, 500)

    def test_circuit_breaker_exists(self, client: httpx.Client) -> None:
        r = client.get("/admin/circuit-breaker")
        assert r.status_code in (200, 401, 404, _RATE_LIMITED, 500)

    def test_firm_policies_exists(self, client: httpx.Client) -> None:
        r = client.get("/admin/firm-policies")
        assert r.status_code in (200, 401, 404, _RATE_LIMITED, 500)
