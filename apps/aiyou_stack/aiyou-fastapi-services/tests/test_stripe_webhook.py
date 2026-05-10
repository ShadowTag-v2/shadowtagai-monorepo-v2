#!/usr/bin/env python3
"""Unit tests for Stripe Webhook Handler.

Tests cover:
    - Signature verification (valid, invalid, expired)
    - Idempotency deduplication
    - Event routing (subscription.created, invoice.paid, etc.)
    - Malformed payload handling
"""

import hashlib
import hmac
import json
import time

import pytest
from fastapi import HTTPException

# Import the handler module
from app.webhooks.stripe_handler import (
    _is_duplicate,
    _processed_events,
    verify_stripe_signature,
)

# ──────────────────────────────────────────────────────
# Test Configuration
# ──────────────────────────────────────────────────────

WEBHOOK_SECRET = "whsec_test_secret_for_unit_tests_only"


def _make_signed_payload(
    payload_dict: dict,
    secret: str = WEBHOOK_SECRET,
    timestamp: int | None = None,
) -> tuple[bytes, str]:
    """Construct a signed payload and Stripe-Signature header.

    Returns:
        Tuple of (raw_payload_bytes, signature_header_string).
    """
    if timestamp is None:
        timestamp = int(time.time())

    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    signed_payload = f"{timestamp}.".encode() + payload_bytes
    sig = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    header = f"t={timestamp},v1={sig}"
    return payload_bytes, header


def _sample_event(event_type: str = "customer.subscription.created") -> dict:
    """Return a minimal valid Stripe event payload."""
    return {
        "id": f"evt_test_{event_type.replace('.', '_')}_{int(time.time())}",
        "type": event_type,
        "data": {
            "object": {
                "id": "sub_test123",
                "customer": "cus_test456",
                "plan": {
                    "id": "price_vanguard_149",
                    "amount": 14900,
                },
                "status": "active",
            },
        },
        "created": int(time.time()),
    }


# ──────────────────────────────────────────────────────
# Signature Verification Tests
# ──────────────────────────────────────────────────────


class TestSignatureVerification:
    """Tests for verify_stripe_signature()."""

    def test_valid_signature(self):
        """Valid payload with correct signature should parse and return event."""
        event = _sample_event()
        payload, header = _make_signed_payload(event)

        result = verify_stripe_signature(payload, header, WEBHOOK_SECRET)

        assert result["id"] == event["id"]
        assert result["type"] == "customer.subscription.created"

    def test_invalid_signature(self):
        """Tampered signature should raise 400."""
        event = _sample_event()
        payload, header = _make_signed_payload(event)

        bad_header = header.replace(header[-8:], "deadbeef")

        with pytest.raises(HTTPException) as exc_info:
            verify_stripe_signature(payload, bad_header, WEBHOOK_SECRET)
        assert exc_info.value.status_code == 400
        assert "verification failed" in exc_info.value.detail.lower()

    def test_wrong_secret(self):
        """Signature computed with different secret should fail."""
        event = _sample_event()
        payload, header = _make_signed_payload(event, secret="whsec_wrong_key")

        with pytest.raises(HTTPException) as exc_info:
            verify_stripe_signature(payload, header, WEBHOOK_SECRET)
        assert exc_info.value.status_code == 400

    def test_expired_timestamp(self):
        """Event older than tolerance window should be rejected."""
        event = _sample_event()
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        payload, header = _make_signed_payload(event, timestamp=old_timestamp)

        with pytest.raises(HTTPException) as exc_info:
            verify_stripe_signature(
                payload,
                header,
                WEBHOOK_SECRET,
                tolerance=300,
            )
        assert exc_info.value.status_code == 400
        assert "too old" in exc_info.value.detail.lower()

    def test_missing_v1_signature(self):
        """Header without v1= field should raise 400."""
        payload = json.dumps(_sample_event()).encode()
        bad_header = f"t={int(time.time())}"

        with pytest.raises(HTTPException) as exc_info:
            verify_stripe_signature(payload, bad_header, WEBHOOK_SECRET)
        assert exc_info.value.status_code == 400

    def test_malformed_json(self):
        """Valid signature but invalid JSON body should raise 400."""
        bad_payload = b"{{not json at all}}"
        timestamp = int(time.time())
        signed = f"{timestamp}.".encode() + bad_payload
        sig = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed,
            hashlib.sha256,
        ).hexdigest()
        header = f"t={timestamp},v1={sig}"

        with pytest.raises(HTTPException) as exc_info:
            verify_stripe_signature(bad_payload, header, WEBHOOK_SECRET)
        assert exc_info.value.status_code == 400
        assert "invalid json" in exc_info.value.detail.lower()


# ──────────────────────────────────────────────────────
# Idempotency Tests
# ──────────────────────────────────────────────────────


class TestIdempotency:
    """Tests for _is_duplicate() deduplication."""

    def setup_method(self):
        """Clear the idempotency store before each test."""
        _processed_events.clear()

    def test_first_event_not_duplicate(self):
        """First occurrence of an event ID should return False."""
        assert _is_duplicate("evt_unique_001") is False

    def test_second_event_is_duplicate(self):
        """Second occurrence of the same event ID should return True."""
        _is_duplicate("evt_dup_001")
        assert _is_duplicate("evt_dup_001") is True

    def test_different_events_not_duplicates(self):
        """Different event IDs should not be treated as duplicates."""
        _is_duplicate("evt_a")
        assert _is_duplicate("evt_b") is False

    def test_expired_entries_cleaned(self):
        """Entries older than TTL should be cleaned up."""
        _processed_events["evt_old"] = time.time() - 100000  # very old
        _is_duplicate("evt_new")
        assert "evt_old" not in _processed_events
        assert "evt_new" in _processed_events


# ──────────────────────────────────────────────────────
# Event Routing Smoke Tests
# ──────────────────────────────────────────────────────


class TestEventRouting:
    """Verify that known event types are routable."""

    KNOWN_EVENTS = [
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
        "checkout.session.completed",
    ]

    @pytest.mark.parametrize("event_type", KNOWN_EVENTS)
    def test_known_event_parses(self, event_type: str):
        """Each known event type should produce a valid signed payload."""
        event = _sample_event(event_type)
        payload, header = _make_signed_payload(event)

        result = verify_stripe_signature(payload, header, WEBHOOK_SECRET)
        assert result["type"] == event_type
        assert result["data"]["object"]["id"] == "sub_test123"
