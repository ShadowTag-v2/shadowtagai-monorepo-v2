# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Hypothesis property-based tests for AllowlistConfirmationProvider.

Validates structural invariants of the allowlist-based confirmation gating
strategy using fuzzing and property-based techniques. Designed for CI
with bounded execution (max 50 examples per test, 1s deadline).

Key properties tested:
    1. Allowlisted functions always approve (idempotent membership).
    2. Non-allowlisted functions always deny (fail-closed invariant).
    3. Empty allowlist denies everything.
    4. Allowlist is immutable (frozen after construction).
    5. Risk tier and action tags never influence allowlist decisions.
    6. Superset inclusion: larger allowlist approves everything smaller does.
"""

from __future__ import annotations

import string
from typing import Any

from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from firebase_tool_bridge.confirmation_providers import AllowlistConfirmationProvider
from firebase_tool_bridge.registry import RiskTier


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid function names: 1–80 chars, alphanumeric + underscores (no empties)
_fn_name_st = st.text(
    alphabet=string.ascii_lowercase + string.digits + "_",
    min_size=1,
    max_size=80,
)

# Sets of function names (1–20 members)
_fn_set_st = st.frozensets(_fn_name_st, min_size=1, max_size=20)

# Risk tiers — all four enum members
_risk_tier_st = st.sampled_from(list(RiskTier))

# Action tags — 0–5 tags from a fixed vocabulary
_action_tag_vocab = [
    "deploy",
    "data_delete",
    "billing",
    "config_write",
    "admin_access",
    "pii_read",
    "escalation",
]
_action_tags_st = st.frozensets(
    st.sampled_from(_action_tag_vocab),
    min_size=0,
    max_size=5,
)

# Arbitrary args dicts (string keys, string values for safety)
_args_st = st.dictionaries(
    keys=st.text(min_size=1, max_size=30),
    values=st.text(max_size=100),
    max_size=10,
)


def _make_provider(allowed: frozenset[str]) -> AllowlistConfirmationProvider:
    """Factory helper — constructs provider from a frozenset."""
    return AllowlistConfirmationProvider(allowed=allowed)


# ---------------------------------------------------------------------------
# Property 1: Membership → Approval (∀ f ∈ allowed, approve(f) == True)
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    risk_tier=_risk_tier_st,
    action_tags=_action_tags_st,
    args=_args_st,
)
def test_allowlisted_functions_always_approve(
    allowed: frozenset[str],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
    args: dict[str, Any],
) -> None:
    """An allowlisted function MUST be approved regardless of context."""
    provider = _make_provider(allowed)
    for fn_name in allowed:
        result = provider.request_confirmation(fn_name, args, risk_tier, action_tags)
        assert result is True, f"Allowlisted '{fn_name}' was denied with risk={risk_tier}, tags={action_tags}"


# ---------------------------------------------------------------------------
# Property 2: Non-membership → Denial (∀ f ∉ allowed, approve(f) == False)
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    intruder=_fn_name_st,
    risk_tier=_risk_tier_st,
    action_tags=_action_tags_st,
    args=_args_st,
)
def test_non_allowlisted_functions_always_deny(
    allowed: frozenset[str],
    intruder: str,
    risk_tier: RiskTier,
    action_tags: frozenset[str],
    args: dict[str, Any],
) -> None:
    """A function NOT in the allowlist MUST be denied."""
    assume(intruder not in allowed)
    provider = _make_provider(allowed)
    result = provider.request_confirmation(intruder, args, risk_tier, action_tags)
    assert result is False, f"Non-allowlisted '{intruder}' was approved when allowed={allowed}"


# ---------------------------------------------------------------------------
# Property 3: Empty allowlist → universal denial
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    fn_name=_fn_name_st,
    risk_tier=_risk_tier_st,
    action_tags=_action_tags_st,
    args=_args_st,
)
def test_empty_allowlist_denies_everything(
    fn_name: str,
    risk_tier: RiskTier,
    action_tags: frozenset[str],
    args: dict[str, Any],
) -> None:
    """An empty allowlist MUST deny every function."""
    provider = _make_provider(frozenset())
    result = provider.request_confirmation(fn_name, args, risk_tier, action_tags)
    assert result is False, f"Empty allowlist approved '{fn_name}'"


# ---------------------------------------------------------------------------
# Property 4: Immutability — the internal set cannot be mutated
# ---------------------------------------------------------------------------


@settings(
    max_examples=20,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(allowed=_fn_set_st)
def test_allowlist_is_immutable(allowed: frozenset[str]) -> None:
    """The internal allowlist MUST be frozen (immutable)."""
    provider = _make_provider(allowed)
    internal = provider._allowed  # noqa: SLF001 — test-only access
    assert isinstance(internal, frozenset), f"Expected frozenset, got {type(internal).__name__}"
    assert internal == allowed


# ---------------------------------------------------------------------------
# Property 5: Risk tier independence — approval depends ONLY on membership
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    risk_tier_a=_risk_tier_st,
    risk_tier_b=_risk_tier_st,
    tags_a=_action_tags_st,
    tags_b=_action_tags_st,
    args=_args_st,
)
def test_risk_tier_and_tags_do_not_affect_decision(
    allowed: frozenset[str],
    risk_tier_a: RiskTier,
    risk_tier_b: RiskTier,
    tags_a: frozenset[str],
    tags_b: frozenset[str],
    args: dict[str, Any],
) -> None:
    """Changing risk tier or action tags MUST NOT change the decision."""
    provider = _make_provider(allowed)
    fn_name = next(iter(allowed))  # Pick any allowed function
    result_a = provider.request_confirmation(fn_name, args, risk_tier_a, tags_a)
    result_b = provider.request_confirmation(fn_name, args, risk_tier_b, tags_b)
    assert result_a == result_b, f"Decision changed for '{fn_name}': {risk_tier_a}/{tags_a} → {result_a}, {risk_tier_b}/{tags_b} → {result_b}"


# ---------------------------------------------------------------------------
# Property 6: Superset monotonicity — expanding allowlist never revokes
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    extra=_fn_set_st,
    risk_tier=_risk_tier_st,
    action_tags=_action_tags_st,
    args=_args_st,
)
def test_superset_monotonicity(
    allowed: frozenset[str],
    extra: frozenset[str],
    risk_tier: RiskTier,
    action_tags: frozenset[str],
    args: dict[str, Any],
) -> None:
    """If A ⊆ B, then B.approve(f) ≥ A.approve(f) for all f ∈ A."""
    superset = allowed | extra
    provider_small = _make_provider(allowed)
    provider_large = _make_provider(superset)

    for fn_name in allowed:
        small_result = provider_small.request_confirmation(fn_name, args, risk_tier, action_tags)
        large_result = provider_large.request_confirmation(fn_name, args, risk_tier, action_tags)
        # If small approves, large MUST also approve (monotonicity)
        if small_result:
            assert large_result, f"Monotonicity violated: '{fn_name}' approved by subset but denied by superset"


# ---------------------------------------------------------------------------
# Property 7: Determinism — same inputs always produce same output
# ---------------------------------------------------------------------------


@settings(
    max_examples=50,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    fn_name=_fn_name_st,
    risk_tier=_risk_tier_st,
    action_tags=_action_tags_st,
    args=_args_st,
)
def test_deterministic_decisions(
    allowed: frozenset[str],
    fn_name: str,
    risk_tier: RiskTier,
    action_tags: frozenset[str],
    args: dict[str, Any],
) -> None:
    """Calling request_confirmation twice with identical inputs MUST yield identical results."""
    provider = _make_provider(allowed)
    r1 = provider.request_confirmation(fn_name, args, risk_tier, action_tags)
    r2 = provider.request_confirmation(fn_name, args, risk_tier, action_tags)
    assert r1 == r2, f"Non-deterministic decision for '{fn_name}': {r1} != {r2}"


# ---------------------------------------------------------------------------
# Property 8: Construction from set vs frozenset equivalence
# ---------------------------------------------------------------------------


@settings(
    max_examples=20,
    deadline=1000,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    allowed=_fn_set_st,
    fn_name=_fn_name_st,
    risk_tier=_risk_tier_st,
    args=_args_st,
)
def test_set_and_frozenset_construction_equivalent(
    allowed: frozenset[str],
    fn_name: str,
    risk_tier: RiskTier,
    args: dict[str, Any],
) -> None:
    """Provider constructed from set vs frozenset MUST behave identically."""
    from_set = AllowlistConfirmationProvider(allowed=set(allowed))
    from_frozen = AllowlistConfirmationProvider(allowed=allowed)

    tags = frozenset[str]()
    assert from_set.request_confirmation(fn_name, args, risk_tier, tags) == from_frozen.request_confirmation(fn_name, args, risk_tier, tags)
