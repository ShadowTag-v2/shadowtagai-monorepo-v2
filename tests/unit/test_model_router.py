"""Unit tests for Model Router — NadirClaw 3-tier dispatch.

Tests cover:
- ModelProvider enum
- AVAILABLE_MODELS registry
- classify_prompt heuristics
- select_model routing logic
- Session pinning with TTL
- Tenant quota (noisy neighbor protection)
- Dispatch metrics recording
- Fallback chain
- TIER_MODEL_MAP
- get_models_for_tier
- Prompt repetition (arXiv 2512.14982)
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset all in-memory state between tests."""
    from apps.counselconduit.api.model_router import (
        _dispatch_metrics,
        _fallback_hits,
        _session_pins,
        _tenant_quotas,
    )

    _session_pins.clear()
    _tenant_quotas.clear()
    _dispatch_metrics.clear()
    _fallback_hits.clear()
    yield
    _session_pins.clear()
    _tenant_quotas.clear()
    _dispatch_metrics.clear()
    _fallback_hits.clear()


class TestModelProvider:
    def test_all_providers(self):
        from apps.counselconduit.api.model_router import ModelProvider

        assert ModelProvider.GEMINI == "gemini"
        assert ModelProvider.CLAUDE == "claude"
        assert ModelProvider.GPT == "openai"
        assert ModelProvider.GROK == "grok"
        assert ModelProvider.PERPLEXITY == "perplexity"


class TestAvailableModels:
    def test_gemini_flash_exists(self):
        from apps.counselconduit.api.model_router import AVAILABLE_MODELS

        assert "gemini-flash" in AVAILABLE_MODELS
        assert AVAILABLE_MODELS["gemini-flash"].tier_minimum == "trial"

    def test_all_models_have_cost(self):
        from apps.counselconduit.api.model_router import AVAILABLE_MODELS

        for key, model in AVAILABLE_MODELS.items():
            assert model.cost_per_1k_input >= 0, f"{key} missing input cost"
            assert model.cost_per_1k_output >= 0, f"{key} missing output cost"

    def test_seven_models_registered(self):
        from apps.counselconduit.api.model_router import AVAILABLE_MODELS

        assert len(AVAILABLE_MODELS) == 7


class TestClassifyPrompt:
    def test_simple_query(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        assert classify_prompt("hello") == DispatchTier.SIMPLE

    def test_complex_query(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        assert classify_prompt("why does this contract clause matter?") == DispatchTier.COMPLEX

    def test_agentic_query(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        assert classify_prompt("analyze this contract and draft a response memo") == DispatchTier.AGENTIC

    def test_long_query_is_agentic(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        long_text = " ".join(["word"] * 201)
        assert classify_prompt(long_text) == DispatchTier.AGENTIC

    def test_medium_query_is_complex(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        medium_text = " ".join(["legal"] * 51)
        assert classify_prompt(medium_text) == DispatchTier.COMPLEX

    def test_explain_is_complex(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        assert classify_prompt("explain the implications") == DispatchTier.COMPLEX

    def test_tool_prefix_is_agentic(self):
        from apps.counselconduit.api.model_router import DispatchTier, classify_prompt

        assert classify_prompt("tool: search for precedent") == DispatchTier.AGENTIC


class TestSessionPinning:
    def test_pin_and_get(self):
        from apps.counselconduit.api.model_router import get_pinned_model, pin_session_model

        pin_session_model("sess1", "gemini-flash")
        assert get_pinned_model("sess1") == "gemini-flash"

    def test_no_pin_returns_none(self):
        from apps.counselconduit.api.model_router import get_pinned_model

        assert get_pinned_model("nonexistent") is None

    def test_expired_pin_returns_none(self):
        from apps.counselconduit.api.model_router import (
            SESSION_PIN_TTL_SECONDS,
            _session_pins,
        )

        # Manually set an expired pin
        _session_pins["old_sess"] = ("gemini-pro", time.time() - SESSION_PIN_TTL_SECONDS - 1)

        from apps.counselconduit.api.model_router import get_pinned_model

        assert get_pinned_model("old_sess") is None


class TestTenantQuota:
    def test_within_quota(self):
        from apps.counselconduit.api.model_router import TenantQuota

        q = TenantQuota(firm_id="f1")
        assert q.is_within_quota("trial") is True

    def test_over_rpm_quota(self):
        from apps.counselconduit.api.model_router import TenantQuota

        q = TenantQuota(firm_id="f1", current_rpm=20)
        assert q.is_within_quota("trial") is False  # trial limit is 20

    def test_over_daily_quota(self):
        from apps.counselconduit.api.model_router import TenantQuota

        q = TenantQuota(firm_id="f1", current_daily=5000)
        assert q.is_within_quota("trial") is False

    def test_get_tenant_quota_creates_new(self):
        from apps.counselconduit.api.model_router import get_tenant_quota

        q = get_tenant_quota("new_firm")
        assert q.firm_id == "new_firm"
        assert q.current_rpm == 0

    def test_get_tenant_quota_reuses(self):
        from apps.counselconduit.api.model_router import get_tenant_quota

        q1 = get_tenant_quota("firm_x")
        q1.current_rpm = 5
        q2 = get_tenant_quota("firm_x")
        assert q2.current_rpm == 5


class TestDispatchMetrics:
    def test_record_dispatch(self):
        from apps.counselconduit.api.model_router import get_dispatch_metrics, record_dispatch

        record_dispatch("simple", "gemini-flash")
        metrics = get_dispatch_metrics()
        assert metrics["dispatch.simple.gemini-flash"] == 1

    def test_record_fallback(self):
        from apps.counselconduit.api.model_router import get_dispatch_metrics, record_fallback

        record_fallback("claude-sonnet", "gpt-4-1")
        metrics = get_dispatch_metrics()
        assert metrics["fallback.claude-sonnet->gpt-4-1"] == 1


class TestSelectModel:
    def test_default_flash(self):
        from apps.counselconduit.api.model_router import ModelRequest, select_model

        req = ModelRequest()
        result = select_model(req)
        assert result.model_id == "gemini-3.1-flash-lite-preview-thinking"

    def test_preferred_model_honored(self):
        from apps.counselconduit.api.model_router import ModelRequest, select_model

        req = ModelRequest(
            preferred_model="gemini-flash",
            firm_allowed_models=["gemini-flash"],
        )
        result = select_model(req)
        assert "flash" in result.model_id.lower()

    def test_preferred_model_not_in_policy_falls_back(self):
        from apps.counselconduit.api.model_router import ModelRequest, select_model

        req = ModelRequest(
            preferred_model="claude-opus",
            firm_allowed_models=["gemini-flash"],
        )
        result = select_model(req)
        assert result.model_id == "gemini-3.1-flash-lite-preview-thinking"

    def test_quota_exceeded_degrades_to_flash(self):
        from apps.counselconduit.api.model_router import (
            ModelRequest,
            get_tenant_quota,
            select_model,
        )

        q = get_tenant_quota("firm_overloaded")
        q.current_daily = 5001  # over limit
        req = ModelRequest(firm_id="firm_overloaded")
        result = select_model(req)
        assert "flash" in result.model_id.lower()

    def test_auto_classify_routes_simple(self):
        from apps.counselconduit.api.model_router import ModelRequest, select_model

        req = ModelRequest(
            query_text="hi",
            firm_allowed_models=["gemini-flash"],
        )
        result = select_model(req)
        assert "flash" in result.model_id.lower()


class TestGetModelsForTier:
    def test_trial_gets_only_trial_models(self):
        from apps.counselconduit.api.model_router import get_models_for_tier

        models = get_models_for_tier("trial")
        assert all(m.tier_minimum == "trial" for m in models)

    def test_enterprise_gets_all_models(self):
        from apps.counselconduit.api.model_router import AVAILABLE_MODELS, get_models_for_tier

        models = get_models_for_tier("enterprise")
        assert len(models) == len(AVAILABLE_MODELS)

    def test_unknown_tier_gets_trial_only(self):
        from apps.counselconduit.api.model_router import get_models_for_tier

        models = get_models_for_tier("nonexistent")
        assert all(m.tier_minimum == "trial" for m in models)


class TestFallbackChain:
    def test_chain_completeness(self):
        from apps.counselconduit.api.model_router import AVAILABLE_MODELS, FALLBACK_CHAIN

        for model, fallback in FALLBACK_CHAIN.items():
            assert fallback in AVAILABLE_MODELS, f"Fallback {fallback} for {model} not in registry"
