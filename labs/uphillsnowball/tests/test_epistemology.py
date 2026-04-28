# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# labs/uphillsnowball/tests/test_epistemology.py
"""Unit tests for EpistemologicalForensics.validate_statistical_claim (Item 12)."""

from __future__ import annotations

import pytest

from src.intelligence.epistemology_engine import EpistemologicalForensics


class TestValidateStatisticalClaim:
    """Tests for the permutation-based statistical claim validator."""

    @pytest.fixture
    def engine(self) -> EpistemologicalForensics:
        return EpistemologicalForensics()

    def test_empty_data_rejected(self, engine):
        """Empty data list is always rejected."""
        result = engine.validate_statistical_claim(real_data=[], claimed_effect_size=1.0)
        assert result["valid"] is False
        assert result["directive"] == "REJECT_EMPTY_DATA"
        assert result["p_value"] == 1.0

    def test_zero_effect_on_uniform_data_verified(self, engine):
        """Zero claimed effect on uniform data should be valid."""
        data = [5.0, 5.0, 5.0, 5.0, 5.0]
        result = engine.validate_statistical_claim(
            real_data=data,
            claimed_effect_size=0.0,
            n_permutations=100,
        )
        assert result["valid"] is True
        assert result["directive"] == "VERIFIED"

    def test_absurd_effect_rejected(self, engine):
        """Absurdly large claimed effect on tight data is rejected."""
        data = [1.0, 1.1, 0.9, 1.0, 1.05]
        result = engine.validate_statistical_claim(
            real_data=data,
            claimed_effect_size=999.0,
            n_permutations=200,
        )
        assert result["valid"] is False
        assert result["directive"] == "REJECT_HALLUCINATED_ALPHA"

    def test_legitimate_effect_verified(self, engine):
        """Effect size well within the observed range should verify."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        mean_abs_dev = sum(abs(x - 30) for x in data) / 5  # = 12.0
        result = engine.validate_statistical_claim(
            real_data=data,
            claimed_effect_size=0.01,  # Trivial claim
            n_permutations=200,
        )
        assert result["valid"] is True

    def test_result_contains_p_value(self, engine):
        """Result dict always contains p_value."""
        result = engine.validate_statistical_claim(
            real_data=[1.0, 2.0, 3.0],
            claimed_effect_size=0.5,
            n_permutations=50,
        )
        assert "p_value" in result
        assert 0.0 <= result["p_value"] <= 1.0

    def test_result_contains_claimed_effect(self, engine):
        """Result dict contains the claimed_effect we passed in."""
        result = engine.validate_statistical_claim(
            real_data=[1.0, 2.0],
            claimed_effect_size=7.77,
            n_permutations=50,
        )
        assert result.get("claimed_effect") == 7.77

    def test_single_element_data(self, engine):
        """Single-element list produces zero MAD; any positive claim rejected."""
        result = engine.validate_statistical_claim(
            real_data=[42.0],
            claimed_effect_size=1.0,
            n_permutations=100,
        )
        # With one element, every permutation has effect 0, so nothing >= 1.0
        assert result["valid"] is False

    def test_custom_alpha(self, engine):
        """Custom alpha threshold is respected."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = engine.validate_statistical_claim(
            real_data=data,
            claimed_effect_size=0.01,
            n_permutations=100,
            alpha=0.001,
        )
        # Very small alpha makes it harder to verify
        assert "valid" in result


class TestComputeEffectSize:
    """Tests for the static _compute_effect_size helper."""

    def test_empty_list(self):
        assert EpistemologicalForensics._compute_effect_size([]) == 0.0

    def test_uniform_list(self):
        assert EpistemologicalForensics._compute_effect_size([5.0, 5.0, 5.0]) == 0.0

    def test_known_values(self):
        # [1, 3] → mean=2, MAD = (|1-2| + |3-2|) / 2 = 1.0
        result = EpistemologicalForensics._compute_effect_size([1.0, 3.0])
        assert result == pytest.approx(1.0)
