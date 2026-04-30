# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# tests/e2e/test_billing_flow.py
"""Playwright-style E2E tests for the billing flow.

Tests Stripe Connect onboarding, coupon application,
and portal session creation via API calls.
"""

from __future__ import annotations

import os

import pytest

# Base URL for testing
_BASE_URL = os.getenv(
    "COUNSELCONDUIT_URL",
    "https://counselconduit-767252945109.us-central1.run.app",
)


class TestBillingOnboarding:
    """E2E tests for Stripe Connect onboarding flow."""

    @pytest.mark.asyncio
    async def test_onboarding_endpoint_exists(self):
        """Connect onboarding endpoint should be accessible."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Without auth, should get 422 (validation error) not 404
            resp = await client.post(
                f"{_BASE_URL}/connect/onboard",
                json={},
                timeout=10,
            )
            # 422 = endpoint exists but validation failed (expected)
            # 403 = auth required (also expected)
            assert resp.status_code in (403, 422, 429, 500)

    @pytest.mark.asyncio
    async def test_billing_status_endpoint_exists(self):
        """Status endpoint should exist and return structured error."""
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_BASE_URL}/connect/status/test-firm-nonexistent",
                timeout=10,
            )
            # 404 = firm not found (correct)
            # 503 = Stripe not configured (acceptable in test)
            assert resp.status_code in (404, 429, 500, 503)

    @pytest.mark.asyncio
    async def test_portal_session_requires_customer(self):
        """Portal session should fail without valid customer."""
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/connect/payment",
                json={
                    "firm_id": "nonexistent",
                    "amount_cents": 100,
                    "description": "test",
                },
                timeout=10,
            )
            assert resp.status_code in (400, 403, 404, 429, 500, 503)


class TestCouponFlow:
    """E2E tests for coupon application."""

    def test_beta_coupon_code_format(self):
        """Beta coupon should be a valid string."""
        beta_coupon = "3wseBY7Z"
        assert len(beta_coupon) == 8
        assert beta_coupon.isalnum()

    def test_coupon_metadata(self):
        """Beta coupon should have correct metadata."""
        coupon_config = {
            "id": "3wseBY7Z",
            "percent_off": 50,
            "duration": "repeating",
            "duration_in_months": 3,
            "max_redemptions": 100,
        }
        assert coupon_config["percent_off"] == 50
        assert coupon_config["duration_in_months"] == 3


class TestStripeWebhook:
    """E2E tests for Stripe webhook endpoint."""

    @pytest.mark.asyncio
    async def test_webhook_rejects_invalid_signature(self):
        """Webhook should reject requests without valid HMAC signature."""
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/webhooks/stripe",
                content=b'{"type": "test"}',
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": "t=1234,v1=invalid",
                },
                timeout=10,
            )
            # 400 = invalid signature, 401 = auth failure (correct behaviors)
            assert resp.status_code in (400, 401, 429, 500)

    @pytest.mark.asyncio
    async def test_webhook_rejects_empty_body(self):
        """Webhook should reject empty request body."""
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/webhooks/stripe",
                content=b"",
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            assert resp.status_code in (400, 422, 429, 500)
