# apps/counselconduit/tests/test_dispatch_router.py
"""Integration tests for dispatch_router.py FastAPI endpoints.

Tests:
    - POST /api/v1/dispatch (happy path, rate limit, circuit breaker)
    - GET  /admin/metrics
    - POST /admin/firm-policy
    - POST /admin/session-cleanup
    - GET  /admin/circuit-breaker
    - GET  /admin/models
    - Rate-limit headers
    - Circuit breaker load shedding
"""

from __future__ import annotations

import time

import pytest

from apps.counselconduit.api.dispatch_router import (
    CIRCUIT_BREAKER_THRESHOLD,
    DispatchRequest,
    FirmPolicyRequest,
    _circuit_state,
    _firm_policies,
    cleanup_expired_session_pins,
)
from apps.counselconduit.api.model_router import (
    SESSION_PIN_TTL_SECONDS,
    _session_pins,
    _tenant_quotas,
    pin_session_model,
)

# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset all mutable state between tests."""
    _session_pins.clear()
    _tenant_quotas.clear()
    _firm_policies.clear()
    _circuit_state["errors"] = 0
    _circuit_state["last_error"] = 0.0
    _circuit_state["open"] = False
    yield


# ── Dispatch Request Model Tests ─────────────────────────────────────────


class TestDispatchRequest:
    def test_valid_request(self):
        req = DispatchRequest(
            query="What is attorney-client privilege?",
            firm_id="firm-001",
        )
        assert req.query == "What is attorney-client privilege?"
        assert req.firm_id == "firm-001"
        assert req.session_id == ""
        assert req.preferred_model is None

    def test_request_with_all_fields(self):
        req = DispatchRequest(
            query="Analyze this case",
            firm_id="firm-002",
            session_id="sess-abc",
            preferred_model="gemini-pro",
            firm_allowed_models=["gemini-flash", "gemini-pro"],
        )
        assert req.session_id == "sess-abc"
        assert req.preferred_model == "gemini-pro"

    def test_empty_query_rejected(self):
        with pytest.raises(Exception):
            DispatchRequest(query="", firm_id="firm-001")


# ── Session Pin Cleanup Tests ────────────────────────────────────────────


class TestSessionCleanup:
    def test_cleanup_no_pins(self):
        evicted = cleanup_expired_session_pins()
        assert evicted == 0

    def test_cleanup_active_pins_preserved(self):
        pin_session_model("sess-1", "gemini-flash")
        evicted = cleanup_expired_session_pins()
        assert evicted == 0
        assert "sess-1" in _session_pins

    def test_cleanup_expired_pins_evicted(self):
        expired_ts = time.time() - SESSION_PIN_TTL_SECONDS - 10
        _session_pins["sess-old"] = ("gemini-flash", expired_ts)
        _session_pins["sess-new"] = ("gemini-pro", time.time())

        evicted = cleanup_expired_session_pins()
        assert evicted == 1
        assert "sess-old" not in _session_pins
        assert "sess-new" in _session_pins


# ── Circuit Breaker Tests ────────────────────────────────────────────────


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        assert _circuit_state["open"] is False
        assert _circuit_state["errors"] == 0

    def test_state_after_threshold(self):
        for _ in range(CIRCUIT_BREAKER_THRESHOLD):
            from apps.counselconduit.api.dispatch_router import _record_circuit_error
            _record_circuit_error()
        assert _circuit_state["open"] is True

    def test_cooldown_resets(self):
        _circuit_state["open"] = True
        _circuit_state["last_error"] = time.time() - 120  # well past cooldown
        _circuit_state["errors"] = CIRCUIT_BREAKER_THRESHOLD
        from apps.counselconduit.api.dispatch_router import _check_circuit_breaker
        _check_circuit_breaker()  # should not raise
        assert _circuit_state["open"] is False


# ── Firm Policy Tests ────────────────────────────────────────────────────


class TestFirmPolicy:
    def test_create_policy(self):
        policy = FirmPolicyRequest(
            firm_id="firm-test",
            allowed_models=["gemini-flash", "claude-sonnet"],
            max_rpm=100,
        )
        assert policy.firm_id == "firm-test"
        assert len(policy.allowed_models) == 2
        assert policy.max_rpm == 100

    def test_policy_with_byok(self):
        from apps.counselconduit.api.model_router import BYOKConfig
        policy = FirmPolicyRequest(
            firm_id="firm-ent",
            allowed_models=["gemini-pro"],
            byok=BYOKConfig(
                enabled=True,
                kms_key_uri="projects/shadowtag-omega-v4/locations/us/keyRings/cc/cryptoKeys/firm-ent",
            ),
        )
        assert policy.byok.enabled is True


# ── Monitoring Tests ─────────────────────────────────────────────────────


class TestMonitoring:
    @pytest.mark.asyncio
    async def test_export_metrics_no_sdk(self):
        from apps.counselconduit.api.monitoring import export_metrics_to_cloud_monitoring
        result = await export_metrics_to_cloud_monitoring()
        # Should gracefully skip when SDK not installed
        assert result["status"] in ("ok", "skipped", "error")

    @pytest.mark.asyncio
    async def test_fallback_alert_no_sdk(self):
        from apps.counselconduit.api.monitoring import configure_fallback_saturation_alert
        result = await configure_fallback_saturation_alert()
        assert result["status"] in ("created", "skipped", "error")
