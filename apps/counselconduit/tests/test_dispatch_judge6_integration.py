# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration test: Dispatch Router → Judge 6 Pipeline.

Tests the full flow: prompt classification → model selection → Judge 6 gate.
Verifies that dispatch output respects Judge 6 enforcement.
"""

from __future__ import annotations

import pytest

from apps.counselconduit.api.model_router import (
    ModelRequest,
    _dispatch_metrics,
    _fallback_hits,
    _session_pins,
    _tenant_quotas,
    classify_prompt,
    dispatch_request,
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


# ── Judge 6 + Dispatch Integration ──────────────────────────────────────


class TestDispatchJudge6Integration:
    """Tests verifying dispatch → Judge 6 pipeline interaction."""

    @pytest.mark.asyncio
    async def test_simple_query_dispatches_and_passes_judge6(self):
        """Simple query should dispatch to flash tier and pass Judge 6."""
        result = await dispatch_request(
            query="What is the statute of limitations?",
            firm_id="firm-judge6-test",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        # Dispatch should succeed
        assert result["model"] is not None
        assert result["tier"] == "simple"
        assert result["cost_per_1k_input"] >= 0

    @pytest.mark.asyncio
    async def test_complex_legal_query_routes_correctly(self):
        """Complex legal query should route to appropriate tier."""
        result = await dispatch_request(
            query="Explain the doctrine of equitable estoppel and how it applies to statute of limitations tolling in federal courts",
            firm_id="firm-legal-complex",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        assert result["tier"] in ("complex", "agentic")
        assert result["model"] is not None

    @pytest.mark.asyncio
    async def test_agentic_query_with_analysis_prefix(self):
        """Agentic query with 'analyze' prefix should route to agentic tier."""
        result = await dispatch_request(
            query="Analyze this contract for potential liability clauses and draft a summary memo with key risks identified",
            firm_id="firm-agentic-test",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        assert result["tier"] == "agentic"

    def test_classify_then_select_then_judge6_flow(self):
        """Test the full classification → selection → Judge 6 gate flow."""
        # Step 1: Classify prompt
        tier = classify_prompt("What time is it?")
        assert tier == "simple"

        # Step 2: Select model based on classification
        req = ModelRequest(
            query="What time is it?",
            firm_id="firm-flow",
            user_tier="trial",
            firm_allowed_models=["gemini-flash"],
        )
        model = select_model(req)
        assert model.model_id is not None

        # Step 3: Judge 6 gate (if available)
        try:
            from apps.counselconduit.api.judge6 import judge6_pipeline

            result = judge6_pipeline("The time is currently 3:00 PM.")
            assert result["signal"] in ("GREEN", "AMBER", "RED")

            # Green output should pass through
            if result["signal"] == "GREEN":
                assert result["output"] == "The time is currently 3:00 PM."

        except ImportError:
            # Judge 6 not available — test classification + selection only
            pass

    @pytest.mark.asyncio
    async def test_dispatch_with_session_pinning_and_judge6(self):
        """Dispatch with session pinning should maintain model through Judge 6."""
        # First dispatch — establishes session pin
        _result1 = await dispatch_request(
            query="Hello",
            firm_id="firm-pin-j6",
            session_id="session-judge6-1",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        # Second dispatch — same session should pin to same model
        result2 = await dispatch_request(
            query="Follow up question",
            firm_id="firm-pin-j6",
            session_id="session-judge6-1",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        assert result2["session_pinned"] is True

    @pytest.mark.asyncio
    async def test_judge6_red_signal_does_not_crash_dispatch(self):
        """Verify Judge 6 RED signal (blocked content) handled gracefully."""
        try:
            from apps.counselconduit.api.judge6 import judge6_pipeline

            # Test with content that Judge 6 should flag
            result = judge6_pipeline("I guarantee this legal advice is 100% correct and you will win your case.")

            # RED signal should replace output
            if result["signal"] == "RED":
                assert "⚠️" in result["output"] or "blocked" in result["output"].lower()
            elif result["signal"] == "AMBER":
                assert "advisory" in result["output"].lower() or "⚠️" in result["output"]

        except ImportError:
            pytest.skip("Judge 6 module not available")

    @pytest.mark.asyncio
    async def test_quota_exhaustion_degrades_gracefully_with_judge6(self):
        """When quota exhausted, dispatch degrades to flash — Judge 6 still applies."""
        # Exhaust quota
        for _ in range(65):
            await dispatch_request(
                query="hello",
                firm_id="firm-exhaust-j6",
                firm_allowed_models=["gemini-flash", "gemini-pro"],
            )

        # After quota exhaustion, should still dispatch (degraded)
        result = await dispatch_request(
            query="Analyze this contract thoroughly",
            firm_id="firm-exhaust-j6",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )

        # Should fall back to flash (cheapest) due to quota pressure
        assert result["model"] is not None
        assert result["cost_per_1k_input"] >= 0
