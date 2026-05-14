# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Unit tests for all Judge verticals
Tests FinJudge, CaseJudge, LawJudge, FraudJudge
"""

import pytest
from src.judges import (
    JudgeFactory,
    JudgeRequest,
    JudgeType,
    JudgeDecision,
    FinJudge,
    CaseJudge,
    LawJudge,
    FraudJudge,
)
from src.risk_matrix import RiskLevel


class TestFinJudge:
    """Test FinJudge financial transaction enforcement"""

    def test_high_value_wire_new_vendor_no_po_blocks(self):
        """Test that $75K wire to new vendor without PO is BLOCKED"""
        judge = FinJudge()
        request = JudgeRequest(
            request_id="test_fin_001",
            judge_type=JudgeType.FIN,
            action_type="wire_transfer",
            context={"amount_usd": 75000, "vendor_status": "new", "purchase_order": None, "destination_country": "Unknown"},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert response.risk_assessment.risk_level in [RiskLevel.H, RiskLevel.EH]
        assert response.approval_gate.value == "cfo"
        assert "new" in response.reasoning.lower() or "vendor" in response.reasoning.lower()

    def test_approved_vendor_with_po_allows(self):
        """Test that approved vendor with PO under $50K is ALLOWED"""
        judge = FinJudge()
        request = JudgeRequest(
            request_id="test_fin_002",
            judge_type=JudgeType.FIN,
            action_type="wire_transfer",
            context={"amount_usd": 25000, "vendor_status": "approved", "purchase_order": "PO-123456", "destination_country": "US"},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.ALLOW
        assert response.approval_gate.value == "auto" or response.approval_gate.value == "finance_director"

    def test_high_risk_destination_blocks(self):
        """Test that high-risk destination country with amount >$10K blocks"""
        judge = FinJudge()
        request = JudgeRequest(
            request_id="test_fin_003",
            judge_type=JudgeType.FIN,
            action_type="wire_transfer",
            context={"amount_usd": 15000, "vendor_status": "approved", "purchase_order": "PO-123", "destination_country": "Unknown"},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "destination" in response.reasoning.lower() or "country" in response.reasoning.lower()

    def test_creates_audit_trail(self):
        """Test that audit trail is created"""
        judge = FinJudge()
        request = JudgeRequest(
            request_id="test_fin_004",
            judge_type=JudgeType.FIN,
            action_type="wire_transfer",
            context={"amount_usd": 50000, "vendor_status": "new", "purchase_order": None},
            requested_by="test@example.com",
        )

        response = judge.judge(request)
        audit_trail = judge.create_audit_trail(response, request)

        assert audit_trail.request_id == request.request_id
        assert audit_trail.judge_type == JudgeType.FIN
        assert audit_trail.decision == response.decision
        assert len(audit_trail.semantic_summary) > 0


class TestCaseJudge:
    """Test CaseJudge legal case assessment"""

    def test_case_acceptance_without_conflict_check_blocks(self):
        """Test that case acceptance without conflict check is BLOCKED"""
        judge = CaseJudge()
        request = JudgeRequest(
            request_id="test_case_001",
            judge_type=JudgeType.CASE,
            action_type="case_acceptance",
            context={"case_value_usd": 500000, "case_type": "contract_dispute", "conflict_check_passed": False, "probability_of_success": 0.6},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "conflict" in response.reasoning.lower()

    def test_case_acceptance_with_conflict_check_allows(self):
        """Test that case acceptance with conflict check passed is ALLOWED"""
        judge = CaseJudge()
        request = JudgeRequest(
            request_id="test_case_002",
            judge_type=JudgeType.CASE,
            action_type="case_acceptance",
            context={"case_value_usd": 500000, "case_type": "contract_dispute", "conflict_check_passed": True, "probability_of_success": 0.6},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.ALLOW

    def test_low_value_case_blocks(self):
        """Test that case value <$10K is BLOCKED"""
        judge = CaseJudge()
        request = JudgeRequest(
            request_id="test_case_003",
            judge_type=JudgeType.CASE,
            action_type="case_acceptance",
            context={"case_value_usd": 5000, "case_type": "small_claims", "conflict_check_passed": True, "probability_of_success": 0.8},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "value" in response.reasoning.lower() or "threshold" in response.reasoning.lower()

    def test_low_success_probability_blocks(self):
        """Test that low probability of success (<30%) is BLOCKED"""
        judge = CaseJudge()
        request = JudgeRequest(
            request_id="test_case_004",
            judge_type=JudgeType.CASE,
            action_type="litigation_strategy",
            context={"case_value_usd": 500000, "case_type": "litigation", "probability_of_success": 0.25},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "probability" in response.reasoning.lower() or "success" in response.reasoning.lower()


class TestLawJudge:
    """Test LawJudge legal compliance validation"""

    def test_high_risk_ai_without_legal_review_blocks(self):
        """Test that high-risk AI system without legal review is BLOCKED"""
        judge = LawJudge()
        request = JudgeRequest(
            request_id="test_law_001",
            judge_type=JudgeType.LAW,
            action_type="compliance_check",
            context={"compliance_area": "eu_ai_act", "ai_system_type": "biometric_identification", "legal_review_completed": False},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "high-risk" in response.reasoning.lower() or "legal review" in response.reasoning.lower()
        assert response.risk_assessment.severity.value == "I"  # Catastrophic

    def test_high_risk_ai_with_legal_review_allows(self):
        """Test that high-risk AI system with legal review is ALLOWED"""
        judge = LawJudge()
        request = JudgeRequest(
            request_id="test_law_002",
            judge_type=JudgeType.LAW,
            action_type="compliance_check",
            context={"compliance_area": "eu_ai_act", "ai_system_type": "biometric_identification", "legal_review_completed": True},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.ALLOW

    def test_gdpr_without_dpia_blocks(self):
        """Test that GDPR processing without DPIA is BLOCKED"""
        judge = LawJudge()
        request = JudgeRequest(
            request_id="test_law_003",
            judge_type=JudgeType.LAW,
            action_type="data_processing",
            context={"compliance_area": "gdpr", "processes_personal_data": True, "dpia_completed": False},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "dpia" in response.reasoning.lower() or "gdpr" in response.reasoning.lower()

    def test_export_control_restricted_country_blocks(self):
        """Test that export to restricted country without license is BLOCKED"""
        judge = LawJudge()
        request = JudgeRequest(
            request_id="test_law_004",
            judge_type=JudgeType.LAW,
            action_type="export_approval",
            context={"compliance_area": "export_control", "destination_country": "CN", "export_license": False},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert response.risk_assessment.severity.value == "I"  # Catastrophic (criminal penalties)


class TestFraudJudge:
    """Test FraudJudge fraud detection & risk scoring"""

    def test_high_fraud_score_blocks(self):
        """Test that fraud score ≥0.7 is BLOCKED"""
        judge = FraudJudge()
        request = JudgeRequest(
            request_id="test_fraud_001",
            judge_type=JudgeType.FRAUD,
            action_type="payment_authorization",
            context={"fraud_score": 0.85, "identity_verified": False, "amount_usd": 5000},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "fraud" in response.reasoning.lower()

    def test_unverified_identity_over_1k_blocks(self):
        """Test that unverified identity with amount >$1K is BLOCKED"""
        judge = FraudJudge()
        request = JudgeRequest(
            request_id="test_fraud_002",
            judge_type=JudgeType.FRAUD,
            action_type="payment_authorization",
            context={"fraud_score": 0.3, "identity_verified": False, "amount_usd": 2000},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "identity" in response.reasoning.lower()

    def test_multiple_fraud_indicators_blocks(self):
        """Test that ≥3 fraud indicators is BLOCKED"""
        judge = FraudJudge()
        request = JudgeRequest(
            request_id="test_fraud_003",
            judge_type=JudgeType.FRAUD,
            action_type="payment_authorization",
            context={
                "fraud_score": 0.5,
                "identity_verified": False,
                "geo_location_mismatch": True,
                "velocity_check_failed": True,
                "device_fingerprint_match": False,
                "amount_usd": 3000,
            },
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.BLOCK
        assert "indicator" in response.reasoning.lower() or "multiple" in response.reasoning.lower()

    def test_low_fraud_score_verified_identity_allows(self):
        """Test that low fraud score with verified identity is ALLOWED"""
        judge = FraudJudge()
        request = JudgeRequest(
            request_id="test_fraud_004",
            judge_type=JudgeType.FRAUD,
            action_type="payment_authorization",
            context={"fraud_score": 0.2, "identity_verified": True, "geo_location_mismatch": False, "amount_usd": 500},
            requested_by="test@example.com",
        )

        response = judge.judge(request)

        assert response.decision == JudgeDecision.ALLOW


class TestJudgeFactory:
    """Test JudgeFactory singleton pattern"""

    def test_factory_returns_correct_judge_type(self):
        """Test that factory returns correct judge instances"""
        fin_judge = JudgeFactory.get_judge(JudgeType.FIN)
        assert isinstance(fin_judge, FinJudge)

        case_judge = JudgeFactory.get_judge(JudgeType.CASE)
        assert isinstance(case_judge, CaseJudge)

        law_judge = JudgeFactory.get_judge(JudgeType.LAW)
        assert isinstance(law_judge, LawJudge)

        fraud_judge = JudgeFactory.get_judge(JudgeType.FRAUD)
        assert isinstance(fraud_judge, FraudJudge)

    def test_factory_returns_singleton(self):
        """Test that factory returns same instance (singleton)"""
        judge1 = JudgeFactory.get_judge(JudgeType.FIN)
        judge2 = JudgeFactory.get_judge(JudgeType.FIN)

        assert judge1 is judge2

    def test_factory_reset(self):
        """Test that factory reset creates new instances"""
        judge1 = JudgeFactory.get_judge(JudgeType.FIN)

        JudgeFactory.reset()

        judge2 = JudgeFactory.get_judge(JudgeType.FIN)

        assert judge1 is not judge2


class TestCrossJudgeConsistency:
    """Test consistency across all judge verticals"""

    def test_all_judges_produce_semantic_trails(self):
        """Test that all judges produce valid semantic trails"""
        test_requests = [
            (JudgeType.FIN, {"amount_usd": 50000, "vendor_status": "new", "purchase_order": None}),
            (JudgeType.CASE, {"case_value_usd": 100000, "conflict_check_passed": True, "probability_of_success": 0.6}),
            (JudgeType.LAW, {"compliance_area": "eu_ai_act", "ai_system_type": "biometric_identification", "legal_review_completed": False}),
            (JudgeType.FRAUD, {"fraud_score": 0.8, "identity_verified": False, "amount_usd": 5000}),
        ]

        for judge_type, context in test_requests:
            judge = JudgeFactory.get_judge(judge_type)
            request = JudgeRequest(
                request_id=f"test_{judge_type.value}_001",
                judge_type=judge_type,
                action_type="test_action",
                context=context,
                requested_by="test@example.com",
            )

            response = judge.judge(request)

            assert len(response.semantic_trail) > 0
            assert "→" in response.semantic_trail
            assert response.semantic_trail.endswith(("ALLOW", "BLOCK"))

    def test_all_judges_track_latency(self):
        """Test that all judges track latency"""
        for judge_type in JudgeType:
            judge = JudgeFactory.get_judge(judge_type)
            request = JudgeRequest(
                request_id=f"test_{judge_type.value}_latency",
                judge_type=judge_type,
                action_type="test_action",
                context={"amount_usd": 1000},
                requested_by="test@example.com",
            )

            response = judge.judge(request)

            assert response.latency_ms > 0
            assert response.latency_ms < 1000  # Should be well under 1 second

    def test_all_judges_have_next_steps(self):
        """Test that all judges provide next steps"""
        for judge_type in JudgeType:
            judge = JudgeFactory.get_judge(judge_type)
            request = JudgeRequest(
                request_id=f"test_{judge_type.value}_steps",
                judge_type=judge_type,
                action_type="test_action",
                context={"amount_usd": 1000},
                requested_by="test@example.com",
            )

            response = judge.judge(request)

            assert len(response.next_steps) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
