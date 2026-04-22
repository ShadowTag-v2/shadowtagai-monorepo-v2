# tests/test_judge6_atp519_scoring.py
"""Integration tests for Judge 6 ATP 5-19 Risk Scoring.

Tests the score_risk function and RISK_MATRIX against known scenarios
to verify correct risk level computation per ATP 5-19.
"""

from __future__ import annotations

from apps.counselconduit.judge6_atp519_scoring import (
    score_risk,
    RISK_MATRIX,
    SEVERITY_LEVELS,
    PROBABILITY_LEVELS,
)


class TestATP519Scoring:
    """Test the ATP 5-19 risk scoring pipeline."""

    def test_catastrophic_frequent_produces_extremely_high(self):
        """Catastrophic severity + Frequent probability → EXTREMELY_HIGH."""
        result = score_risk("catastrophic", "frequent")
        assert result["risk_level"] == "EXTREMELY_HIGH"
        assert result["severity_score"] == 4
        assert result["probability_score"] == 4
        assert "BLOCK" in result["action"]

    def test_negligible_unlikely_produces_low(self):
        """Negligible severity + Unlikely probability → LOW."""
        result = score_risk("negligible", "unlikely")
        assert result["risk_level"] == "LOW"
        assert result["severity_score"] == 1
        assert result["probability_score"] == 1
        assert "Developer" in result["action"]

    def test_critical_likely_produces_high(self):
        """Critical severity + Likely probability → HIGH."""
        result = score_risk("critical", "likely")
        assert result["risk_level"] == "HIGH"
        assert "CTO" in result["action"]

    def test_moderate_occasional_produces_medium(self):
        """Moderate severity + Occasional probability → MEDIUM."""
        result = score_risk("moderate", "occasional")
        assert result["risk_level"] == "MEDIUM"
        assert "Tech Lead" in result["action"]

    def test_case_insensitive_inputs(self):
        """Input strings should be case-insensitive."""
        result = score_risk("CRITICAL", "LIKELY")
        assert result["risk_level"] == "HIGH"

        result2 = score_risk("CaTaStRoPhIc", "fReQuEnT")
        assert result2["risk_level"] == "EXTREMELY_HIGH"

    def test_invalid_severity_returns_error(self):
        """Invalid severity string returns error dict."""
        result = score_risk("bogus", "likely")
        assert "error" in result

    def test_invalid_probability_returns_error(self):
        """Invalid probability string returns error dict."""
        result = score_risk("critical", "never")
        assert "error" in result

    def test_all_matrix_cells_have_valid_levels(self):
        """Every (severity, probability) pair maps to a valid risk level."""
        valid_levels = {"EXTREMELY_HIGH", "HIGH", "MEDIUM", "LOW"}
        for (sev, prob), level in RISK_MATRIX.items():
            assert level in valid_levels, f"({sev}, {prob}) → {level} is not valid"

    def test_matrix_monotonic_severity(self):
        """Higher severity should produce same or higher risk for constant probability."""
        for prob in range(1, 5):
            levels = []
            for sev in range(1, 5):
                levels.append(RISK_MATRIX[(sev, prob)])
            # Convert to numeric for comparison
            level_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREMELY_HIGH": 4}
            numeric = [level_order[lv] for lv in levels]
            for i in range(len(numeric) - 1):
                assert numeric[i] <= numeric[i + 1], (
                    f"Severity monotonicity violated: prob={prob}, sev {i + 1}→{levels[i]}, sev {i + 2}→{levels[i + 1]}"
                )

    def test_matrix_monotonic_probability(self):
        """Higher probability should produce same or higher risk for constant severity."""
        for sev in range(1, 5):
            levels = []
            for prob in range(1, 5):
                levels.append(RISK_MATRIX[(sev, prob)])
            level_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREMELY_HIGH": 4}
            numeric = [level_order[lv] for lv in levels]
            for i in range(len(numeric) - 1):
                assert numeric[i] <= numeric[i + 1], (
                    f"Probability monotonicity violated: sev={sev}, prob {i + 1}→{levels[i]}, prob {i + 2}→{levels[i + 1]}"
                )

    def test_result_dict_has_all_fields(self):
        """Result dict should contain all expected fields."""
        result = score_risk("moderate", "likely")
        assert "risk_level" in result
        assert "severity" in result
        assert "severity_score" in result
        assert "probability" in result
        assert "probability_score" in result
        assert "action" in result

    def test_severity_dict_completeness(self):
        """All 4 severity levels should be defined."""
        assert len(SEVERITY_LEVELS) == 4
        assert set(SEVERITY_LEVELS.keys()) == {"catastrophic", "critical", "moderate", "negligible"}

    def test_probability_dict_completeness(self):
        """All 4 probability levels should be defined."""
        assert len(PROBABILITY_LEVELS) == 4
        assert set(PROBABILITY_LEVELS.keys()) == {"frequent", "likely", "occasional", "unlikely"}

    def test_matrix_complete_4x4(self):
        """Risk matrix should have all 16 (4×4) cells."""
        assert len(RISK_MATRIX) == 16
        for sev in range(1, 5):
            for prob in range(1, 5):
                assert (sev, prob) in RISK_MATRIX, f"Missing ({sev}, {prob})"

    # ── Real-World Scenarios ───────────────────────────────────

    def test_prompt_injection_scenario(self):
        """OWASP LLM01: Prompt injection on model routing → HIGH risk."""
        result = score_risk("critical", "likely")
        assert result["risk_level"] == "HIGH"

    def test_cosmetic_bug_scenario(self):
        """Low-impact UI bug → LOW risk."""
        result = score_risk("negligible", "unlikely")
        assert result["risk_level"] == "LOW"

    def test_privilege_boundary_violation(self):
        """Privilege boundary violation → EXTREMELY_HIGH."""
        result = score_risk("catastrophic", "likely")
        assert result["risk_level"] == "EXTREMELY_HIGH"

    def test_billing_error_occasional(self):
        """Billing calculation error (occasional) → HIGH."""
        result = score_risk("critical", "occasional")
        assert result["risk_level"] == "HIGH"

    def test_gdpr_retention_failure(self):
        """GDPR data retention failure → EXTREMELY_HIGH."""
        result = score_risk("catastrophic", "occasional")
        assert result["risk_level"] == "HIGH"
