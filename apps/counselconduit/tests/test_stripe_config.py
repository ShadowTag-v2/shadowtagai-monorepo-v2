# apps/counselconduit/tests/test_stripe_config.py
"""Unit tests for Stripe configuration module.

Validates:
- All product IDs match expected Stripe format
- All price IDs match expected Stripe format
- Tier → Price mapping is complete and consistent
- Token limits are sane and ordered
- No duplicate IDs across products/prices
- Webhook URL points to correct domain
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# Add parent to sys.path for import resolution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.stripe_config import (
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


# ── ID Format Validation ──────────────────────────────────────────────────


class TestStripeIDFormats:
  """Verify all Stripe IDs match the expected format patterns."""

  _PRODUCT_RE = re.compile(r"^prod_[A-Za-z0-9]{14,}$")
  _PRICE_RE = re.compile(r"^price_[A-Za-z0-9]{24,}$")
  _WEBHOOK_RE = re.compile(r"^we_[A-Za-z0-9]{24,}$")
  _PORTAL_RE = re.compile(r"^bpc_[A-Za-z0-9]{24,}$")

  @pytest.mark.parametrize(
    "product_id,name",
    [
      (PRODUCT_TRIAL, "trial"),
      (PRODUCT_PROFESSIONAL, "professional"),
      (PRODUCT_ENTERPRISE, "enterprise"),
    ],
  )
  def test_product_id_format(self, product_id: str, name: str) -> None:
    """Product IDs must match Stripe's prod_ prefix format."""
    assert self._PRODUCT_RE.match(product_id), (
      f"{name} product ID '{product_id}' does not match expected format"
    )

  @pytest.mark.parametrize(
    "price_id,name",
    [
      (PRICE_PRO_MONTHLY, "pro_monthly"),
      (PRICE_PRO_ANNUAL, "pro_annual"),
      (PRICE_ENT_MONTHLY, "ent_monthly"),
    ],
  )
  def test_price_id_format(self, price_id: str, name: str) -> None:
    """Price IDs must match Stripe's price_ prefix format."""
    assert self._PRICE_RE.match(price_id), (
      f"{name} price ID '{price_id}' does not match expected format"
    )

  def test_webhook_endpoint_id_format(self) -> None:
    """Webhook endpoint ID must match Stripe's we_ prefix format."""
    assert self._WEBHOOK_RE.match(WEBHOOK_ENDPOINT_ID), (
      f"Webhook ID '{WEBHOOK_ENDPOINT_ID}' does not match expected format"
    )

  def test_portal_config_id_format(self) -> None:
    """Portal config ID must match Stripe's bpc_ prefix format."""
    assert self._PORTAL_RE.match(PORTAL_CONFIG_ID), (
      f"Portal ID '{PORTAL_CONFIG_ID}' does not match expected format"
    )


# ── Tier Mapping Completeness ──────────────────────────────────────────────


class TestTierPriceMapping:
  """Verify the tier → price mapping is complete and correct."""

  def test_all_expected_tiers_present(self) -> None:
    """All expected tier keys must exist in TIER_PRICES."""
    expected = {"professional_monthly", "professional_annual", "enterprise_monthly"}
    assert set(TIER_PRICES.keys()) == expected

  def test_pro_monthly_maps_correctly(self) -> None:
    """Professional monthly maps to the correct price ID."""
    assert TIER_PRICES["professional_monthly"] == PRICE_PRO_MONTHLY

  def test_pro_annual_maps_correctly(self) -> None:
    """Professional annual maps to the correct price ID."""
    assert TIER_PRICES["professional_annual"] == PRICE_PRO_ANNUAL

  def test_ent_monthly_maps_correctly(self) -> None:
    """Enterprise monthly maps to the correct price ID."""
    assert TIER_PRICES["enterprise_monthly"] == PRICE_ENT_MONTHLY

  def test_no_duplicate_price_ids(self) -> None:
    """Each tier must map to a unique price ID."""
    price_values = list(TIER_PRICES.values())
    assert len(price_values) == len(set(price_values)), "Duplicate price IDs detected"


# ── Token Limits ──────────────────────────────────────────────────────────


class TestTierTokenLimits:
  """Verify token limits are sane and properly ordered."""

  def test_all_tiers_have_limits(self) -> None:
    """All tiers must have token limits defined."""
    expected = {"trial", "professional", "enterprise"}
    assert set(TIER_TOKEN_LIMITS.keys()) == expected

  def test_trial_lowest(self) -> None:
    """Trial tier must have the lowest token limit."""
    assert TIER_TOKEN_LIMITS["trial"] < TIER_TOKEN_LIMITS["professional"]

  def test_professional_middle(self) -> None:
    """Professional tier must be between trial and enterprise."""
    assert (
      TIER_TOKEN_LIMITS["trial"]
      < TIER_TOKEN_LIMITS["professional"]
      < TIER_TOKEN_LIMITS["enterprise"]
    )

  def test_enterprise_highest(self) -> None:
    """Enterprise tier must have the highest token limit."""
    assert TIER_TOKEN_LIMITS["enterprise"] > TIER_TOKEN_LIMITS["professional"]

  @pytest.mark.parametrize("tier", ["trial", "professional", "enterprise"])
  def test_positive_limits(self, tier: str) -> None:
    """All token limits must be positive integers."""
    limit = TIER_TOKEN_LIMITS[tier]
    assert isinstance(limit, int)
    assert limit > 0

  def test_enterprise_is_1m(self) -> None:
    """Enterprise tier must be 1M tokens per CISO pitch."""
    assert TIER_TOKEN_LIMITS["enterprise"] == 1_000_000


# ── No Duplicate IDs ──────────────────────────────────────────────────────


class TestNoDuplicates:
  """Ensure no duplicate Stripe IDs across all constants."""

  def test_unique_product_ids(self) -> None:
    """All product IDs must be unique."""
    products = [PRODUCT_TRIAL, PRODUCT_PROFESSIONAL, PRODUCT_ENTERPRISE]
    assert len(products) == len(set(products))

  def test_unique_price_ids(self) -> None:
    """All price IDs must be unique."""
    prices = [PRICE_PRO_MONTHLY, PRICE_PRO_ANNUAL, PRICE_ENT_MONTHLY]
    assert len(prices) == len(set(prices))

  def test_products_and_prices_disjoint(self) -> None:
    """Product IDs and price IDs must not overlap."""
    products = {PRODUCT_TRIAL, PRODUCT_PROFESSIONAL, PRODUCT_ENTERPRISE}
    prices = {PRICE_PRO_MONTHLY, PRICE_PRO_ANNUAL, PRICE_ENT_MONTHLY}
    assert products.isdisjoint(prices)


# ── Webhook Configuration ─────────────────────────────────────────────────


class TestWebhookConfig:
  """Verify webhook configuration is correct."""

  def test_webhook_url_is_https(self) -> None:
    """Webhook URL must use HTTPS."""
    assert WEBHOOK_URL.startswith("https://")

  def test_webhook_url_domain(self) -> None:
    """Webhook URL must point to counselconduit API domain."""
    assert "counselconduit" in WEBHOOK_URL

  def test_webhook_url_path(self) -> None:
    """Webhook URL must point to /webhooks/stripe endpoint."""
    assert WEBHOOK_URL.endswith("/webhooks/stripe")


# ── Coupon Configuration ──────────────────────────────────────────────────


class TestCouponConfig:
  """Verify coupon configuration."""

  def test_beta_coupon_is_string(self) -> None:
    """Beta coupon code must be a non-empty string."""
    assert isinstance(COUPON_BETA_50, str)
    assert len(COUPON_BETA_50) > 0

  def test_beta_coupon_no_spaces(self) -> None:
    """Coupon code must not contain spaces."""
    assert " " not in COUPON_BETA_50
