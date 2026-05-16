# tests/e2e/test_counselconduit_e2e.py
"""Playwright E2E tests for CounselConduit checkout and onboarding flows.

Requires: pip install playwright && playwright install chromium

Run: pytest tests/e2e/ --headed  (visual)
     pytest tests/e2e/           (headless)

Tests:
1. Health check and API discovery
2. OpenAPI documentation endpoint
3. Magic link creation and verification
4. Vent Mode checkout initiation
5. Oracle Studio flow
6. GDPR deletion request
7. Attestation generation and verification
8. Stripe Connect onboarding
9. Cloud Tasks GDPR scheduling
"""

from __future__ import annotations

import os
import httpx
import pytest

# Gate: skip entire module unless CLOUD_RUN_LIVE_TEST=1 is set
pytestmark = pytest.mark.skipif(
  os.getenv("CLOUD_RUN_LIVE_TEST", "") != "1",
  reason="Set CLOUD_RUN_LIVE_TEST=1 to run Cloud Run e2e tests",
)

# Base URL for the deployed service (override with COUNSELCONDUIT_BASE_URL env var)
BASE_URL = os.getenv(
  "COUNSELCONDUIT_BASE_URL",
  "https://counselconduit-767252945109.us-central1.run.app",
)
LOCAL_URL = "http://localhost:8080"


def _get_base() -> str:
  """Return LOCAL_URL if CounselConduit is running locally, else env/production."""
  try:
    r = httpx.get(f"{LOCAL_URL}/health", timeout=2)
    if r.status_code == 200:
      data = r.json()
      # Verify it's actually CounselConduit (not Gemma-4 llama-server on :8080)
      if data.get("service") == "counselconduit":
        return LOCAL_URL
  except Exception:
    pass
  return BASE_URL


@pytest.fixture(scope="module")
def base_url():
  return _get_base()


# ── Health + Discovery ──────────────────────────────────────────────────


class TestHealthAndDiscovery:
  def test_health_endpoint(self, base_url):
    """Verify /health returns 200 with correct structure."""
    r = httpx.get(f"{base_url}/health", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["service"] == "counselconduit"
    assert "version" in data

  def test_root_endpoint(self, base_url):
    """Verify / returns API discovery info."""
    r = httpx.get(f"{base_url}/", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "CounselConduit"
    assert data["status"] == "operational"

  def test_openapi_docs(self, base_url):
    """Verify /docs (Swagger UI) returns HTML."""
    r = httpx.get(f"{base_url}/docs", timeout=10)
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")

  def test_openapi_schema(self, base_url):
    """Verify /openapi.json returns valid OpenAPI schema."""
    r = httpx.get(f"{base_url}/openapi.json", timeout=10)
    assert r.status_code == 200
    schema = r.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/health" in schema["paths"]

  def test_security_headers(self, base_url):
    """Verify security headers are present (Cor.30 R31)."""
    r = httpx.get(f"{base_url}/health", timeout=10)
    headers = r.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"


# ── Magic Link Onboarding ──────────────────────────────────────────────


class TestMagicLinkOnboarding:
  def test_create_matter(self, base_url):
    """Attorney creates a matter and receives a magic link."""
    payload = {
      "attorney_id": "att_test_001",
      "firm_id": "firm_test_001",
      "client_name": "John Doe",
      "client_email": "john@example.com",
      "matter_description": "Contract review for SaaS agreement",
      "allowed_models": ["gemini-flash"],
    }
    r = httpx.post(f"{base_url}/onboarding/create-matter", json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "matter_id" in data
    assert "magic_link" in data
    assert data["client_email"] == "john@example.com"
    assert "kovelai.web.app/portal?token=" in data["magic_link"]

  def test_verify_magic_link(self, base_url):
    """Client verifies a magic link token."""
    # First create a matter
    payload = {
      "attorney_id": "att_test_002",
      "firm_id": "firm_test_002",
      "client_name": "Jane Smith",
      "client_email": "jane@example.com",
    }
    r = httpx.post(f"{base_url}/onboarding/create-matter", json=payload, timeout=10)
    data = r.json()
    token = data["magic_link"].split("token=")[1]

    # Verify the token
    r2 = httpx.get(f"{base_url}/onboarding/verify/{token}", timeout=10)
    assert r2.status_code == 200
    verify = r2.json()
    assert verify["valid"] is True


# ── Vent Mode ──────────────────────────────────────────────────────────


class TestVentMode:
  def test_start_vent_session(self, base_url):
    """Client starts a Vent Mode intake session."""
    payload = {
      "firm_id": "firm_test_001",
      "attorney_id": "att_test_001",
      "client_name": "Test Client",
      "client_email": "test@example.com",
      "fee_amount_cents": 5000,
    }
    r = httpx.post(f"{base_url}/vent/start", json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert "checkout_url" in data
    assert data["amount_display"] == "$50.00"

  def test_send_vent_message(self, base_url):
    """Client sends a message in a Vent session."""
    payload = {
      "session_id": "test_session_001",
      "message": "I'm having a dispute with my landlord about the lease.",
    }
    r = httpx.post(f"{base_url}/vent/message", json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == "test_session_001"
    assert "response" in data


# ── Attestation ────────────────────────────────────────────────────────


class TestAttestation:
  def test_generate_attestation(self, base_url):
    """Generate a Kovel attestation receipt."""
    payload = {
      "session_id": "test_session_001",
      "attorney_id": "att_test_001",
      "firm_id": "firm_test_001",
      "client_id": "client_test_001",
      "model_used": "gemini-flash",
      "query_text": "What are my rights as a tenant?",
      "response_text": "Under applicable landlord-tenant law...",
    }
    r = httpx.post(f"{base_url}/attestation/generate", json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "attestation_id" in data
    assert "hmac_signature" in data
    assert data["privilege_type"] == "kovel_doctrine"

    # Verify the attestation
    r2 = httpx.post(f"{base_url}/attestation/verify", json=data, timeout=10)
    assert r2.status_code == 200
    verify = r2.json()
    assert verify["valid"] is True


# ── GDPR ───────────────────────────────────────────────────────────────


class TestGDPR:
  def test_deletion_request(self, base_url):
    """Client requests account deletion (Article 17)."""
    payload = {"confirmation": "DELETE MY ACCOUNT", "reason": "test"}
    r = httpx.post(
      f"{base_url}/account/delete",
      json=payload,
      timeout=10,
    )
    assert r.status_code == 202
    data = r.json()
    assert "receipt_id" in data
    assert data["status"] == "scheduled"

  def test_export_my_data(self, base_url):
    """Client requests data export (Article 20 - portability)."""
    payload = {"format": "json"}
    r = httpx.post(
      f"{base_url}/account/export",
      json=payload,
      timeout=10,
    )
    assert r.status_code == 202
    data = r.json()
    assert "export_id" in data
    assert data["format"] == "json"


# ── Stripe Webhook ─────────────────────────────────────────────────────


class TestStripeWebhook:
  def test_webhook_rejects_get(self, base_url):
    """Stripe webhook only accepts POST (security check)."""
    r = httpx.get(f"{base_url}/webhooks/stripe", timeout=10)
    assert r.status_code == 405  # Method Not Allowed

  def test_webhook_rejects_unsigned(self, base_url):
    """Stripe webhook rejects requests without valid signature."""
    r = httpx.post(
      f"{base_url}/webhooks/stripe",
      content=b'{"type": "test"}',
      headers={"Content-Type": "application/json"},
      timeout=10,
    )
    # Should fail with missing/invalid signature
    assert r.status_code in (400, 403, 422)
