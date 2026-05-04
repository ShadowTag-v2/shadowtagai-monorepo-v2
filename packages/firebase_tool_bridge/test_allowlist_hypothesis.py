# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Hypothesis property tests for AllowlistConfirmationProvider.

These tests verify structural invariants of the allowlist-based
confirmation gate using property-based testing:

1. Membership invariant: If name ∈ allowlist → approved. If name ∉ → denied.
2. Immutability: Provider state never changes after construction.
3. Frozenset coercion: Mutable set inputs are frozen on construction.
4. Empty-set denial: An empty allowlist denies everything.
5. Risk/tag independence: Approval depends only on function name.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from firebase_tool_bridge.confirmation_providers import AllowlistConfirmationProvider
from firebase_tool_bridge.registry import RiskTier

# ── Strategies ──────────────────────────────────────────────────

# Function names: non-empty ASCII identifiers (Python-legal names)
_fn_name = st.from_regex(r"[a-z][a-z0-9_]{0,63}", fullmatch=True)

# Risk tiers
_risk_tier = st.sampled_from(list(RiskTier))

# Action tag sets
_action_tags = st.frozensets(
    st.from_regex(r"[a-z_]{1,20}", fullmatch=True),
    min_size=0,
    max_size=5,
)

# Argument dicts (always ignored by allowlist, but must be valid)
_args = st.fixed_dictionaries(
    {},
    optional={
        "key": st.text(min_size=0, max_size=10),
        "val": st.integers(),
    },
)


# ── Property: Membership Invariant ──────────────────────────────


@given(
    allowed_set=st.frozensets(_fn_name, min_size=1, max_size=20),
    query_name=_fn_name,
    risk=_risk_tier,
    tags=_action_tags,
    args=_args,
)
@settings(max_examples=200, deadline=500)
def test_membership_invariant(
    allowed_set: frozenset[str],
    query_name: str,
    risk: RiskTier,
    tags: frozenset[str],
    args: dict,
) -> None:
    """If function_name ∈ allowlist → True, else → False."""
    provider = AllowlistConfirmationProvider(allowed=allowed_set)
    result = provider.request_confirmation(query_name, args, risk, tags)

    if query_name in allowed_set:
        assert result is True, f"{query_name!r} should be approved (in allowlist)"
    else:
        assert result is False, f"{query_name!r} should be denied (not in allowlist)"


# ── Property: Risk Tier Independence ────────────────────────────


@given(
    fn_name=_fn_name,
    risk_a=_risk_tier,
    risk_b=_risk_tier,
    tags=_action_tags,
    args=_args,
)
@settings(max_examples=100, deadline=500)
def test_risk_tier_independence(
    fn_name: str,
    risk_a: RiskTier,
    risk_b: RiskTier,
    tags: frozenset[str],
    args: dict,
) -> None:
    """Approval decision is independent of risk tier."""
    allowed = frozenset({fn_name})
    provider = AllowlistConfirmationProvider(allowed=allowed)

    result_a = provider.request_confirmation(fn_name, args, risk_a, tags)
    result_b = provider.request_confirmation(fn_name, args, risk_b, tags)

    assert result_a == result_b, "Risk tier should not affect allowlist decision"


# ── Property: Action Tags Independence ──────────────────────────


@given(
    fn_name=_fn_name,
    risk=_risk_tier,
    tags_a=_action_tags,
    tags_b=_action_tags,
    args=_args,
)
@settings(max_examples=100, deadline=500)
def test_action_tags_independence(
    fn_name: str,
    risk: RiskTier,
    tags_a: frozenset[str],
    tags_b: frozenset[str],
    args: dict,
) -> None:
    """Approval decision is independent of action tags."""
    allowed = frozenset({fn_name})
    provider = AllowlistConfirmationProvider(allowed=allowed)

    result_a = provider.request_confirmation(fn_name, args, risk, tags_a)
    result_b = provider.request_confirmation(fn_name, args, risk, tags_b)

    assert result_a == result_b, "Action tags should not affect allowlist decision"


# ── Property: Empty Allowlist Denies Everything ─────────────────


@given(
    fn_name=_fn_name,
    risk=_risk_tier,
    tags=_action_tags,
    args=_args,
)
@settings(max_examples=100, deadline=500)
def test_empty_allowlist_denies_all(
    fn_name: str,
    risk: RiskTier,
    tags: frozenset[str],
    args: dict,
) -> None:
    """An empty allowlist always denies."""
    provider = AllowlistConfirmationProvider(allowed=frozenset())
    result = provider.request_confirmation(fn_name, args, risk, tags)
    assert result is False, "Empty allowlist should deny all functions"


# ── Property: Frozenset Coercion ────────────────────────────────


@given(
    allowed_list=st.lists(_fn_name, min_size=1, max_size=10),
)
@settings(max_examples=50, deadline=500)
def test_mutable_set_coercion(
    allowed_list: list[str],
) -> None:
    """Mutable set input is safely frozen on construction."""
    mutable = set(allowed_list)
    provider = AllowlistConfirmationProvider(allowed=mutable)

    # Mutate the original — should NOT affect provider
    original_copy = frozenset(mutable)
    mutable.add("__injected_mutation__")

    for fn in original_copy:
        result = provider.request_confirmation(fn, {}, RiskTier.LOW, frozenset())
        assert result is True

    # The injected name should NOT be approved
    result = provider.request_confirmation("__injected_mutation__", {}, RiskTier.LOW, frozenset())
    assert result is False, "Provider should be immune to post-construction mutation"


# ── Property: Idempotency ───────────────────────────────────────


@given(
    allowed_set=st.frozensets(_fn_name, min_size=1, max_size=10),
    fn_name=_fn_name,
    risk=_risk_tier,
    tags=_action_tags,
    args=_args,
)
@settings(max_examples=100, deadline=500)
def test_idempotent_repeated_calls(
    allowed_set: frozenset[str],
    fn_name: str,
    risk: RiskTier,
    tags: frozenset[str],
    args: dict,
) -> None:
    """Multiple calls with same inputs produce same result."""
    provider = AllowlistConfirmationProvider(allowed=allowed_set)

    result_1 = provider.request_confirmation(fn_name, args, risk, tags)
    result_2 = provider.request_confirmation(fn_name, args, risk, tags)
    result_3 = provider.request_confirmation(fn_name, args, risk, tags)

    assert result_1 == result_2 == result_3, "Repeated calls must be idempotent"
