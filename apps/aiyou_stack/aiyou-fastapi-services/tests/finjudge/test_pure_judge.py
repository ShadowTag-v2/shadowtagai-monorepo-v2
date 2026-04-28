# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for Pure Judge Engine (v0.2)"""

from uuid import uuid4

import pytest

from src.finjudge.core.pure_judge import PureJudge
from src.finjudge.models.judge import (
    Actor,
    ActorRole,
    DecisionContext,
    Disposition,
    Exposure,
    Flags,
    JudgeRequest,
    LiquidityMetrics,
    Metrics,
    Objective,
    PnLDistribution,
    RiskLevel,
    TailRisk,
    TimeHorizon,
    Volatility,
)


@pytest.fixture
def pure_judge():
    """Create pure judge instance"""
    return PureJudge(version="test-v0.2.0")


@pytest.fixture
def basic_request():
    """Create basic judge request"""
    return JudgeRequest(
        decision_id=str(uuid4()),
        module="test_module",
        actor=Actor(role=ActorRole.TRADER, org_unit="Test Desk", jurisdiction="US"),
        intent_nl="Test decision for risk assessment",
        context=DecisionContext(
            time_horizon=TimeHorizon.SWING,
            objective=Objective.ALPHA,
            constraints=[],
        ),
        metrics=Metrics(
            exposure=Exposure(notional=500000.0, pct_aum=2.5, leverage_ratio=1.0),
            tail_risk=TailRisk(var_95=75000.0, cvar_95=125000.0),
        ),
        flags=Flags(),
    )


class TestPureJudgeBasics:
    """Test basic pure judge functionality"""

    def test_judge_initialization(self, pure_judge):
        """Test judge initializes correctly"""
        assert pure_judge.version == "test-v0.2.0"
        assert pure_judge.synthesizer is not None

    def test_basic_judgment(self, pure_judge, basic_request):
        """Test basic judgment produces valid ruling"""
        ruling = pure_judge.judge(basic_request)

        # Check ruling structure
        assert ruling.decision_id == basic_request.decision_id
        assert ruling.judge_version == "test-v0.2.0"
        assert ruling.risk_matrix is not None
        assert ruling.numeric_overview is not None
        assert ruling.recommendation is not None
        assert ruling.explanation_nl is not None
        assert ruling.audit_trail is not None

    def test_audit_trail_created(self, pure_judge, basic_request):
        """Test audit trail is created"""
        ruling = pure_judge.judge(basic_request)

        audit = ruling.audit_trail
        assert audit.input_hash is not None
        assert len(audit.input_hash) == 64  # SHA-256 hex
        assert audit.feature_vector_hash is not None
        assert isinstance(audit.overrides, list)


class TestRiskClassification:
    """Test risk classification logic"""

    def test_low_risk_scenario(self, pure_judge):
        """Test low risk classification"""
        request = JudgeRequest(
            module="test",
            actor=Actor(role=ActorRole.PM, org_unit="Test", jurisdiction="US"),
            intent_nl="Small position, low risk",
            context=DecisionContext(time_horizon=TimeHorizon.LONG_TERM, objective=Objective.INCOME),
            metrics=Metrics(
                exposure=Exposure(notional=50000.0, pct_aum=1.0, leverage_ratio=1.0),
                tail_risk=TailRisk(var_95=5000.0),
            ),
        )

        ruling = pure_judge.judge(request)

        # Low risk should result in APPROVE
        assert ruling.risk_matrix.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE]
        assert ruling.recommendation.disposition in [Disposition.APPROVE, Disposition.MODIFY]

    def test_high_risk_scenario(self, pure_judge):
        """Test high risk classification"""
        request = JudgeRequest(
            module="test",
            actor=Actor(role=ActorRole.TRADER, org_unit="Test", jurisdiction="US"),
            intent_nl="Large leveraged position",
            context=DecisionContext(
                time_horizon=TimeHorizon.INTRA_DAY,
                objective=Objective.SPECULATION,
            ),
            metrics=Metrics(
                exposure=Exposure(notional=25000000.0, pct_aum=25.0, leverage_ratio=3.0),
                tail_risk=TailRisk(var_95=8000000.0, cvar_95=15000000.0),
                volatility=Volatility(realized_vol=0.45, regime_tag="stressed"),
            ),
        )

        ruling = pure_judge.judge(request)

        # High risk should result in MODIFY, ESCALATE, or REJECT
        assert ruling.risk_matrix.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]
        assert ruling.recommendation.disposition in [
            Disposition.MODIFY,
            Disposition.ESCALATE,
            Disposition.REJECT,
        ]

    def test_regulatory_flag_rejection(self, pure_judge):
        """Test regulatory flags trigger rejection"""
        request = JudgeRequest(
            module="test",
            actor=Actor(role=ActorRole.COMPLIANCE, org_unit="Test", jurisdiction="US"),
            intent_nl="Transaction with regulatory violation",
            context=DecisionContext(time_horizon=TimeHorizon.LONG_TERM, objective=Objective.HEDGE),
            metrics=Metrics(exposure=Exposure(notional=100000.0, pct_aum=2.0)),
            flags=Flags(regulatory_flags=["OFAC_violation", "concentration_breach"]),
        )

        ruling = pure_judge.judge(request)

        # Regulatory flags should trigger REJECT
        assert ruling.recommendation.disposition == Disposition.REJECT


class TestFeatureSynthesis:
    """Test feature synthesis layer"""

    def test_capital_at_risk_calculated(self, pure_judge):
        """Test capital at risk feature is synthesized"""
        request = JudgeRequest(
            module="test",
            actor=Actor(role=ActorRole.PM, org_unit="Test", jurisdiction="US"),
            intent_nl="Test capital at risk",
            context=DecisionContext(time_horizon=TimeHorizon.SWING, objective=Objective.ALPHA),
            metrics=Metrics(
                exposure=Exposure(
                    notional=1000000.0,
                    pct_aum=15.0,  # High concentration
                ),
            ),
        )

        ruling = pure_judge.judge(request)

        # Should identify concentration as risk driver
        assert ruling.numeric_overview.primary_risk_driver in ["concentration", "general_risk"]

    def test_liquidity_heat_calculated(self, pure_judge):
        """Test liquidity heat feature is synthesized"""
        request = JudgeRequest(
            module="test",
            actor=Actor(role=ActorRole.TRADER, org_unit="Test", jurisdiction="US"),
            intent_nl="Test liquidity risk",
            context=DecisionContext(
                time_horizon=TimeHorizon.INTRA_DAY,
                objective=Objective.SPECULATION,
            ),
            metrics=Metrics(
                exposure=Exposure(notional=500000.0, pct_aum=5.0),
                liquidity_metrics=LiquidityMetrics(
                    spread_bps=150.0,  # Wide spread
                    depth_score=20.0,  # Low depth
                    days_to_liquidate=7.0,  # Slow to liquidate
                ),
            ),
        )

        ruling = pure_judge.judge(request)

        # Should identify liquidity as primary risk
        assert (
            "liquidity" in ruling.numeric_overview.primary_risk_driver
            or ruling.recommendation.disposition == Disposition.MODIFY
        )


class TestExplanationGeneration:
    """Test explanation generation"""

    def test_explanation_completeness(self, pure_judge, basic_request):
        """Test explanation includes all required components"""
        ruling = pure_judge.judge(basic_request)

        explanation = ruling.explanation_nl
        assert len(explanation.short_summary) > 0
        assert len(explanation.short_summary) <= 500  # Cap enforced
        assert len(explanation.detail_bullets) >= 3  # WHAT, WHY, WHERE
        assert any("WHAT:" in bullet for bullet in explanation.detail_bullets)
        assert any("WHY" in bullet for bullet in explanation.detail_bullets)
        assert any("WHERE" in bullet for bullet in explanation.detail_bullets)

    def test_rationale_summary_format(self, pure_judge, basic_request):
        """Test rationale summary is well-formatted"""
        ruling = pure_judge.judge(basic_request)

        rationale = ruling.risk_matrix.rationale_summary
        assert len(rationale) >= 20  # Min length requirement
        assert "probability" in rationale.lower() or "%" in rationale


class TestRealWorldScenarios:
    """Test real-world financial scenarios"""

    def test_burn_rate_increase(self, pure_judge):
        """Test financial runway / burn rate scenario"""
        request = JudgeRequest(
            decision_id="burn_rate_increase_2025_11",
            module="financial_runway_monitor",
            actor=Actor(role=ActorRole.CFO, org_unit="Finance", jurisdiction="US"),
            intent_nl="Approve hiring 3 engineers, increasing monthly burn from $180k to $240k",
            context=DecisionContext(
                time_horizon=TimeHorizon.LONG_TERM,
                objective=Objective.ALPHA,
                constraints=["max_12mo_runway"],
            ),
            metrics=Metrics(
                exposure=Exposure(
                    notional=720000.0,  # 12 months * $60k increase
                    pct_aum=33.3,  # Significant % of runway
                    leverage_ratio=1.0,
                ),
                custom={
                    "current_burn": 180000,
                    "proposed_burn": 240000,
                    "runway_months_current": 18,
                    "runway_months_proposed": 13.5,
                    "pct_increase": 33.3,
                },
            ),
            flags=Flags(policy_flags=["approaching_12mo_runway_threshold"]),
        )

        ruling = pure_judge.judge(request)

        # Should identify as HIGH or MODERATE risk with MODIFY disposition
        assert ruling.risk_matrix.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE]
        assert ruling.recommendation.disposition in [Disposition.MODIFY, Disposition.ESCALATE]
        assert len(ruling.recommendation.required_controls) > 0

    def test_large_trade_approval(self, pure_judge):
        """Test large trade approval scenario"""
        request = JudgeRequest(
            module="trading_system",
            actor=Actor(role=ActorRole.TRADER, org_unit="Equity Desk", jurisdiction="US"),
            intent_nl="Execute $10M NVDA block trade with 2x leverage",
            context=DecisionContext(
                time_horizon=TimeHorizon.SWING,
                objective=Objective.ALPHA,
                constraints=["max_10_pct_position"],
            ),
            metrics=Metrics(
                exposure=Exposure(notional=10000000.0, pct_aum=8.5, leverage_ratio=2.0),
                tail_risk=TailRisk(var_95=1500000.0, var_99=3000000.0),
                pnl_distribution_summary=PnLDistribution(
                    mean=200000.0,
                    stddev=800000.0,
                    skew=-0.6,  # Negative skew
                    kurtosis=5.2,  # Fat tails
                ),
                volatility=Volatility(realized_vol=0.38, implied_vol=0.45, regime_tag="high_vol"),
                liquidity_metrics=LiquidityMetrics(
                    spread_bps=8.0,
                    depth_score=85.0,
                    days_to_liquidate=1.5,
                ),
            ),
        )

        ruling = pure_judge.judge(request)

        # Large leveraged position should be HIGH risk with controls
        assert ruling.risk_matrix.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE]
        assert ruling.recommendation.disposition in [Disposition.APPROVE, Disposition.MODIFY]
        # Should have some controls due to leverage/size
        assert (
            len(ruling.recommendation.required_controls) > 0
            or ruling.risk_matrix.risk_level == RiskLevel.MODERATE
        )
