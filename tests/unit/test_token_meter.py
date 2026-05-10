"""Unit tests for Token Budget Meter.

Tests cover:
- Tier daily limits mapping
- TokenMeterResponse model
- Status thresholds (ok, warning, critical, exhausted)
"""

from __future__ import annotations

import pytest


class TestTierDailyLimits:
  """Tests for TIER_DAILY_LIMITS constant."""

  def test_trial_limit(self):
    from apps.counselconduit.api.token_meter import TIER_DAILY_LIMITS

    assert TIER_DAILY_LIMITS["trial"] == 10_000

  def test_solo_limit(self):
    from apps.counselconduit.api.token_meter import TIER_DAILY_LIMITS

    assert TIER_DAILY_LIMITS["solo"] == 100_000

  def test_professional_limit(self):
    from apps.counselconduit.api.token_meter import TIER_DAILY_LIMITS

    assert TIER_DAILY_LIMITS["professional"] == 500_000

  def test_enterprise_limit(self):
    from apps.counselconduit.api.token_meter import TIER_DAILY_LIMITS

    assert TIER_DAILY_LIMITS["enterprise"] == 2_000_000

  def test_all_tiers_present(self):
    from apps.counselconduit.api.token_meter import TIER_DAILY_LIMITS

    assert set(TIER_DAILY_LIMITS.keys()) == {
      "trial",
      "solo",
      "professional",
      "enterprise",
    }


class TestTokenMeterResponse:
  """Tests for TokenMeterResponse model."""

  def test_ok_status(self):
    from apps.counselconduit.api.token_meter import TokenMeterResponse

    resp = TokenMeterResponse(
      firm_id="f1",
      tier="trial",
      budget_limit=10000,
      budget_used=1000,
      budget_remaining=9000,
      usage_pct=10.0,
      status="ok",
      reset_at="2026-01-01T00:00:00+00:00",
    )
    assert resp.status == "ok"
    assert resp.warning_threshold_pct == 80.0
    assert resp.critical_threshold_pct == 95.0

  def test_exhausted_status(self):
    from apps.counselconduit.api.token_meter import TokenMeterResponse

    resp = TokenMeterResponse(
      firm_id="f1",
      tier="trial",
      budget_limit=10000,
      budget_used=10000,
      budget_remaining=0,
      usage_pct=100.0,
      status="exhausted",
      reset_at="2026-01-01T00:00:00+00:00",
    )
    assert resp.budget_remaining == 0


class TestTokenMeterEndpoint:
  """Tests for the token_meter endpoint function."""

  @pytest.mark.asyncio
  async def test_default_trial_tier(self):
    from apps.counselconduit.api.token_meter import token_meter

    result = await token_meter(firm_id="test_firm")
    assert result.tier == "trial"
    assert result.budget_limit == 10_000
    assert result.status == "ok"
    assert result.budget_used == 0  # Firestore unavailable fallback

  @pytest.mark.asyncio
  async def test_enterprise_tier(self):
    from apps.counselconduit.api.token_meter import token_meter

    result = await token_meter(firm_id="test_firm", x_user_tier="enterprise")
    assert result.budget_limit == 2_000_000
    assert result.tier == "enterprise"

  @pytest.mark.asyncio
  async def test_unknown_tier_defaults_to_trial(self):
    from apps.counselconduit.api.token_meter import token_meter

    result = await token_meter(firm_id="test_firm", x_user_tier="nonexistent")
    assert result.budget_limit == 10_000  # Falls back to trial

  @pytest.mark.asyncio
  async def test_reset_at_is_iso8601(self):
    from apps.counselconduit.api.token_meter import token_meter

    result = await token_meter(firm_id="test_firm")
    assert "T" in result.reset_at
    assert "00:00:00" in result.reset_at
