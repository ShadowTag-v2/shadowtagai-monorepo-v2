# tests/test_stripe_config.py
"""Stripe Configuration Validation Suite.

Validates live Stripe product IDs, price IDs, tier mapping integrity,
webhook configuration, and token limits against AGENTS.md doctrine.
Account: acct_1Syh9JEHnWpykeMi (US, live mode).
"""

from __future__ import annotations


from apps.counselconduit.api.stripe_config import (
    COUPON_BETA_50,
    PORTAL_CONFIG_ID,
    PRICE_ENT_MONTHLY,
    PRICE_PRO_ANNUAL,
    PRICE_PRO_MONTHLY,
    PRODUCT_ENTERPRISE,
    PRODUCT_PROFESSIONAL,
    PRODUCT_TRIAL,
    TIER_PRICES,
    TIER_TOKEN_LIMITS,
    WEBHOOK_ENDPOINT_ID,
    WEBHOOK_URL,
)


class TestProductIDs:
    """Verify all product IDs match Stripe dashboard."""

    def test_trial_product_id(self):
        assert PRODUCT_TRIAL == "prod_UM2XwCF1byjegL"

    def test_professional_product_id(self):
        assert PRODUCT_PROFESSIONAL == "prod_UM2X10cpyay52e"

    def test_enterprise_product_id(self):
        assert PRODUCT_ENTERPRISE == "prod_UM2XMVp9Er7A0i"

    def test_product_ids_are_unique(self):
        products = [PRODUCT_TRIAL, PRODUCT_PROFESSIONAL, PRODUCT_ENTERPRISE]
        assert len(products) == len(set(products))

    def test_product_ids_prefix(self):
        """All Stripe product IDs must start with 'prod_'."""
        for pid in [PRODUCT_TRIAL, PRODUCT_PROFESSIONAL, PRODUCT_ENTERPRISE]:
            assert pid.startswith("prod_"), f"Invalid product ID prefix: {pid}"


class TestPriceIDs:
    """Verify all price IDs and their mappings."""

    def test_pro_monthly_price_id(self):
        assert PRICE_PRO_MONTHLY == "price_1TNKSREHnWpykeMiRMDlVgLl"

    def test_pro_annual_price_id(self):
        assert PRICE_PRO_ANNUAL == "price_1TNKSjEHnWpykeMi0S9GCVjy"

    def test_enterprise_monthly_price_id(self):
        assert PRICE_ENT_MONTHLY == "price_1TNKSREHnWpykeMi8mrDf4rI"

    def test_price_ids_are_unique(self):
        prices = [PRICE_PRO_MONTHLY, PRICE_PRO_ANNUAL, PRICE_ENT_MONTHLY]
        assert len(prices) == len(set(prices))

    def test_price_ids_prefix(self):
        """All Stripe price IDs must start with 'price_'."""
        for pid in [PRICE_PRO_MONTHLY, PRICE_PRO_ANNUAL, PRICE_ENT_MONTHLY]:
            assert pid.startswith("price_"), f"Invalid price ID prefix: {pid}"


class TestTierMapping:
    """Verify tier → price mapping is complete and correct."""

    def test_tier_prices_contains_pro_monthly(self):
        assert "professional_monthly" in TIER_PRICES
        assert TIER_PRICES["professional_monthly"] == PRICE_PRO_MONTHLY

    def test_tier_prices_contains_pro_annual(self):
        assert "professional_annual" in TIER_PRICES
        assert TIER_PRICES["professional_annual"] == PRICE_PRO_ANNUAL

    def test_tier_prices_contains_enterprise(self):
        assert "enterprise_monthly" in TIER_PRICES
        assert TIER_PRICES["enterprise_monthly"] == PRICE_ENT_MONTHLY

    def test_tier_prices_count(self):
        """Exactly 3 tier→price mappings (no orphans)."""
        assert len(TIER_PRICES) == 3

    def test_all_tier_prices_are_valid_stripe_ids(self):
        for tier, price_id in TIER_PRICES.items():
            assert price_id.startswith("price_"), f"Tier {tier} has invalid price: {price_id}"


class TestTokenLimits:
    """Verify token limits per tier are sane."""

    def test_trial_limit(self):
        assert TIER_TOKEN_LIMITS["trial"] == 10_000

    def test_professional_limit(self):
        assert TIER_TOKEN_LIMITS["professional"] == 100_000

    def test_enterprise_limit(self):
        assert TIER_TOKEN_LIMITS["enterprise"] == 1_000_000

    def test_limits_are_ascending(self):
        """Trial < Pro < Enterprise."""
        assert TIER_TOKEN_LIMITS["trial"] < TIER_TOKEN_LIMITS["professional"]
        assert TIER_TOKEN_LIMITS["professional"] < TIER_TOKEN_LIMITS["enterprise"]

    def test_limits_count(self):
        assert len(TIER_TOKEN_LIMITS) == 3


class TestWebhookConfig:
    """Verify webhook and portal configuration."""

    def test_webhook_endpoint_id(self):
        assert WEBHOOK_ENDPOINT_ID == "we_1TNKSjEHnWpykeMiQZqmpy3X"

    def test_webhook_url_is_https(self):
        assert WEBHOOK_URL.startswith("https://")

    def test_webhook_url_target(self):
        assert WEBHOOK_URL == "https://counselconduit-api.run.app/webhooks/stripe"

    def test_portal_config_id(self):
        assert PORTAL_CONFIG_ID == "bpc_1TNKSjEHnWpykeMi0qQPoaHm"

    def test_portal_config_prefix(self):
        assert PORTAL_CONFIG_ID.startswith("bpc_")

    def test_coupon_code(self):
        assert COUPON_BETA_50 == "3wseBY7Z"
