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
