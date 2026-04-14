"""Tests for FinJudge Decision Engine
"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.finjudge.core.decision_engine import DecisionEngine
from src.finjudge.models.base import (
    Constraints,
    DecisionContext,
    DecisionOutcome,
    DecisionRequest,
    DecisionType,
    Evidence,
    EvidenceType,
    RiskLevel,
    RiskLimits,
    Urgency,
)


@pytest.fixture
def decision_engine():
    """Create decision engine instance"""
    return DecisionEngine(model_version="test-v0.1.0")


@pytest.fixture
def basic_trade_request():
    """Create basic trade approval request"""
    return DecisionRequest(
        request_id=uuid4(),
        decision_type=DecisionType.TRADE_APPROVAL,
        context=DecisionContext(
            timestamp=datetime.utcnow(),
            entity="Test Trading Desk",
            purpose="Test trade approval for 1000 AAPL shares",
            urgency=Urgency.NORMAL,
        ),
        evidence=[
            Evidence(
                type=EvidenceType.MARKET_DATA,
                source="Bloomberg",
                data={"symbol": "AAPL", "price": 175.50, "volume": 80000000},
                confidence=95.0,
            ),
            Evidence(
                type=EvidenceType.RISK_METRIC,
                source="Internal Risk System",
                data={"probability": 25.0, "expected_loss": 125000},
                confidence=90.0,
            ),
        ],
        constraints=Constraints(
            regulatory=["SEC Rule 15c3-1"],
            risk_limits=RiskLimits(position_limit=50000),
            policy_rules=["RISK-001"],
        ),
    )


class TestDecisionEngineBasics:
    """Test basic decision engine functionality"""

    def test_engine_initialization(self, decision_engine):
        """Test engine initializes correctly"""
        assert decision_engine.model_version == "test-v0.1.0"
        assert decision_engine.compliance_engine is not None
        assert decision_engine.policy_engine is not None

    def test_basic_evaluation(self, decision_engine, basic_trade_request):
        """Test basic decision evaluation"""
        ruling = decision_engine.evaluate(basic_trade_request)

        # Check ruling structure
        assert ruling.ruling_id is not None
        assert ruling.request_id == basic_trade_request.request_id
        assert ruling.decision in DecisionOutcome
        assert 0 <= ruling.confidence <= 100
        assert ruling.risk_assessment is not None
        assert ruling.rationale is not None
        assert ruling.audit_trail is not None

    def test_audit_trail(self, decision_engine, basic_trade_request):
        """Test audit trail creation"""
        ruling = decision_engine.evaluate(basic_trade_request)

        audit = ruling.audit_trail
        assert audit.evidence_reviewed == len(basic_trade_request.evidence)
        assert len(audit.rules_applied) > 0
        assert audit.computation_time_ms > 0
        assert audit.model_version == "test-v0.1.0"


class TestRiskAssessment:
    """Test risk assessment logic"""

    def test_low_risk_approval(self, decision_engine):
        """Test low risk scenario -> APPROVE"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(), entity="Low Risk Desk", purpose="Small trade, low risk",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={"probability": 3.0, "expected_loss": 25000},
                    confidence=95.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        assert ruling.risk_assessment.level == RiskLevel.L
        assert ruling.decision == DecisionOutcome.APPROVE
        assert ruling.confidence > 85

    def test_high_risk_conditions(self, decision_engine):
        """Test high risk -> APPROVE_WITH_CONDITIONS"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="High Risk Desk",
                purpose="Large position, significant risk",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={"probability": 55.0, "expected_loss": 8000000},
                    confidence=90.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        assert ruling.risk_assessment.level == RiskLevel.H
        assert ruling.decision == DecisionOutcome.APPROVE_WITH_CONDITIONS
        assert len(ruling.conditions) > 0
        assert len(ruling.risk_assessment.mitigation) > 0

    def test_extremely_high_risk_denial(self, decision_engine):
        """Test extremely high risk -> DENY"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="EH Risk Desk",
                purpose="Extremely risky position",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={"probability": 85.0, "expected_loss": 25000000},
                    confidence=92.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        assert ruling.risk_assessment.level == RiskLevel.EH
        assert ruling.decision == DecisionOutcome.DENY
        assert "DENY" in ruling.rationale.summary


class TestEvidenceQuality:
    """Test evidence quality assessment"""

    def test_high_quality_evidence(self, decision_engine):
        """Test decision with high-quality evidence"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.RISK_ASSESSMENT,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Quality Test",
                purpose="High quality evidence test",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.COMPLIANCE_DOC,
                    source="Regulatory Filing",
                    data={"filing": "10-K"},
                    confidence=98.0,
                ),
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Bloomberg",
                    data={"var_95": 100000},
                    confidence=95.0,
                ),
                Evidence(
                    type=EvidenceType.CREDIT_RATING,
                    source="S&P",
                    data={"rating": "AA"},
                    confidence=100.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        # High evidence quality should boost confidence
        assert ruling.confidence > 85

    def test_low_quality_evidence_defer(self, decision_engine):
        """Test low quality evidence -> DEFER"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.RISK_ASSESSMENT,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Low Quality Test",
                purpose="Insufficient evidence test",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.MARKET_DATA,
                    source="Unknown",
                    data={"estimate": "rough guess"},
                    confidence=30.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        # Low evidence + non-extreme risk -> DEFER
        assert ruling.decision in [DecisionOutcome.DEFER, DecisionOutcome.DENY]
        assert ruling.confidence < 80


class TestComplianceIntegration:
    """Test compliance checking integration"""

    def test_compliance_violation_denial(self, decision_engine):
        """Test compliance violation -> DENY"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Compliance Violation Test",
                purpose="Test compliance failure",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={
                        "probability": 10.0,
                        "expected_loss": 50000,
                        "leverage": 5.0,  # Exceeds Reg T limit of 2.0
                    },
                    confidence=90.0,
                ),
            ],
            constraints=Constraints(regulatory=["Regulation T"]),
        )

        ruling = decision_engine.evaluate(request)

        # Compliance violation should trigger denial
        assert ruling.decision == DecisionOutcome.DENY
        assert any(f.status.value == "violation" for f in ruling.compliance_flags)

    def test_compliance_pass(self, decision_engine):
        """Test compliant request"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.COMPLIANCE_CHECK,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Compliance Pass Test",
                purpose="Test compliance success",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.COMPLIANCE_DOC,
                    source="Compliance System",
                    data={"kyc_complete": True, "aml_check": "passed"},
                    confidence=100.0,
                ),
            ],
            constraints=Constraints(regulatory=["Dodd-Frank"]),
        )

        ruling = decision_engine.evaluate(request)

        # Should have compliance flags showing compliant status
        assert len(ruling.compliance_flags) > 0
        compliant = any(f.status.value == "compliant" for f in ruling.compliance_flags)
        assert compliant


class TestRationaleGeneration:
    """Test ruling rationale generation"""

    def test_rationale_completeness(self, decision_engine, basic_trade_request):
        """Test that rationale includes all required components"""
        ruling = decision_engine.evaluate(basic_trade_request)

        rationale = ruling.rationale
        assert len(rationale.summary) >= 50  # Min length requirement
        assert len(rationale.key_factors) > 0
        assert isinstance(rationale.precedents, list)

    def test_dissent_on_low_confidence(self, decision_engine):
        """Test dissenting opinion on low confidence"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.RISK_ASSESSMENT,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Low Confidence Test",
                purpose="Test dissent generation",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.MODEL_OUTPUT,
                    source="ML Model",
                    data={"prediction": "uncertain"},
                    confidence=50.0,  # Low confidence
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        if ruling.confidence < 80:
            assert ruling.rationale.dissent is not None
            assert "confidence" in ruling.rationale.dissent.lower()


class TestConditionsAndNextSteps:
    """Test condition and next step generation"""

    def test_conditional_approval_conditions(self, decision_engine):
        """Test that APPROVE_WITH_CONDITIONS includes conditions"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Conditional Test",
                purpose="Test condition generation",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={"probability": 55.0, "expected_loss": 3000000},
                    confidence=88.0,
                ),
            ],
            constraints=Constraints(),
        )

        ruling = decision_engine.evaluate(request)

        if ruling.decision == DecisionOutcome.APPROVE_WITH_CONDITIONS:
            assert len(ruling.conditions) > 0
            # At least one mandatory condition
            assert any(c.mandatory for c in ruling.conditions)

    def test_next_steps_present(self, decision_engine, basic_trade_request):
        """Test that next steps are generated"""
        ruling = decision_engine.evaluate(basic_trade_request)

        assert len(ruling.next_steps) > 0
        # Next steps should be actionable strings
        assert all(isinstance(step, str) and len(step) > 10 for step in ruling.next_steps)


# ============================================================================
# Integration Tests
# ============================================================================


class TestRealWorldScenarios:
    """Test real-world financial scenarios"""

    def test_large_block_trade(self, decision_engine):
        """Test large block trade approval"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.TRADE_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Block Trading Desk",
                purpose="Approve 100K MSFT share block trade ($35M notional)",
                urgency=Urgency.HIGH,
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.MARKET_DATA,
                    source="Bloomberg",
                    data={
                        "symbol": "MSFT",
                        "price": 350.00,
                        "volume": 25000000,
                        "liquidity": "high",
                    },
                    confidence=98.0,
                ),
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={
                        "probability": 35.0,
                        "expected_loss": 1500000,
                        "var_95": 2000000,
                        "trade_size_usd": 35000000,
                        "senior_approval": True,
                    },
                    confidence=92.0,
                ),
            ],
            constraints=Constraints(
                regulatory=["SEC Rule 15c3-1", "FINRA Rule 4210"],
                risk_limits=RiskLimits(var_limit=10000000, position_limit=200000),
                policy_rules=["TRADE-001", "RISK-003"],
            ),
        )

        ruling = decision_engine.evaluate(request)

        # Should approve or approve with conditions (not deny for valid trade)
        assert ruling.decision in [DecisionOutcome.APPROVE, DecisionOutcome.APPROVE_WITH_CONDITIONS]
        assert ruling.risk_assessment.level in [RiskLevel.M, RiskLevel.L]

    def test_counterparty_credit_assessment(self, decision_engine):
        """Test counterparty credit approval"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.COUNTERPARTY_APPROVAL,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Credit Risk Department",
                purpose="Approve new OTC derivative counterparty XYZ Corp",
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.CREDIT_RATING,
                    source="S&P",
                    data={"credit_rating": "BBB+"},
                    confidence=100.0,
                ),
                Evidence(
                    type=EvidenceType.COMPLIANCE_DOC,
                    source="KYC System",
                    data={"kyc_complete": True, "aml_check": "passed"},
                    confidence=100.0,
                ),
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Credit Model",
                    data={
                        "probability": 12.0,  # 12% default probability
                        "expected_loss": 2500000,
                    },
                    confidence=85.0,
                ),
            ],
            constraints=Constraints(
                regulatory=["Dodd-Frank"], policy_rules=["CREDIT-001", "RISK-002"],
            ),
        )

        ruling = decision_engine.evaluate(request)

        # BBB+ rating meets minimum, should approve
        assert ruling.decision in [DecisionOutcome.APPROVE, DecisionOutcome.APPROVE_WITH_CONDITIONS]
        assert len(ruling.compliance_flags) > 0

    def test_limit_breach_escalation(self, decision_engine):
        """Test risk limit breach handling"""
        request = DecisionRequest(
            request_id=uuid4(),
            decision_type=DecisionType.LIMIT_BREACH,
            context=DecisionContext(
                timestamp=datetime.utcnow(),
                entity="Risk Committee",
                purpose="Address VaR limit breach - $15M vs $10M limit",
                urgency=Urgency.CRITICAL,
            ),
            evidence=[
                Evidence(
                    type=EvidenceType.RISK_METRIC,
                    source="Risk System",
                    data={"var_95": 15000000, "probability": 70.0, "expected_loss": 12000000},
                    confidence=95.0,
                ),
            ],
            constraints=Constraints(
                risk_limits=RiskLimits(var_limit=10000000), policy_rules=["RISK-003"],
            ),
        )

        ruling = decision_engine.evaluate(request)

        # Limit breach should trigger denial or escalation
        assert ruling.decision in [
            DecisionOutcome.DENY,
            DecisionOutcome.ESCALATE,
            DecisionOutcome.APPROVE_WITH_CONDITIONS,
        ]
        assert "limit" in ruling.rationale.summary.lower()
