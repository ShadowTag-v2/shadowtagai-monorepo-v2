"""
Unit tests for ATP 5-19 Risk Matrix
Tests risk calculation, approval authority, and edge cases
"""

import pytest
from src.risk_matrix import (
    Probability,
    Severity,
    RiskLevel,
    calculate_risk_level,
    determine_approval_authority,
    assess_risk,
)


class TestRiskMatrixLookup:
    """Test ATP 5-19 matrix lookup correctness"""

    def test_extremely_high_risk_combinations(self):
        """Test EH (Extremely High) risk classifications"""
        # A×I = EH
        assert calculate_risk_level(Probability.A, Severity.I) == RiskLevel.EH
        # A×II = EH
        assert calculate_risk_level(Probability.A, Severity.II) == RiskLevel.EH
        # B×I = EH
        assert calculate_risk_level(Probability.B, Severity.I) == RiskLevel.EH
        # C×I = EH
        assert calculate_risk_level(Probability.C, Severity.I) == RiskLevel.EH

    def test_high_risk_combinations(self):
        """Test H (High) risk classifications"""
        # A×III = H
        assert calculate_risk_level(Probability.A, Severity.III) == RiskLevel.H
        # B×II = H
        assert calculate_risk_level(Probability.B, Severity.II) == RiskLevel.H
        # B×III = H
        assert calculate_risk_level(Probability.B, Severity.III) == RiskLevel.H
        # C×II = H
        assert calculate_risk_level(Probability.C, Severity.II) == RiskLevel.H
        # D×I = H
        assert calculate_risk_level(Probability.D, Severity.I) == RiskLevel.H

    def test_medium_risk_combinations(self):
        """Test M (Medium) risk classifications"""
        # A×IV = M
        assert calculate_risk_level(Probability.A, Severity.IV) == RiskLevel.M
        # B×IV = M
        assert calculate_risk_level(Probability.B, Severity.IV) == RiskLevel.M
        # C×III = M
        assert calculate_risk_level(Probability.C, Severity.III) == RiskLevel.M
        # D×II = M
        assert calculate_risk_level(Probability.D, Severity.II) == RiskLevel.M
        # D×III = M
        assert calculate_risk_level(Probability.D, Severity.III) == RiskLevel.M
        # E×I = M
        assert calculate_risk_level(Probability.E, Severity.I) == RiskLevel.M
        # E×II = M
        assert calculate_risk_level(Probability.E, Severity.II) == RiskLevel.M

    def test_low_risk_combinations(self):
        """Test L (Low) risk classifications"""
        # C×IV = L
        assert calculate_risk_level(Probability.C, Severity.IV) == RiskLevel.L
        # D×IV = L
        assert calculate_risk_level(Probability.D, Severity.IV) == RiskLevel.L
        # E×III = L
        assert calculate_risk_level(Probability.E, Severity.III) == RiskLevel.L
        # E×IV = L
        assert calculate_risk_level(Probability.E, Severity.IV) == RiskLevel.L


class TestApprovalAuthority:
    """Test approval authority determination"""

    def test_financial_thresholds(self):
        """Test financial amount-based approval"""
        # $50K+ requires CFO
        authority, requires = determine_approval_authority(RiskLevel.M, 50_000)
        assert authority == "CFO"
        assert requires is True

        authority, requires = determine_approval_authority(RiskLevel.L, 75_000)
        assert authority == "CFO"
        assert requires is True

        # $10K-50K requires Finance Director
        authority, requires = determine_approval_authority(RiskLevel.M, 25_000)
        assert authority == "Finance Director"
        assert requires is True

        # <$10K follows risk-based rules
        authority, requires = determine_approval_authority(RiskLevel.L, 5_000)
        assert authority == "Automated"
        assert requires is False

    def test_risk_based_approval(self):
        """Test risk level-based approval (no financial amount)"""
        # EH = C-Suite + Board
        authority, requires = determine_approval_authority(RiskLevel.EH, 0)
        assert authority == "C-Suite + Board"
        assert requires is True

        # H = Senior Executive
        authority, requires = determine_approval_authority(RiskLevel.H, 0)
        assert authority == "Senior Executive"
        assert requires is True

        # M = Department Head
        authority, requires = determine_approval_authority(RiskLevel.M, 0)
        assert authority == "Department Head"
        assert requires is True

        # L = Automated
        authority, requires = determine_approval_authority(RiskLevel.L, 0)
        assert authority == "Automated"
        assert requires is False

    def test_combined_financial_and_risk(self):
        """Test that financial thresholds override risk-based approval"""
        # High amount + low risk still requires CFO
        authority, requires = determine_approval_authority(RiskLevel.L, 100_000)
        assert authority == "CFO"
        assert requires is True


class TestRiskAssessment:
    """Test complete risk assessment flow"""

    def test_basic_risk_assessment(self):
        """Test basic risk assessment creation"""
        assessment = assess_risk(
            probability=Probability.B,
            severity=Severity.II,
            rationale="Test transaction with moderate risk",
            mitigations=["Verify vendor", "Require dual approval"],
            amount_usd=75_000,
        )

        assert assessment.probability == Probability.B
        assert assessment.severity == Severity.II
        assert assessment.risk_level == RiskLevel.H  # B×II = H
        assert assessment.requires_approval is True
        assert assessment.approval_authority == "CFO"  # $75K
        assert len(assessment.mitigations) == 2

    def test_mitigation_reduces_severity(self):
        """Test that mitigations reduce residual risk"""
        assessment = assess_risk(
            probability=Probability.C, severity=Severity.II, rationale="Test with mitigations", mitigations=["Control A", "Control B"], amount_usd=0
        )

        # Original: C×II = H
        assert assessment.risk_level == RiskLevel.H
        # Residual: C×III = M (severity reduced by one level)
        assert assessment.residual_risk == RiskLevel.M

    def test_no_mitigations(self):
        """Test assessment without mitigations"""
        assessment = assess_risk(probability=Probability.D, severity=Severity.IV, rationale="Low risk, no mitigations needed", amount_usd=0)

        assert assessment.risk_level == RiskLevel.L
        assert assessment.residual_risk == RiskLevel.L
        assert len(assessment.mitigations) == 0

    def test_catastrophic_severity_no_reduction(self):
        """Test that Severity I cannot be reduced below I"""
        assessment = assess_risk(
            probability=Probability.A, severity=Severity.I, rationale="Catastrophic risk", mitigations=["All possible controls"], amount_usd=0
        )

        assert assessment.severity == Severity.I
        assert assessment.risk_level == RiskLevel.EH
        # Residual should be II (reduced by one)
        assert assessment.residual_risk == RiskLevel.EH  # A×II = EH


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_all_probability_severity_combinations(self):
        """Verify all 20 combinations in ATP 5-19 matrix are defined"""
        probabilities = [Probability.A, Probability.B, Probability.C, Probability.D, Probability.E]
        severities = [Severity.I, Severity.II, Severity.III, Severity.IV]

        for prob in probabilities:
            for sev in severities:
                risk_level = calculate_risk_level(prob, sev)
                assert risk_level in [RiskLevel.EH, RiskLevel.H, RiskLevel.M, RiskLevel.L]

    def test_zero_amount(self):
        """Test approval with zero financial amount"""
        authority, requires = determine_approval_authority(RiskLevel.L, 0)
        assert authority == "Automated"
        assert requires is False

    def test_very_large_amount(self):
        """Test approval with very large financial amount"""
        authority, requires = determine_approval_authority(RiskLevel.L, 10_000_000)
        assert authority == "CFO"
        assert requires is True

    def test_risk_assessment_fields_populated(self):
        """Test that all required fields are populated"""
        assessment = assess_risk(
            probability=Probability.C, severity=Severity.III, rationale="Complete field test", mitigations=["Control 1"], amount_usd=15_000
        )

        assert assessment.probability is not None
        assert assessment.severity is not None
        assert assessment.risk_level is not None
        assert assessment.rationale is not None
        assert isinstance(assessment.mitigations, list)
        assert assessment.residual_risk is not None
        assert assessment.requires_approval is not None
        assert assessment.approval_authority is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
