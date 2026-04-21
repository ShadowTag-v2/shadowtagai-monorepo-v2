"""Unit tests for NadirClaw 3-tier dispatch model router.

Tests cover:
- Prompt classification (simple/complex/agentic)
- Session pinning with TTL
- Per-tenant quota enforcement
- Fallback chain routing
- Dispatch metrics recording
- FastAPI integration function
"""

from __future__ import annotations

import time

import pytest

from apps.counselconduit.api.model_router import (
    SESSION_PIN_TTL_SECONDS,
    BYOKConfig,
    DispatchTier,
    ModelRequest,
    TenantQuota,
    _dispatch_metrics,
    _fallback_hits,
    _session_pins,
    _tenant_quotas,
    classify_prompt,
    dispatch_request,
    get_dispatch_metrics,
    get_pinned_model,
    get_tenant_quota,
    pin_session_model,
    record_dispatch,
    record_fallback,
    select_model,
)

# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset all global state before each test."""
    _session_pins.clear()
    _tenant_quotas.clear()
    _dispatch_metrics.clear()
    _fallback_hits.clear()
    yield
    _session_pins.clear()
    _tenant_quotas.clear()
    _dispatch_metrics.clear()
    _fallback_hits.clear()


# ── Prompt Classification Tests ──────────────────────────────────────────


class TestClassifyPrompt:
    """Tests for NadirClaw ~10ms prompt classifier."""

    def test_simple_query(self):
        assert classify_prompt("hello") == DispatchTier.SIMPLE

    def test_simple_short_question(self):
        assert classify_prompt("what is tort law?") == DispatchTier.SIMPLE

    def test_complex_explain(self):
        assert classify_prompt("explain the difference between civil and criminal law") == DispatchTier.COMPLEX

    def test_complex_why(self):
        assert classify_prompt("why did the court rule this way?") == DispatchTier.COMPLEX

    def test_complex_how_does(self):
        assert classify_prompt("how does res judicata apply here?") == DispatchTier.COMPLEX

    def test_agentic_analyze(self):
        assert classify_prompt("analyze the contract for liability risks") == DispatchTier.AGENTIC

    def test_agentic_draft(self):
        assert classify_prompt("draft a motion to dismiss") == DispatchTier.AGENTIC

    def test_agentic_tool_prefix(self):
        assert classify_prompt("tool: search case database") == DispatchTier.AGENTIC

    def test_agentic_long_query(self):
        long_query = " ".join(["word"] * 201)
        assert classify_prompt(long_query) == DispatchTier.AGENTIC

    def test_empty_query(self):
        assert classify_prompt("") == DispatchTier.SIMPLE


# ── Session Pinning + TTL Tests ──────────────────────────────────────────


class TestSessionPinning:
    """Tests for session model pinning with 30-min TTL."""

    def test_pin_and_retrieve(self):
        pin_session_model("sess1", "gemini-pro")
        assert get_pinned_model("sess1") == "gemini-pro"

    def test_no_pin(self):
        assert get_pinned_model("nonexistent") is None

    def test_ttl_expiry(self):
        pin_session_model("sess2", "claude-sonnet")
        # Simulate expiry by manipulating the pin timestamp
        _session_pins["sess2"] = ("claude-sonnet", time.time() - SESSION_PIN_TTL_SECONDS - 1)
        assert get_pinned_model("sess2") is None
        assert "sess2" not in _session_pins

    def test_ttl_within_window(self):
        pin_session_model("sess3", "gpt-4-1")
        # Pin just set — should still be valid
        assert get_pinned_model("sess3") == "gpt-4-1"


# ── Tenant Quota Tests ───────────────────────────────────────────────────


class TestTenantQuota:
    """Tests for per-tenant request quotas (noisy neighbor protection)."""

    def test_default_quota(self):
        quota = get_tenant_quota("firm-001")
        assert quota.max_rpm == 60
        assert quota.max_daily == 5000

    def test_within_quota(self):
        quota = get_tenant_quota("firm-002")
        assert quota.is_within_quota("trial") is True

    def test_rpm_exceeded(self):
        quota = get_tenant_quota("firm-003")
        quota.current_rpm = 25  # trial limit = 20
        assert quota.is_within_quota("trial") is False

    def test_enterprise_higher_limit(self):
        quota = get_tenant_quota("firm-004")
        quota.current_rpm = 150
        assert quota.is_within_quota("enterprise") is True  # enterprise limit = 200

    def test_daily_exceeded(self):
        quota = get_tenant_quota("firm-005")
        quota.current_daily = 5001
        assert quota.is_within_quota("trial") is False

    def test_tier_overrides(self):
        quota = TenantQuota(
            firm_id="custom",
            tier_overrides={"trial": 10, "professional": 100},
        )
        assert quota.tier_overrides["trial"] == 10


# ── BYOK Config Tests ────────────────────────────────────────────────────


class TestBYOKConfig:
    """Tests for Phase 4 BYOK encryption config stub."""

    def test_default_disabled(self):
        config = BYOKConfig()
        assert config.enabled is False
        assert config.kms_key_uri is None
        assert config.rotation_period_days == 90


# ── Dispatch Metrics Tests ────────────────────────────────────────────────


class TestDispatchMetrics:
    """Tests for Cloud Monitoring metric recording."""

    def test_record_dispatch(self):
        record_dispatch("simple", "gemini-flash")
        record_dispatch("simple", "gemini-flash")
        metrics = get_dispatch_metrics()
        assert metrics["dispatch.simple.gemini-flash"] == 2

    def test_record_fallback(self):
        record_fallback("gemini-pro", "claude-sonnet")
        metrics = get_dispatch_metrics()
        assert metrics["fallback.gemini-pro->claude-sonnet"] == 1

    def test_mixed_metrics(self):
        record_dispatch("agentic", "gemini-pro")
        record_fallback("claude-sonnet", "gpt-4-1")
        metrics = get_dispatch_metrics()
        assert "dispatch.agentic.gemini-pro" in metrics
        assert "fallback.claude-sonnet->gpt-4-1" in metrics


# ── Model Selection Tests ─────────────────────────────────────────────────


class TestSelectModel:
    """Tests for the full NadirClaw model selection pipeline."""

    def test_simple_query_routes_to_flash(self):
        req = ModelRequest(
            query_text="hello",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )
        model = select_model(req)
        assert model.model_id == "gemini-3.1-flash-lite-preview"

    def test_agentic_query_routes_to_pro(self):
        req = ModelRequest(
            query_text="analyze this contract and draft a response",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )
        model = select_model(req)
        assert model.model_id == "gemini-3.1-pro"

    def test_preferred_model_respected(self):
        req = ModelRequest(
            preferred_model="claude-sonnet",
            firm_allowed_models=["gemini-flash", "claude-sonnet"],
        )
        model = select_model(req)
        assert model.model_id == "claude-sonnet-4-5-20250514"

    def test_preferred_model_not_in_policy(self):
        req = ModelRequest(
            preferred_model="claude-opus",
            query_text="hello",
            firm_allowed_models=["gemini-flash"],
        )
        model = select_model(req)
        assert model.model_id == "gemini-3.1-flash-lite-preview"

    def test_session_pin_overrides(self):
        pin_session_model("s1", "claude-sonnet")
        req = ModelRequest(
            query_text="hello",
            session_id="s1",
            firm_allowed_models=["gemini-flash", "claude-sonnet"],
        )
        model = select_model(req)
        assert model.model_id == "claude-sonnet-4-5-20250514"

    def test_quota_exceeded_degrades_to_flash(self):
        quota = get_tenant_quota("firm-blocked", "trial")
        quota.current_rpm = 999
        req = ModelRequest(
            query_text="analyze everything",
            firm_id="firm-blocked",
            user_tier="trial",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )
        model = select_model(req)
        assert model.model_id == "gemini-3.1-flash-lite-preview"


# ── Async Dispatch Integration Tests ─────────────────────────────────────


class TestDispatchRequest:
    """Tests for the FastAPI integration function."""

    @pytest.mark.asyncio
    async def test_basic_dispatch(self):
        result = await dispatch_request(
            query="hello",
            firm_id="firm-test",
            firm_allowed_models=["gemini-flash"],
        )
        assert result["model"] == "gemini-3.1-flash-lite-preview"
        assert result["tier"] == "simple"
        assert isinstance(result["cost_per_1k_input"], float)

    @pytest.mark.asyncio
    async def test_dispatch_increments_quota(self):
        await dispatch_request(
            query="hello",
            firm_id="firm-quota",
            firm_allowed_models=["gemini-flash"],
        )
        quota = _tenant_quotas.get("firm-quota")
        assert quota is not None
        assert quota.current_rpm >= 1
        assert quota.current_daily >= 1

    @pytest.mark.asyncio
    async def test_dispatch_records_metrics(self):
        await dispatch_request(
            query="analyze this contract",
            firm_id="firm-metrics",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )
        metrics = get_dispatch_metrics()
        assert any("dispatch." in k for k in metrics)
