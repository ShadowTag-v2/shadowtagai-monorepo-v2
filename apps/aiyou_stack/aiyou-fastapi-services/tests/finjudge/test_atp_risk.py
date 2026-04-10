"""
Tests for ATP 5-19 Risk Assessment Engine
"""

import pytest

from src.finjudge.core.atp_risk import (
    assess_probability_from_frequency,
    assess_probability_from_percentage,
    assess_residual_risk,
    assess_severity_from_loss,
    assess_severity_from_var,
    calculate_risk_from_loss,
    calculate_risk_from_var,
    calculate_risk_level,
    recommend_action,
    validate_risk_assessment,
)
from src.finjudge.models.base import Probability, RiskLevel, Severity


class TestProbabilityAssessment:
    """Test probability assessment functions"""

    def test_probability_frequent(self):
        """Test frequent probability (≥80%)"""
        assert assess_probability_from_percentage(80) == Probability.A
        assert assess_probability_from_percentage(95) == Probability.A
        assert assess_probability_from_percentage(100) == Probability.A

    def test_probability_likely(self):
        """Test likely probability (50-79%)"""
        assert assess_probability_from_percentage(50) == Probability.B
        assert assess_probability_from_percentage(65) == Probability.B
        assert assess_probability_from_percentage(79) == Probability.B

    def test_probability_occasional(self):
        """Test occasional probability (20-49%)"""
        assert assess_probability_from_percentage(20) == Probability.C
        assert assess_probability_from_percentage(35) == Probability.C
        assert assess_probability_from_percentage(49) == Probability.C

    def test_probability_seldom(self):
        """Test seldom probability (5-19%)"""
        assert assess_probability_from_percentage(5) == Probability.D
        assert assess_probability_from_percentage(10) == Probability.D
        assert assess_probability_from_percentage(19) == Probability.D

    def test_probability_unlikely(self):
        """Test unlikely probability (<5%)"""
        assert assess_probability_from_percentage(0) == Probability.E
        assert assess_probability_from_percentage(2.5) == Probability.E
        assert assess_probability_from_percentage(4.9) == Probability.E

    def test_probability_from_frequency(self):
        """Test probability calculation from historical frequency"""
        assert assess_probability_from_frequency(80, 100) == Probability.A
        assert assess_probability_from_frequency(50, 100) == Probability.B
        assert assess_probability_from_frequency(25, 100) == Probability.C
        assert assess_probability_from_frequency(10, 100) == Probability.D
        assert assess_probability_from_frequency(2, 100) == Probability.E

    def test_probability_invalid_inputs(self):
        """Test invalid probability inputs"""
        with pytest.raises(ValueError):
            assess_probability_from_percentage(-10)
        with pytest.raises(ValueError):
            assess_probability_from_percentage(150)
        with pytest.raises(ValueError):
            assess_probability_from_frequency(50, 0)
        with pytest.raises(ValueError):
            assess_probability_from_frequency(-5, 100)


class TestSeverityAssessment:
    """Test severity assessment functions"""

    def test_severity_catastrophic(self):
        """Test catastrophic severity (>$10M)"""
        assert assess_severity_from_loss(15_000_000) == Severity.I
        assert assess_severity_from_loss(50_000_000) == Severity.I

    def test_severity_critical(self):
        """Test critical severity ($1M-$10M)"""
        assert assess_severity_from_loss(1_000_000) == Severity.II
        assert assess_severity_from_loss(5_000_000) == Severity.II
        assert assess_severity_from_loss(10_000_000) == Severity.II

    def test_severity_moderate(self):
        """Test moderate severity ($100K-$1M)"""
        assert assess_severity_from_loss(100_000) == Severity.III
        assert assess_severity_from_loss(500_000) == Severity.III
        assert assess_severity_from_loss(999_999) == Severity.III

    def test_severity_negligible(self):
        """Test negligible severity (<$100K)"""
        assert assess_severity_from_loss(0) == Severity.IV
        assert assess_severity_from_loss(50_000) == Severity.IV
        assert assess_severity_from_loss(99_999) == Severity.IV

    def test_severity_negative_loss(self):
        """Test severity with negative loss (profit)"""
        # Absolute value should be used
        assert assess_severity_from_loss(-500_000) == Severity.III

    def test_severity_from_var(self):
        """Test severity assessment from VaR"""
        portfolio = 10_000_000

        # >20% portfolio = catastrophic
        assert assess_severity_from_var(2_500_000, portfolio) == Severity.I

        # 5-20% = critical
        assert assess_severity_from_var(1_000_000, portfolio) == Severity.II

        # 1-5% = moderate
        assert assess_severity_from_var(200_000, portfolio) == Severity.III

        # <1% = negligible
        assert assess_severity_from_var(50_000, portfolio) == Severity.IV

    def test_severity_from_var_invalid(self):
        """Test invalid VaR inputs"""
        with pytest.raises(ValueError):
            assess_severity_from_var(100_000, 0)
        with pytest.raises(ValueError):
            assess_severity_from_var(100_000, -1000000)


class TestRiskLevelCalculation:
    """Test risk level calculation from matrix"""

    def test_extremely_high_risks(self):
        """Test EH (Extremely High) risk combinations"""
        assert calculate_risk_level(Probability.A, Severity.I) == RiskLevel.EH
        assert calculate_risk_level(Probability.A, Severity.II) == RiskLevel.EH
        assert calculate_risk_level(Probability.B, Severity.I) == RiskLevel.EH

    def test_high_risks(self):
        """Test H (High) risk combinations"""
        assert calculate_risk_level(Probability.A, Severity.III) == RiskLevel.H
        assert calculate_risk_level(Probability.B, Severity.II) == RiskLevel.H
        assert calculate_risk_level(Probability.C, Severity.I) == RiskLevel.H

    def test_medium_risks(self):
        """Test M (Medium) risk combinations"""
        assert calculate_risk_level(Probability.A, Severity.IV) == RiskLevel.M
        assert calculate_risk_level(Probability.B, Severity.III) == RiskLevel.M
        assert calculate_risk_level(Probability.C, Severity.II) == RiskLevel.M
        assert calculate_risk_level(Probability.C, Severity.III) == RiskLevel.M
        assert calculate_risk_level(Probability.D, Severity.I) == RiskLevel.M
        assert calculate_risk_level(Probability.D, Severity.II) == RiskLevel.M
        assert calculate_risk_level(Probability.E, Severity.I) == RiskLevel.M

    def test_low_risks(self):
        """Test L (Low) risk combinations"""
        assert calculate_risk_level(Probability.B, Severity.IV) == RiskLevel.L
        assert calculate_risk_level(Probability.C, Severity.IV) == RiskLevel.L
        assert calculate_risk_level(Probability.D, Severity.III) == RiskLevel.L
        assert calculate_risk_level(Probability.D, Severity.IV) == RiskLevel.L
        assert calculate_risk_level(Probability.E, Severity.II) == RiskLevel.L
        assert calculate_risk_level(Probability.E, Severity.III) == RiskLevel.L
        assert calculate_risk_level(Probability.E, Severity.IV) == RiskLevel.L

    def test_complete_risk_calculation(self):
        """Test complete risk calculation from loss"""
        # High probability (70%), catastrophic loss ($20M) -> EH
        prob, sev, risk = calculate_risk_from_loss(70, 20_000_000)
        assert prob == Probability.B
        assert sev == Severity.I
        assert risk == RiskLevel.EH

        # Medium probability (30%), moderate loss ($500K) -> M
        prob, sev, risk = calculate_risk_from_loss(30, 500_000)
        assert prob == Probability.C
        assert sev == Severity.III
        assert risk == RiskLevel.M

        # Low probability (2%), negligible loss ($10K) -> L
        prob, sev, risk = calculate_risk_from_loss(2, 10_000)
        assert prob == Probability.E
        assert sev == Severity.IV
        assert risk == RiskLevel.L


class TestResidualRisk:
    """Test residual risk after mitigation"""

    def test_highly_effective_mitigation(self):
        """Test >75% effective mitigation (reduce by 2 levels)"""
        assert assess_residual_risk(RiskLevel.EH, 80) == RiskLevel.M
        assert assess_residual_risk(RiskLevel.H, 90) == RiskLevel.L
        assert assess_residual_risk(RiskLevel.M, 85) == RiskLevel.L

    def test_moderately_effective_mitigation(self):
        """Test 50-75% effective mitigation (reduce by 1 level)"""
        assert assess_residual_risk(RiskLevel.EH, 60) == RiskLevel.H
        assert assess_residual_risk(RiskLevel.H, 70) == RiskLevel.M
        assert assess_residual_risk(RiskLevel.M, 65) == RiskLevel.L

    def test_minimally_effective_mitigation(self):
        """Test <50% effective mitigation (no change)"""
        assert assess_residual_risk(RiskLevel.EH, 30) == RiskLevel.EH
        assert assess_residual_risk(RiskLevel.H, 40) == RiskLevel.H
        assert assess_residual_risk(RiskLevel.M, 45) == RiskLevel.M
        assert assess_residual_risk(RiskLevel.L, 25) == RiskLevel.L

    def test_mitigation_floor(self):
        """Test that L risk cannot be reduced further"""
        assert assess_residual_risk(RiskLevel.L, 100) == RiskLevel.L

    def test_mitigation_invalid(self):
        """Test invalid mitigation effectiveness"""
        with pytest.raises(ValueError):
            assess_residual_risk(RiskLevel.M, -10)
        with pytest.raises(ValueError):
            assess_residual_risk(RiskLevel.M, 150)


class TestDecisionSupport:
    """Test decision support functions"""

    def test_recommend_action_high_confidence(self):
        """Test recommendations with high confidence (≥80%)"""
        assert "DENY" in recommend_action(RiskLevel.EH, 90)
        assert "APPROVE_WITH_CONDITIONS" in recommend_action(RiskLevel.H, 85)
        assert "APPROVE_WITH_CONDITIONS" in recommend_action(RiskLevel.M, 88)
        assert "APPROVE" in recommend_action(RiskLevel.L, 95)

    def test_recommend_action_medium_confidence(self):
        """Test recommendations with medium confidence (60-80%)"""
        assert "ESCALATE" in recommend_action(RiskLevel.EH, 70)
        assert "ESCALATE" in recommend_action(RiskLevel.H, 65)
        assert "APPROVE_WITH_CONDITIONS" in recommend_action(RiskLevel.M, 75)
        assert "APPROVE" in recommend_action(RiskLevel.L, 70)

    def test_recommend_action_low_confidence(self):
        """Test recommendations with low confidence (<60%)"""
        assert "DENY" in recommend_action(RiskLevel.EH, 50)
        assert "DENY" in recommend_action(RiskLevel.H, 40)
        assert "DEFER" in recommend_action(RiskLevel.M, 55)
        assert "DEFER" in recommend_action(RiskLevel.L, 45)

    def test_validate_risk_assessment(self):
        """Test risk assessment validation"""
        # Valid assessments
        assert validate_risk_assessment(Probability.A, Severity.I, RiskLevel.EH)
        assert validate_risk_assessment(Probability.C, Severity.III, RiskLevel.M)
        assert validate_risk_assessment(Probability.E, Severity.IV, RiskLevel.L)

        # Invalid assessments
        assert not validate_risk_assessment(Probability.A, Severity.I, RiskLevel.L)
        assert not validate_risk_assessment(Probability.E, Severity.IV, RiskLevel.EH)


# ============================================================================
# Financial Edge Cases
# ============================================================================


class TestFinancialEdgeCases:
    """Test real-world financial edge cases"""

    def test_flash_crash_scenario(self):
        """Test flash crash risk (rare but catastrophic)"""
        # 1% probability, $100M loss
        prob, sev, risk = calculate_risk_from_loss(1, 100_000_000)
        assert prob == Probability.E  # Unlikely
        assert sev == Severity.I  # Catastrophic
        assert risk == RiskLevel.M  # Medium (E×I=M per matrix)

    def test_daily_trading_loss(self):
        """Test typical daily trading loss"""
        # 40% probability, $250K loss
        prob, sev, risk = calculate_risk_from_loss(40, 250_000)
        assert prob == Probability.C  # Occasional
        assert sev == Severity.III  # Moderate
        assert risk == RiskLevel.M  # Medium

    def test_counterparty_default(self):
        """Test counterparty default risk"""
        # 8% probability, $5M exposure
        prob, sev, risk = calculate_risk_from_loss(8, 5_000_000)
        assert prob == Probability.D  # Seldom
        assert sev == Severity.II  # Critical
        assert risk == RiskLevel.M  # Medium

    def test_market_making_risk(self):
        """Test market making position risk"""
        # 60% probability, $80K loss
        prob, sev, risk = calculate_risk_from_loss(60, 80_000)
        assert prob == Probability.B  # Likely
        assert sev == Severity.IV  # Negligible
        assert risk == RiskLevel.L  # Low

    def test_leveraged_portfolio(self):
        """Test highly leveraged portfolio VaR"""
        portfolio = 50_000_000
        var_95 = 15_000_000  # 30% of portfolio at risk

        prob, sev, risk = calculate_risk_from_var(75, var_95, portfolio)
        assert prob == Probability.B  # Likely
        assert sev == Severity.I  # Catastrophic (>20% portfolio)
        assert risk == RiskLevel.EH  # Extremely High
