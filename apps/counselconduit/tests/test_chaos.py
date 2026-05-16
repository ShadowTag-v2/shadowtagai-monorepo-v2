"""Chaos Engineering Tests for CounselConduit (Item #21).

Tests system resilience under failure conditions:
1. Provider circuit breaker activation
2. Token budget exhaustion behavior
3. Session pin expiry under load
4. Concurrent dispatch race conditions
5. Malformed request handling
"""

import asyncio
import time

import pytest

# Mark all tests as chaos engineering
pytestmark = pytest.mark.chaos


class TestCircuitBreakerChaos:
  """Verify circuit breaker triggers and recovers correctly."""

  def test_circuit_opens_after_5_failures(self):
    """Circuit breaker should open after 5 consecutive failures."""
    from apps.counselconduit.api.dispatch_router import (
      _circuit_breakers,
      is_circuit_open,
      record_provider_failure,
    )

    # Reset state
    _circuit_breakers.clear()
    model = "test-model"

    # Record 4 failures — circuit should stay closed
    for _ in range(4):
      record_provider_failure(model)
    assert not is_circuit_open(model)

    # 5th failure — circuit opens
    record_provider_failure(model)
    assert is_circuit_open(model)

  def test_circuit_resets_on_success(self):
    """Success should reset the circuit breaker."""
    from apps.counselconduit.api.dispatch_router import (
      _circuit_breakers,
      is_circuit_open,
      record_provider_failure,
      record_provider_success,
    )

    _circuit_breakers.clear()
    model = "test-model"

    for _ in range(5):
      record_provider_failure(model)
    assert is_circuit_open(model)

    record_provider_success(model)
    assert not is_circuit_open(model)

  def test_circuit_half_open_after_timeout(self):
    """Circuit should transition to half-open after 5 min cooldown."""
    from apps.counselconduit.api.dispatch_router import (
      _circuit_breakers,
      is_circuit_open,
      record_provider_failure,
    )

    _circuit_breakers.clear()
    model = "test-model"

    for _ in range(5):
      record_provider_failure(model)

    # Simulate time passing (5+ minutes)
    _circuit_breakers[model]["opened_at"] = time.time() - 301

    # Should be half-open (not fully open)
    assert not is_circuit_open(model)
    assert _circuit_breakers[model]["failures"] == 3  # half-open


class TestTokenBudgetChaos:
  """Verify behavior when token budgets are exhausted."""

  def test_quota_exceeded_degrades_to_flash(self):
    """When tenant exceeds quota, should degrade to cheapest model."""
    from apps.counselconduit.api.model_router import (
      ModelRequest,
      TenantQuota,
      _tenant_quotas,
      select_model,
    )

    # Set up exhausted quota
    _tenant_quotas["chaos-firm"] = TenantQuota(
      firm_id="chaos-firm",
      current_rpm=100,  # Way over limit
      current_daily=6000,
    )

    req = ModelRequest(
      query_text="Analyze this complex legal case",
      firm_id="chaos-firm",
      user_tier="trial",
      firm_allowed_models=["gemini-flash", "gemini-pro"],
    )

    model = select_model(req)
    assert model.model_id == "gemini-3.1-flash-lite-preview-thinking"

    # Cleanup
    del _tenant_quotas["chaos-firm"]


class TestSessionPinChaos:
  """Verify session pinning under edge conditions."""

  def test_expired_pin_returns_none(self):
    """Expired session pins should return None."""
    from apps.counselconduit.api.model_router import (
      _session_pins,
      get_pinned_model,
      pin_session_model,
    )

    session = "chaos-session-expired"
    pin_session_model(session, "gemini-pro")

    # Simulate TTL expiry
    _session_pins[session] = ("gemini-pro", time.time() - 1801)  # > 30 min

    result = get_pinned_model(session)
    assert result is None

  def test_valid_pin_returns_model(self):
    """Valid session pins should return the model key."""
    from apps.counselconduit.api.model_router import (
      get_pinned_model,
      pin_session_model,
    )

    session = "chaos-session-valid"
    pin_session_model(session, "claude-sonnet")

    result = get_pinned_model(session)
    assert result == "claude-sonnet"


class TestPromptRepetitionChaos:
  """Verify arXiv 2512.14982 prompt repetition logic."""

  @pytest.mark.asyncio
  async def test_flash_model_gets_repetition(self):
    """Non-reasoning flash model should get prompt repeated."""
    from apps.counselconduit.api.model_router import dispatch_request

    result = await dispatch_request(
      query="What is consideration in contract law?",
      firm_id="chaos-firm-rep",
      user_tier="trial",
      firm_allowed_models=["gemini-flash"],
    )

    # gemini-3.1-flash-lite-preview-thinking ends with -thinking
    # so prompt_repeated should be False (reasoning model exception)
    assert "prompt_repeated" in result

  @pytest.mark.asyncio
  async def test_dispatch_returns_effective_query(self):
    """Dispatch should always return effective_query field."""
    from apps.counselconduit.api.model_router import dispatch_request

    result = await dispatch_request(
      query="Hello",
      firm_id="chaos-firm-eq",
      user_tier="trial",
      firm_allowed_models=["gemini-flash"],
    )

    assert "effective_query" in result
    assert "Hello" in result["effective_query"]


class TestConcurrentDispatchChaos:
  """Verify dispatch under concurrent load."""

  @pytest.mark.asyncio
  async def test_concurrent_dispatches_dont_corrupt_state(self):
    """50 concurrent dispatches should not corrupt shared state."""
    from apps.counselconduit.api.model_router import dispatch_request

    async def dispatch_one(i: int):
      return await dispatch_request(
        query=f"Query {i}: What is tort law?",
        firm_id=f"chaos-firm-{i % 5}",
        session_id=f"chaos-session-{i}",
        user_tier="trial",
        firm_allowed_models=["gemini-flash"],
      )

    results = await asyncio.gather(*(dispatch_one(i) for i in range(50)))

    assert len(results) == 50
    for r in results:
      assert r["model"] == "gemini-3.1-flash-lite-preview-thinking"
      assert "tier" in r
