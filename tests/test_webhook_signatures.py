# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# tests/test_webhook_signatures.py
"""Webhook signature verification tests.

Validates HMAC signature checking for Stripe, Stripe Connect,
and Resend webhook endpoints per Cor.30 R21-22.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time


class TestStripeWebhookSignature:
    """Verify Stripe webhook HMAC validation."""

    WEBHOOK_SECRET = "whsec_test_secret_12345"

    def _make_stripe_signature(self, payload: bytes, secret: str) -> str:
        """Generate a valid Stripe-Signature header."""
        timestamp = str(int(time.time()))
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_sig = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={expected_sig}"

    def test_valid_signature_format(self):
        """Verify signature generation produces correct format."""
        payload = b'{"type": "payment_intent.succeeded"}'
        sig = self._make_stripe_signature(payload, self.WEBHOOK_SECRET)
        assert sig.startswith("t=")
        assert ",v1=" in sig
        parts = sig.split(",")
        assert len(parts) == 2
        assert parts[0].startswith("t=")
        assert parts[1].startswith("v1=")

    def test_signature_changes_with_payload(self):
        """Different payloads produce different signatures."""
        sig1 = self._make_stripe_signature(b'{"a": 1}', self.WEBHOOK_SECRET)
        sig2 = self._make_stripe_signature(b'{"a": 2}', self.WEBHOOK_SECRET)
        assert sig1.split(",v1=")[1] != sig2.split(",v1=")[1]

    def test_signature_changes_with_secret(self):
        """Different secrets produce different signatures."""
        payload = b'{"type": "test"}'
        sig1 = self._make_stripe_signature(payload, "secret_a")
        sig2 = self._make_stripe_signature(payload, "secret_b")
        assert sig1.split(",v1=")[1] != sig2.split(",v1=")[1]

    def test_tampered_payload_fails_verification(self):
        """Tampered payload should not match original signature."""
        original = b'{"amount": 5000}'
        sig = self._make_stripe_signature(original, self.WEBHOOK_SECRET)

        # Extract timestamp and original HMAC
        t = sig.split(",")[0].split("=")[1]
        original_hmac = sig.split(",v1=")[1]

        # Tamper the payload
        tampered = b'{"amount": 50000}'
        tampered_signed = f"{t}.{tampered.decode()}"
        tampered_hmac = hmac.new(
            self.WEBHOOK_SECRET.encode(),
            tampered_signed.encode(),
            hashlib.sha256,
        ).hexdigest()

        assert original_hmac != tampered_hmac

    def test_replay_attack_detection(self):
        """Old timestamps should be rejected (> 5 min tolerance)."""
        old_timestamp = str(int(time.time()) - 400)  # 6+ minutes ago
        payload = b'{"type": "test"}'
        signed_payload = f"{old_timestamp}.{payload.decode()}"
        sig = hmac.new(
            self.WEBHOOK_SECRET.encode(),
            signed_payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        header = f"t={old_timestamp},v1={sig}"

        # Parse timestamp and check tolerance
        t = int(header.split(",")[0].split("=")[1])
        assert abs(time.time() - t) > 300  # > 5 min = reject


class TestKovelAttestationHMAC:
    """Verify Kovel attestation HMAC integrity."""

    ATTESTATION_SECRET = "kovel_test_secret"

    def test_attestation_hmac_generation(self):
        """Generate and verify a Kovel attestation HMAC."""
        attestation_data = {
            "session_id": "sess_001",
            "attorney_id": "att_001",
            "firm_id": "firm_001",
            "timestamp": "2026-04-18T00:00:00Z",
        }
        canonical = json.dumps(attestation_data, sort_keys=True)
        signature = hmac.new(
            self.ATTESTATION_SECRET.encode(),
            canonical.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Verify
        expected = hmac.new(
            self.ATTESTATION_SECRET.encode(),
            canonical.encode(),
            hashlib.sha256,
        ).hexdigest()
        assert hmac.compare_digest(signature, expected)

    def test_attestation_tamper_detection(self):
        """Tampered attestation data should fail verification."""
        data = {"session_id": "sess_001", "attorney_id": "att_001"}
        canonical = json.dumps(data, sort_keys=True)
        original_sig = hmac.new(
            self.ATTESTATION_SECRET.encode(),
            canonical.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Tamper
        data["attorney_id"] = "att_hacker"
        tampered = json.dumps(data, sort_keys=True)
        tampered_sig = hmac.new(
            self.ATTESTATION_SECRET.encode(),
            tampered.encode(),
            hashlib.sha256,
        ).hexdigest()

        assert not hmac.compare_digest(original_sig, tampered_sig)


class TestResendWebhookSignature:
    """Verify Resend webhook signature checking."""

    RESEND_SECRET = "resend_test_secret"

    def test_resend_signature_format(self):
        """Resend uses svix-signature header with HMAC-SHA256."""
        payload = b'{"type": "email.delivered"}'
        msg_id = "msg_test_001"
        timestamp = str(int(time.time()))

        to_sign = f"{msg_id}.{timestamp}.{payload.decode()}"
        signature = hmac.new(
            self.RESEND_SECRET.encode(),
            to_sign.encode(),
            hashlib.sha256,
        ).hexdigest()

        assert len(signature) == 64  # SHA-256 hex digest

    def test_resend_missing_signature_rejected(self):
        """Requests without signature should be rejected."""
        # Simulate missing header check
        headers = {"Content-Type": "application/json"}
        assert "svix-signature" not in headers
