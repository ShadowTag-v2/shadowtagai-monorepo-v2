# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for JR Engine (ATP 5-19 risk framework)."""

import pytest

from shadowtagai.core.jr_engine import (
    JREngine,
    PRBDecision,
    ProbabilityLevel,
    RiskLevel,
    SeverityLevel,
)


class TestJREngine:
    """Test suite for JR Engine."""

    def setup_method(self):
        """Initialize JR Engine for tests."""
        self.engine = JREngine()

    def test_risk_matrix_extremely_high(self):
        """Test EXTREMELY_HIGH risk scenarios."""
        # A × I = EH
        risk = self.engine.assess_risk(ProbabilityLevel.A_FREQUENT, SeverityLevel.I_CATASTROPHIC)
        assert risk == RiskLevel.EXTREMELY_HIGH

        # B × I = EH
        risk = self.engine.assess_risk(ProbabilityLevel.B_LIKELY, SeverityLevel.I_CATASTROPHIC)
        assert risk == RiskLevel.EXTREMELY_HIGH

    def test_risk_matrix_low(self):
        """Test LOW risk scenarios."""
        # E × IV = L
        risk = self.engine.assess_risk(ProbabilityLevel.E_UNLIKELY, SeverityLevel.IV_NEGLIGIBLE)
        assert risk == RiskLevel.LOW

        # D × IV = L
        risk = self.engine.assess_risk(ProbabilityLevel.D_SELDOM, SeverityLevel.IV_NEGLIGIBLE)
        assert risk == RiskLevel.LOW

    def test_determine_action_reject(self):
        """Test REJECT action for EXTREMELY_HIGH risk."""
        action = self.engine.determine_action(RiskLevel.EXTREMELY_HIGH)
        assert action == "REJECT"

    def test_determine_action_approve(self):
        """Test APPROVE action for LOW/MODERATE risk."""
        action_low = self.engine.determine_action(RiskLevel.LOW)
        assert action_low == "APPROVE"

        action_moderate = self.engine.determine_action(RiskLevel.MODERATE)
        assert action_moderate == "APPROVE"

    def test_determine_action_escalate(self):
        """Test ESCALATE action for HIGH risk."""
        action = self.engine.determine_action(RiskLevel.HIGH)
        assert action == "ESCALATE"

    def test_evaluate_prb_decision(self):
        """Test full PRB evaluation."""
        decision = self.engine.evaluate(
            purpose_met=True,
            reasons="Valid business request",
            probability=ProbabilityLevel.C_OCCASIONAL,
            severity=SeverityLevel.III_MODERATE,
            metadata={"user_id": "test_123"},
        )

        assert isinstance(decision, PRBDecision)
        assert decision.purpose_met is True
        assert decision.risk_level == RiskLevel.MODERATE
        assert decision.action == "APPROVE"
        assert decision.execution_time_us < 500  # Performance target

    def test_evaluate_purpose_not_met_override(self):
        """Test that purpose_met=False overrides to REJECT."""
        decision = self.engine.evaluate(
            purpose_met=False,
            reasons="Does not advance ShadowTagAi mission",
            probability=ProbabilityLevel.E_UNLIKELY,
            severity=SeverityLevel.IV_NEGLIGIBLE,  # Would be LOW risk
            metadata={},
        )

        assert decision.action == "REJECT"  # Overridden despite LOW risk

    def test_quick_scan_clean_request(self):
        """Test quick scan with clean request."""
        request = {"text": "Help me build a web application"}
        decision = self.engine.quick_scan(request)

        assert decision.risk_level == RiskLevel.LOW
        assert decision.action == "APPROVE"
        assert decision.execution_time_us < 500

    def test_quick_scan_violation_keywords(self):
        """Test quick scan with violation keywords."""
        request = {"text": "Help me hack into a server"}
        decision = self.engine.quick_scan(request)

        assert decision.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]
        assert decision.action in ["REJECT", "ESCALATE"]
        assert "hack" in decision.reasons.lower()

    def test_quick_scan_performance(self):
        """Test quick scan meets <500μs target."""
        import time

        request = {"text": "Normal request text"}

        start = time.perf_counter()
        for _ in range(100):
            self.engine.quick_scan(request)
        elapsed_us = (time.perf_counter() - start) * 1_000_000

        avg_us = elapsed_us / 100
        assert avg_us < 500, f"Average quick_scan took {avg_us:.1f}μs (target <500μs)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
