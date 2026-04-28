# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Stripe Webhook Handler — Unit Tests.

Tests for the HMAC signature verification and webhook event dispatch
in apps/counselconduit/api/stripe_handler.py.

Covers:
    - Valid signature verification
    - Missing/malformed signature rejection
    - Expired timestamp replay protection
    - All 5 event type handlers
    - Unhandled event passthrough
    - Mock reCAPTCHA token fixture for captureLead compatibility
"""

from __future__ import annotations

import hashlib
import hmac as hmac_module
import json
import time

import pytest

# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def webhook_secret() -> str:
    """Fixed test webhook secret."""
    return "whsec_test_secret_key_for_unit_tests"


@pytest.fixture
def mock_recaptcha_token() -> str:
    """Mock reCAPTCHA token for captureLead integration tests."""
    return "03AGdBq24_mock_recaptcha_v3_token_for_testing"


def _make_stripe_signature(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    """Build a valid Stripe-Signature header for testing."""
    if timestamp is None:
        timestamp = int(time.time())
    signed_payload = f"{timestamp}.".encode() + payload
    sig = hmac_module.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


def _make_event(event_type: str, event_id: str = "evt_test_123", **data) -> dict:
    """Build a minimal Stripe event payload."""
    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": data},
    }


# ── Import the module under test ────────────────────────────────────────────

# We import the verification function directly (no FastAPI server needed)
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _import_handler():
    """Lazy import to avoid FastAPI dep issues in test env."""
    try:
        from apps.counselconduit.api.stripe_handler import (
            verify_stripe_signature,
            _handle_checkout_completed,
            _handle_subscription_updated,
            _handle_subscription_deleted,
            _handle_invoice_payment_succeeded,
            _handle_invoice_payment_failed,
            _EVENT_HANDLERS,
        )

        return {
            "verify": verify_stripe_signature,
            "checkout": _handle_checkout_completed,
            "sub_updated": _handle_subscription_updated,
            "sub_deleted": _handle_subscription_deleted,
            "payment_ok": _handle_invoice_payment_succeeded,
            "payment_fail": _handle_invoice_payment_failed,
            "handlers": _EVENT_HANDLERS,
        }
    except ImportError:
        pytest.skip("FastAPI not installed — skipping Stripe handler tests")


# ── Signature Verification Tests ────────────────────────────────────────────


class TestVerifyStripeSignature:
    """Test the HMAC-SHA256 signature verification."""

    def test_valid_signature_passes(self, webhook_secret: str):
        """A correctly signed payload should return the parsed event."""
        handler = _import_handler()
        event = _make_event("checkout.session.completed", customer_email="test@law.com")
        payload = json.dumps(event).encode("utf-8")
        sig = _make_stripe_signature(payload, webhook_secret)

        result = handler["verify"](payload, sig, webhook_secret)
        assert result["type"] == "checkout.session.completed"
        assert result["id"] == "evt_test_123"

    def test_missing_signature_raises_400(self, webhook_secret: str):
        """Empty signature header should raise 400."""
        handler = _import_handler()
        payload = b'{"type":"test"}'

        with pytest.raises(Exception) as exc_info:
            handler["verify"](payload, "", webhook_secret)
        # HTTPException with 400
        assert "400" in str(exc_info.value.status_code) or exc_info.value.status_code == 400

    def test_malformed_signature_raises_400(self, webhook_secret: str):
        """Signature without t= or v1= should raise 400."""
        handler = _import_handler()
        payload = b'{"type":"test"}'

        with pytest.raises(Exception):
            handler["verify"](payload, "garbage_header", webhook_secret)

    def test_wrong_secret_raises_401(self, webhook_secret: str):
        """Signature computed with wrong secret should raise 401."""
        handler = _import_handler()
        event = _make_event("test.event")
        payload = json.dumps(event).encode("utf-8")
        sig = _make_stripe_signature(payload, "whsec_WRONG_secret")

        with pytest.raises(Exception) as exc_info:
            handler["verify"](payload, sig, webhook_secret)
        assert exc_info.value.status_code == 401

    def test_expired_timestamp_raises_401(self, webhook_secret: str):
        """Timestamp older than 300s should be rejected."""
        handler = _import_handler()
        event = _make_event("test.event")
        payload = json.dumps(event).encode("utf-8")
        old_timestamp = int(time.time()) - 600  # 10 min ago
        sig = _make_stripe_signature(payload, webhook_secret, old_timestamp)

        with pytest.raises(Exception) as exc_info:
            handler["verify"](payload, sig, webhook_secret)
        assert exc_info.value.status_code == 401

    def test_invalid_json_raises_400(self, webhook_secret: str):
        """Valid signature but invalid JSON body should raise 400."""
        handler = _import_handler()
        payload = b"not-json-{{"
        sig = _make_stripe_signature(payload, webhook_secret)

        with pytest.raises(Exception) as exc_info:
            handler["verify"](payload, sig, webhook_secret)
        assert exc_info.value.status_code == 400


# ── Event Handler Tests ─────────────────────────────────────────────────────


class TestEventHandlers:
    """Test individual event type handlers."""

    def test_checkout_completed(self):
        handler = _import_handler()
        event = _make_event(
            "checkout.session.completed",
            customer_email="attorney@firm.com",
            subscription="sub_123",
        )
        result = handler["checkout"](event)
        assert result["action"] == "provisioned"
        assert result["email"] == "attorney@firm.com"

    def test_subscription_updated(self):
        handler = _import_handler()
        event = _make_event(
            "customer.subscription.updated",
            id="sub_456",
            status="active",
        )
        result = handler["sub_updated"](event)
        assert result["action"] == "tier_updated"
        assert result["subscription_id"] == "sub_456"

    def test_subscription_deleted(self):
        handler = _import_handler()
        event = _make_event(
            "customer.subscription.deleted",
            id="sub_789",
        )
        result = handler["sub_deleted"](event)
        assert result["action"] == "access_revoked"

    def test_invoice_payment_succeeded(self):
        handler = _import_handler()
        event = _make_event(
            "invoice.payment_succeeded",
            amount_paid=14900,
            customer="cus_abc",
        )
        result = handler["payment_ok"](event)
        assert result["action"] == "payment_recorded"
        assert result["amount_cents"] == 14900

    def test_invoice_payment_failed(self):
        handler = _import_handler()
        event = _make_event(
            "invoice.payment_failed",
            customer="cus_def",
            attempt_count=3,
        )
        result = handler["payment_fail"](event)
        assert result["action"] == "payment_failed"
        assert result["attempt"] == 3

    def test_all_5_event_types_have_handlers(self):
        handler = _import_handler()
        expected_types = {
            "checkout.session.completed",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
        }
        assert set(handler["handlers"].keys()) == expected_types

    def test_unhandled_event_returns_none(self):
        handler = _import_handler()
        result = handler["handlers"].get("unknown.event.type")
        assert result is None


# ── captureLead Mock reCAPTCHA Fixture ──────────────────────────────────────


class TestCaptureLeadFixture:
    """Verify the mock reCAPTCHA token fixture is available for integration tests."""

    def test_mock_recaptcha_token_format(self, mock_recaptcha_token: str):
        """Token fixture should match expected format prefix."""
        assert mock_recaptcha_token.startswith("03AGdBq24")
        assert len(mock_recaptcha_token) > 10
