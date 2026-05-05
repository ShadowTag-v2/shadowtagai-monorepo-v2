"""Tests for Stripe circuit breaker integration.

Validates that:
1. StripeConnectService methods are gated by the stripe circuit breaker.
2. The stripe_connect_webhook endpoint returns 503 when the breaker is OPEN.
3. Success/failure are correctly recorded against the breaker.
4. Graceful degradation when circuit_breaker is unavailable.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


# ── StripeConnectService Tests ─────────────────────────────────────────


class TestStripeConnectServiceBreaker:
    """Test circuit breaker wiring in StripeConnectService."""

    def _make_service(self) -> object:
        from apps.counselconduit.services.stripe_connect import StripeConnectService

        return StripeConnectService(stripe_secret_key="sk_test_fake")

    @pytest.mark.asyncio
    async def test_create_account_blocked_when_breaker_open(self):
        """When the stripe breaker is OPEN, create_connect_account raises RuntimeError."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = False
        mock_breaker.seconds_until_probe = 42.0

        with patch(
            "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
            return_value=mock_breaker,
        ):
            svc = self._make_service()
            with pytest.raises(RuntimeError, match="Circuit breaker OPEN for stripe"):
                await svc.create_connect_account(tenant_id="t1", firm_name="Test LLP", email="a@b.com")

        mock_breaker.allow_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_onboarding_link_blocked_when_breaker_open(self):
        """When the stripe breaker is OPEN, create_onboarding_link raises RuntimeError."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = False
        mock_breaker.seconds_until_probe = 30.0

        with patch(
            "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
            return_value=mock_breaker,
        ):
            svc = self._make_service()
            with pytest.raises(RuntimeError, match="Circuit breaker OPEN for stripe"):
                await svc.create_onboarding_link("acct_fake123")

    @pytest.mark.asyncio
    async def test_create_subscription_blocked_when_breaker_open(self):
        """When the stripe breaker is OPEN, create_subscription raises RuntimeError."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = False
        mock_breaker.seconds_until_probe = 15.0

        with patch(
            "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
            return_value=mock_breaker,
        ):
            svc = self._make_service()
            with pytest.raises(RuntimeError, match="Circuit breaker OPEN for stripe"):
                await svc.create_subscription(stripe_account_id="acct_fake123", tier="solo")

    @pytest.mark.asyncio
    async def test_create_account_records_success_on_stripe_ok(self):
        """On successful Stripe API call, breaker.record_success() is called."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = True

        mock_account = MagicMock()
        mock_account.id = "acct_test_123"

        mock_stripe = MagicMock()
        mock_stripe.Account.create.return_value = mock_account

        with (
            patch(
                "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
                return_value=mock_breaker,
            ),
            patch.dict(sys.modules, {"stripe": mock_stripe}),
        ):
            svc = self._make_service()
            result = await svc.create_connect_account(tenant_id="t1", firm_name="Test LLP", email="a@b.com")

            assert result.stripe_account_id == "acct_test_123"
            mock_breaker.record_success.assert_called_once()
            mock_breaker.record_failure.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_account_records_failure_on_stripe_error(self):
        """On Stripe API error, breaker.record_failure() is called."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = True

        mock_stripe = MagicMock()
        mock_stripe.Account.create.side_effect = Exception("Stripe down")

        with (
            patch(
                "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
                return_value=mock_breaker,
            ),
            patch.dict(sys.modules, {"stripe": mock_stripe}),
        ):
            svc = self._make_service()
            with pytest.raises(Exception, match="Stripe down"):
                await svc.create_connect_account(tenant_id="t1", firm_name="Test LLP", email="a@b.com")

            mock_breaker.record_failure.assert_called_once()
            mock_breaker.record_success.assert_not_called()

    @pytest.mark.asyncio
    async def test_graceful_degradation_without_breaker(self):
        """When circuit_breaker isn't available, Stripe calls proceed normally."""
        mock_account = MagicMock()
        mock_account.id = "acct_no_breaker"

        mock_stripe = MagicMock()
        mock_stripe.Account.create.return_value = mock_account

        with (
            patch(
                "apps.counselconduit.services.stripe_connect._get_stripe_breaker",
                return_value=None,
            ),
            patch.dict(sys.modules, {"stripe": mock_stripe}),
        ):
            svc = self._make_service()
            result = await svc.create_connect_account(tenant_id="t2", firm_name="NoBreakerLLC", email="c@d.com")
            assert result.stripe_account_id == "acct_no_breaker"


# ── Stripe Connect Webhook Tests ───────────────────────────────────────


class TestStripeConnectWebhookBreaker:
    """Test circuit breaker wiring in stripe_connect_webhook."""

    def test_webhook_returns_503_when_breaker_open(self):
        """When the stripe breaker is OPEN, webhook returns 503."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = False
        mock_breaker.seconds_until_probe = 60.0

        with (
            patch(
                "apps.counselconduit.api.stripe_connect_webhook._get_stripe_breaker",
                return_value=mock_breaker,
            ),
            patch(
                "apps.counselconduit.api.stripe_connect_webhook._CONNECT_WEBHOOK_SECRET",
                "whsec_test",
            ),
        ):
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            from apps.counselconduit.api.stripe_connect_webhook import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)

            response = client.post(
                "/webhooks/stripe-connect",
                content=b"{}",
                headers={"Stripe-Signature": "t=123,v1=abc"},
            )

            assert response.status_code == 503
            assert "circuit breaker" in response.json()["detail"].lower()


# ── Stripe Billing Webhook Circuit Breaker Tests ───────────────────────


class TestStripeBillingWebhookBreaker:
    """Test circuit breaker wiring in the main stripe_handler webhook."""

    def _make_test_client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from apps.counselconduit.api.stripe_handler import router

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_billing_webhook_returns_503_when_breaker_open(self):
        """When the stripe breaker is OPEN, billing webhook returns 503."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = False
        mock_breaker.seconds_until_probe = 45.0

        with patch(
            "apps.counselconduit.api.stripe_handler._get_stripe_breaker",
            return_value=mock_breaker,
        ):
            client = self._make_test_client()
            response = client.post(
                "/webhooks/stripe",
                content=b'{"type":"test"}',
                headers={"Stripe-Signature": "t=123,v1=abc"},
            )

            assert response.status_code == 503
            detail = response.json()["detail"].lower()
            assert "circuit breaker" in detail
            mock_breaker.allow_request.assert_called_once()

    def test_billing_webhook_proceeds_when_breaker_closed(self):
        """When breaker is CLOSED, webhook proceeds to signature verification."""
        mock_breaker = MagicMock()
        mock_breaker.allow_request.return_value = True

        with (
            patch(
                "apps.counselconduit.api.stripe_handler._get_stripe_breaker",
                return_value=mock_breaker,
            ),
            patch(
                "apps.counselconduit.api.stripe_handler._get_webhook_secret",
                return_value="whsec_test_fake",
            ),
        ):
            client = self._make_test_client()
            # Will fail at signature verification, but that proves we passed the breaker gate
            response = client.post(
                "/webhooks/stripe",
                content=b"{}",
                headers={"Stripe-Signature": ""},
            )

            # 400 means it reached signature verification (past breaker gate)
            assert response.status_code == 400
            assert "Stripe-Signature" in response.json()["detail"]

    def test_billing_webhook_works_without_breaker(self):
        """When circuit_breaker is unavailable, webhook still functions."""
        with (
            patch(
                "apps.counselconduit.api.stripe_handler._get_stripe_breaker",
                return_value=None,
            ),
            patch(
                "apps.counselconduit.api.stripe_handler._get_webhook_secret",
                return_value="whsec_test_fake",
            ),
        ):
            client = self._make_test_client()
            response = client.post(
                "/webhooks/stripe",
                content=b"{}",
                headers={"Stripe-Signature": ""},
            )

            # 400 from missing signature — proves graceful degradation
            assert response.status_code == 400


# ── HALF_OPEN → CLOSED Recovery Integration Tests ──────────────────────


class TestStripeHalfOpenRecovery:
    """Integration tests for circuit breaker recovery under simulated Stripe flakiness.

    These tests validate the full state machine: CLOSED → OPEN → HALF_OPEN → CLOSED
    using the real CircuitBreaker implementation (not mocks).
    """

    def _create_stripe_breaker(self, *, failure_threshold=3, reset_timeout_s=0.05):
        """Create a real circuit breaker with short timeout for test speed."""
        from circuit_breaker.breaker import CircuitBreaker, CircuitBreakerState, FailureMode

        return CircuitBreaker(
            service_name="stripe_test",
            failure_threshold=failure_threshold,
            reset_timeout_s=reset_timeout_s,
            failure_mode=FailureMode.CONSECUTIVE,
        ), CircuitBreakerState

    def test_full_recovery_cycle_consecutive_failures(self):
        """CLOSED → (3 failures) → OPEN → (timeout) → HALF_OPEN → (success) → CLOSED."""
        import time

        breaker, State = self._create_stripe_breaker()

        # Start CLOSED
        assert breaker.state == State.CLOSED
        assert breaker.allow_request() is True

        # Simulate 3 consecutive Stripe failures
        for _ in range(3):
            breaker.record_failure()

        # Now OPEN
        assert breaker.state == State.OPEN
        assert breaker.allow_request() is False

        # Wait for reset timeout
        time.sleep(0.06)

        # Should be HALF_OPEN — one probe allowed
        assert breaker.allow_request() is True
        assert breaker.state == State.HALF_OPEN

        # Simulate successful probe (Stripe recovered)
        breaker.record_success()

        # Back to CLOSED
        assert breaker.state == State.CLOSED
        assert breaker.allow_request() is True

    def test_half_open_probe_failure_re_trips(self):
        """HALF_OPEN → (probe fails) → OPEN again."""
        import time

        breaker, State = self._create_stripe_breaker()

        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == State.OPEN

        # Wait for timeout
        time.sleep(0.06)

        # Allow probe
        assert breaker.allow_request() is True
        assert breaker.state == State.HALF_OPEN

        # Probe fails — Stripe still down
        breaker.record_failure()

        # Back to OPEN
        assert breaker.state == State.OPEN
        assert breaker.allow_request() is False

    def test_intermittent_flakiness_recovery(self):
        """Simulate intermittent Stripe failures — breaker should not trip on mixed results."""
        breaker, State = self._create_stripe_breaker(failure_threshold=3)

        # 2 failures + 1 success resets consecutive counter
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_success()  # Resets consecutive failures

        assert breaker.state == State.CLOSED

        # 2 more failures — still under threshold
        breaker.record_failure()
        breaker.record_failure()

        assert breaker.state == State.CLOSED

        # 3rd consecutive failure trips
        breaker.record_failure()
        assert breaker.state == State.OPEN

    def test_sliding_window_recovery(self):
        """Test HALF_OPEN recovery using sliding window failure mode."""
        import time

        from circuit_breaker.breaker import CircuitBreaker, CircuitBreakerState, FailureMode

        breaker = CircuitBreaker(
            service_name="stripe_sliding_test",
            failure_threshold=3,
            reset_timeout_s=0.05,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=1.0,
        )

        # Trip via sliding window
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for reset
        time.sleep(0.06)

        # Probe and recover
        assert breaker.allow_request() is True
        breaker.record_success()

        assert breaker.state == CircuitBreakerState.CLOSED

    def test_concurrent_probe_rejection(self):
        """Only one probe should be allowed in HALF_OPEN — additional requests rejected."""
        import time

        breaker, State = self._create_stripe_breaker()

        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()

        time.sleep(0.06)

        # First probe allowed
        assert breaker.allow_request() is True

        # Second probe should be rejected (one probe at a time)
        assert breaker.allow_request() is False
