# labs/uphillsnowball/tests/test_epistemology_hypothesis.py
"""Property-based tests for EpistemologicalForensics using Hypothesis.

Validates mathematical invariants of the permutation-based statistical
claim validation engine. These tests complement the example-based tests
in test_epistemology.py by exhaustively searching the input space.

Properties tested:
  1. _compute_effect_size is always non-negative (MAD ≥ 0)
  2. Constant data ⇒ effect size = 0
  3. Effect size is permutation-invariant (shuffle-stable)
  4. p-value is always in [0, 1]
  5. Empty data ⇒ deterministic rejection
  6. validate_statistical_claim returns well-typed results
  7. Single-element data ⇒ MAD = 0
"""

from __future__ import annotations

import random

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.intelligence.epistemology_engine import EpistemologicalForensics


# Shared strategy: lists of finite floats (no NaN/inf)
finite_floats = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
data_lists = st.lists(finite_floats, min_size=1, max_size=200)
nonempty_data = st.lists(finite_floats, min_size=2, max_size=200)

forensics = EpistemologicalForensics()


# ─── Property 1: MAD is always non-negative ──────────────────────────
class TestEffectSizeProperties:
    """Property-based tests for _compute_effect_size (MAD)."""

    @given(data=data_lists)
    def test_mad_is_nonnegative(self, data: list[float]):
        """Mean absolute deviation can never be negative."""
        result = forensics._compute_effect_size(data)
        assert result >= 0.0, f"MAD was negative: {result}"

    @given(value=finite_floats, n=st.integers(min_value=1, max_value=100))
    def test_constant_data_yields_zero(self, value: float, n: int):
        """If all data points are identical, MAD must be ~0 (within FP tolerance)."""
        import math

        data = [value] * n
        result = forensics._compute_effect_size(data)
        assert math.isclose(result, 0.0, abs_tol=1e-9), f"Constant data gave non-zero MAD: {result}"

    @given(data=nonempty_data)
    @settings(max_examples=50)
    def test_shuffle_invariance(self, data: list[float]):
        """MAD is invariant under permutation of inputs."""
        original = forensics._compute_effect_size(data)
        shuffled = data.copy()
        random.shuffle(shuffled)
        permuted = forensics._compute_effect_size(shuffled)
        assert abs(original - permuted) < 1e-9, f"Shuffle changed MAD: {original} → {permuted}"

    @given(data=data_lists, scale=st.floats(min_value=0.1, max_value=100.0))
    @settings(max_examples=50)
    def test_scaling_property(self, data: list[float], scale: float):
        """MAD(k*data) = |k| * MAD(data) — positive homogeneity."""
        assume(all(abs(x * scale) < 1e10 for x in data))
        original = forensics._compute_effect_size(data)
        scaled_data = [x * scale for x in data]
        scaled_mad = forensics._compute_effect_size(scaled_data)
        assert abs(scaled_mad - scale * original) < 1e-4 * max(1, abs(scaled_mad)), f"Scaling violated: {scaled_mad} ≠ {scale} * {original}"

    def test_empty_data_returns_zero(self):
        """Empty list ⇒ MAD = 0.0 (guard clause)."""
        assert forensics._compute_effect_size([]) == 0.0

    @given(value=finite_floats)
    def test_single_element_is_zero(self, value: float):
        """A single data point has zero deviation from itself."""
        assert forensics._compute_effect_size([value]) == 0.0


# ─── Property 2: validate_statistical_claim output contract ──────────
class TestClaimValidationProperties:
    """Property-based tests for validate_statistical_claim."""

    @given(
        data=nonempty_data,
        claimed_effect=st.floats(min_value=0.0, max_value=1e4),
        alpha=st.floats(min_value=0.01, max_value=0.99),
    )
    @settings(max_examples=30)
    def test_p_value_bounded(self, data: list[float], claimed_effect: float, alpha: float):
        """p-value must always be in [0, 1]."""
        result = forensics.validate_statistical_claim(data, claimed_effect, n_permutations=50, alpha=alpha)
        assert 0.0 <= result["p_value"] <= 1.0, f"p_value out of range: {result['p_value']}"

    @given(
        data=nonempty_data,
        claimed_effect=st.floats(min_value=0.0, max_value=1e4),
        alpha=st.floats(min_value=0.01, max_value=0.99),
    )
    @settings(max_examples=30)
    def test_result_has_required_keys(self, data: list[float], claimed_effect: float, alpha: float):
        """Result dict must always contain 'valid', 'p_value', 'directive'."""
        result = forensics.validate_statistical_claim(data, claimed_effect, n_permutations=50, alpha=alpha)
        assert "valid" in result
        assert "p_value" in result
        assert "directive" in result
        assert isinstance(result["valid"], bool)

    @given(
        data=nonempty_data,
        claimed_effect=st.floats(min_value=0.0, max_value=1e4),
        alpha=st.floats(min_value=0.01, max_value=0.99),
    )
    @settings(max_examples=30)
    def test_directive_is_valid_enum(self, data: list[float], claimed_effect: float, alpha: float):
        """Directive must be one of the defined enum values."""
        result = forensics.validate_statistical_claim(data, claimed_effect, n_permutations=50, alpha=alpha)
        valid_directives = {"VERIFIED", "REJECT_HALLUCINATED_ALPHA", "REJECT_EMPTY_DATA"}
        assert result["directive"] in valid_directives, f"Unknown directive: {result['directive']}"

    def test_empty_data_always_rejects(self):
        """Empty data must always produce REJECT_EMPTY_DATA."""
        result = forensics.validate_statistical_claim([], 0.5)
        assert result["valid"] is False
        assert result["directive"] == "REJECT_EMPTY_DATA"
        assert result["p_value"] == 1.0

    @given(
        data=nonempty_data,
        alpha=st.floats(min_value=0.01, max_value=0.99),
    )
    @settings(max_examples=30)
    def test_validity_matches_directive(self, data: list[float], alpha: float):
        """valid=True ⟺ directive='VERIFIED'."""
        result = forensics.validate_statistical_claim(data, 0.0, n_permutations=50, alpha=alpha)
        if result["valid"]:
            assert result["directive"] == "VERIFIED"
        else:
            assert result["directive"] != "VERIFIED"
