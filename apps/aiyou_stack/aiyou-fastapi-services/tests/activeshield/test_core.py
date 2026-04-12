"""
ActiveShield Medical - Unit Tests
==================================

Test coverage for:
- SB243ComplianceEngine
- MedicalDLPEngine
- ClinicalDecisionGateway
- LiabilityShield
"""

import pytest

from activeshield_medical.core.clinical_gateway import (
    ClinicalDecision,
    ClinicalDecisionGateway,
    ClinicalRiskLevel,
    DecisionCategory,
    EscalationReason,
    EvidenceLevel,
)
from activeshield_medical.core.liability_shield import (
    LiabilityShield,
    ShieldAction,
    ShieldPhase,
)
from activeshield_medical.core.medical_dlp import (
    ClinicalDataType,
    MedicalDLPEngine,
    PHIType,
    SensitivityLevel,
)

# Core components
from activeshield_medical.core.sb243_compliance import (
    CrisisLevel,
    SB243ComplianceEngine,
    SeverityLevel,
    ViolationType,
)

# =============================================================================
# SB243 Compliance Engine Tests
# =============================================================================


class TestSB243ComplianceEngine:
    """Test SB 243 Compliance Engine"""

    @pytest.fixture
    def engine(self):
        return SB243ComplianceEngine()

    @pytest.mark.asyncio
    async def test_crisis_detection_self_harm(self, engine):
        """Detect self-harm patterns and escalate appropriately"""
        result = await engine.check(
            session_id="test-001",
            content="I want to hurt myself",
            context={"user_id": "patient-123"},
            is_ai_response=False,
        )

        assert result.has_violations
        assert CrisisLevel.IMMEDIATE in [
            v.crisis_level for v in result.violations if hasattr(v, "crisis_level")
        ]

    @pytest.mark.asyncio
    async def test_crisis_detection_suicide_ideation(self, engine):
        """Detect suicide ideation with 988 escalation"""
        result = await engine.check(
            session_id="test-002",
            content="I don't want to live anymore",
            context={},
            is_ai_response=False,
        )

        assert result.has_violations
        # Should trigger crisis response

    @pytest.mark.asyncio
    async def test_minor_protection_age_indicator(self, engine):
        """Detect minor status from age indicators"""
        result = await engine.check(
            session_id="test-003",
            content="I'm 15 years old and need help",
            context={},
            is_ai_response=False,
        )

        # Should flag potential minor
        assert result.minor_detected or any(
            v.violation_type == ViolationType.MINOR_PROTECTION for v in result.violations
        )

    @pytest.mark.asyncio
    async def test_ai_disclosure_violation(self, engine):
        """Flag AI responses that don't include disclosure"""
        result = await engine.check(
            session_id="test-004",
            content="You should take this medication daily.",
            context={"ai_disclosed": False},
            is_ai_response=True,
        )

        # Should flag missing AI disclosure
        has_disclosure_violation = any(
            v.violation_type == ViolationType.AI_DISCLOSURE for v in result.violations
        )
        assert has_disclosure_violation or result.ai_disclosure_required

    @pytest.mark.asyncio
    async def test_deception_detection(self, engine):
        """Detect AI persona deception attempts"""
        result = await engine.check(
            session_id="test-005",
            content="I am a real doctor and I'm telling you this is safe",
            context={},
            is_ai_response=True,
        )

        # Should flag deception
        has_deception = any(
            v.violation_type == ViolationType.AI_DECEPTION for v in result.violations
        )
        assert has_deception

    @pytest.mark.asyncio
    async def test_clean_content_passes(self, engine):
        """Normal health content should pass without violations"""
        result = await engine.check(
            session_id="test-006",
            content="What are the symptoms of the common cold?",
            context={"ai_disclosed": True},
            is_ai_response=False,
        )

        assert not result.has_violations or result.severity == SeverityLevel.INFO


# =============================================================================
# Medical DLP Engine Tests
# =============================================================================


class TestMedicalDLPEngine:
    """Test Medical DLP (PHI Detection) Engine"""

    @pytest.fixture
    def engine(self):
        return MedicalDLPEngine()

    @pytest.mark.asyncio
    async def test_ssn_detection(self, engine):
        """Detect and redact SSN"""
        result = await engine.scan(
            "Patient SSN is 123-45-6789",
            redact=True,
        )

        assert result.total_phi_count >= 1
        assert any(p.phi_type == PHIType.SSN for p in result.phi_detected)
        assert "123-45-6789" not in result.redacted_text
        assert "SSN_REDACTED" in result.redacted_text

    @pytest.mark.asyncio
    async def test_mrn_detection(self, engine):
        """Detect Medical Record Numbers"""
        result = await engine.scan(
            "MRN: AB12345678",
            redact=True,
        )

        assert result.total_phi_count >= 1
        assert any(p.phi_type == PHIType.MRN for p in result.phi_detected)

    @pytest.mark.asyncio
    async def test_phone_detection(self, engine):
        """Detect phone numbers"""
        result = await engine.scan(
            "Call me at 555-123-4567",
            redact=True,
        )

        assert any(p.phi_type == PHIType.PHONE for p in result.phi_detected)
        assert "555-123-4567" not in result.redacted_text

    @pytest.mark.asyncio
    async def test_email_detection(self, engine):
        """Detect email addresses"""
        result = await engine.scan(
            "Contact: redacted@shadowtag-v4.local",
            redact=True,
        )

        assert any(p.phi_type == PHIType.EMAIL for p in result.phi_detected)
        assert "redacted@shadowtag-v4.local" not in result.redacted_text

    @pytest.mark.asyncio
    async def test_date_detection(self, engine):
        """Detect date of birth / dates"""
        result = await engine.scan(
            "DOB: 01/15/1985",
            redact=True,
        )

        assert any(p.phi_type == PHIType.DATES for p in result.phi_detected)

    @pytest.mark.asyncio
    async def test_clinical_medication_detection(self, engine):
        """Detect medication mentions"""
        result = await engine.scan(
            "Patient takes metformin 500mg twice daily",
            redact=False,
        )

        assert result.total_clinical_count >= 1
        assert any(c.data_type == ClinicalDataType.MEDICATION for c in result.clinical_detected)

    @pytest.mark.asyncio
    async def test_mental_health_high_sensitivity(self, engine):
        """Mental health data should be marked highly restricted"""
        result = await engine.scan(
            "Patient diagnosed with depression and anxiety",
            redact=True,
        )

        assert any(c.data_type == ClinicalDataType.MENTAL_HEALTH for c in result.clinical_detected)
        assert result.highest_sensitivity in [
            SensitivityLevel.RESTRICTED,
            SensitivityLevel.HIGHLY_RESTRICTED,
        ]

    @pytest.mark.asyncio
    async def test_genetic_data_highest_sensitivity(self, engine):
        """Genetic data should trigger highest sensitivity"""
        result = await engine.scan(
            "BRCA1 mutation positive",
            redact=True,
        )

        assert any(c.data_type == ClinicalDataType.GENETIC for c in result.clinical_detected)
        assert result.highest_sensitivity == SensitivityLevel.HIGHLY_RESTRICTED

    @pytest.mark.asyncio
    async def test_clean_text_no_phi(self, engine):
        """Clean text should return no PHI"""
        result = await engine.scan(
            "The weather is nice today.",
            redact=True,
        )

        assert result.total_phi_count == 0
        assert result.redacted_text == "The weather is nice today."


# =============================================================================
# Clinical Decision Gateway Tests
# =============================================================================


class TestClinicalDecisionGateway:
    """Test Clinical Decision Gateway"""

    @pytest.fixture
    def gateway(self):
        return ClinicalDecisionGateway()

    @pytest.mark.asyncio
    async def test_informational_decision_approved(self, gateway):
        """Informational decisions should be auto-approved"""
        decision = ClinicalDecision(
            decision_id="dec-001",
            category=DecisionCategory.INFORMATIONAL,
            content="General information about vitamins",
            evidence_level=EvidenceLevel.E3,
            confidence_score=0.9,
            risk_level=ClinicalRiskLevel.MINIMAL,
        )

        result = await gateway.evaluate(decision)

        assert result.approved
        assert not result.human_review_required

    @pytest.mark.asyncio
    async def test_medication_requires_review(self, gateway):
        """Medication decisions should require human review"""
        decision = ClinicalDecision(
            decision_id="dec-002",
            category=DecisionCategory.MEDICATION,
            content="Consider starting metformin 500mg",
            evidence_level=EvidenceLevel.E2,
            confidence_score=0.8,
            risk_level=ClinicalRiskLevel.MODERATE,
        )

        result = await gateway.evaluate(decision)

        assert result.human_review_required
        assert EscalationReason.REGULATORY_REQUIRED in result.escalation_reasons

    @pytest.mark.asyncio
    async def test_emergency_pattern_escalation(self, gateway):
        """Emergency patterns should trigger immediate escalation"""
        decision = ClinicalDecision(
            decision_id="dec-003",
            category=DecisionCategory.TRIAGE,
            content="Patient reports severe chest pain",
            evidence_level=EvidenceLevel.E5,
            confidence_score=0.7,
            risk_level=ClinicalRiskLevel.MODERATE,
        )

        result = await gateway.evaluate(decision)

        assert result.human_review_required
        assert EscalationReason.EMERGENCY in result.escalation_reasons
        assert result.decision.risk_level == ClinicalRiskLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_drug_interaction_detection(self, gateway):
        """Detect drug interactions"""
        decision = ClinicalDecision(
            decision_id="dec-004",
            category=DecisionCategory.MEDICATION,
            content="Consider adding aspirin 81mg daily",
            evidence_level=EvidenceLevel.E2,
            confidence_score=0.85,
            risk_level=ClinicalRiskLevel.MODERATE,
        )

        patient_context = {
            "current_medications": ["warfarin", "lisinopril"],
        }

        result = await gateway.evaluate(decision, patient_context)

        assert EscalationReason.DRUG_INTERACTION in result.escalation_reasons
        assert any("warfarin" in w.lower() and "aspirin" in w.lower() for w in result.warnings)

    @pytest.mark.asyncio
    async def test_allergy_contraindication(self, gateway):
        """Detect allergy contraindications"""
        decision = ClinicalDecision(
            decision_id="dec-005",
            category=DecisionCategory.MEDICATION,
            content="Prescribe penicillin for infection",
            evidence_level=EvidenceLevel.E2,
            confidence_score=0.9,
            risk_level=ClinicalRiskLevel.LOW,
        )

        patient_context = {
            "allergies": ["penicillin"],
        }

        result = await gateway.evaluate(decision, patient_context)

        assert EscalationReason.CONTRAINDICATION in result.escalation_reasons
        assert any("allergic" in w.lower() or "penicillin" in w.lower() for w in result.warnings)

    @pytest.mark.asyncio
    async def test_low_confidence_escalation(self, gateway):
        """Low confidence decisions should escalate"""
        decision = ClinicalDecision(
            decision_id="dec-006",
            category=DecisionCategory.THERAPEUTIC,
            content="Might consider physical therapy",
            evidence_level=EvidenceLevel.E4,
            confidence_score=0.3,  # Very low
            risk_level=ClinicalRiskLevel.LOW,
        )

        result = await gateway.evaluate(decision)

        assert result.human_review_required
        assert EscalationReason.CONFIDENCE_LOW in result.escalation_reasons

    @pytest.mark.asyncio
    async def test_critical_risk_never_approved(self, gateway):
        """Critical risk decisions should never auto-approve"""
        decision = ClinicalDecision(
            decision_id="dec-007",
            category=DecisionCategory.EMERGENCY,
            content="Patient experiencing anaphylaxis",
            evidence_level=EvidenceLevel.E1,
            confidence_score=0.99,
            risk_level=ClinicalRiskLevel.CRITICAL,
        )

        result = await gateway.evaluate(decision)

        assert not result.approved
        assert "Human takeover required" in str(result.required_actions)


# =============================================================================
# Liability Shield (Orchestrator) Tests
# =============================================================================


class TestLiabilityShield:
    """Test Liability Shield Orchestrator"""

    @pytest.fixture
    def shield(self):
        return LiabilityShield()

    @pytest.mark.asyncio
    async def test_pre_check_clean_input(self, shield):
        """Pre-check should pass for clean input"""
        result = await shield.pre_check(
            session_id="shield-001",
            user_input="What are symptoms of a cold?",
            context={"ai_disclosed": True},
        )

        assert result.phase == ShieldPhase.PRE_HOC
        assert result.action in [ShieldAction.ALLOW, ShieldAction.FLAG]

    @pytest.mark.asyncio
    async def test_pre_check_crisis_blocked(self, shield):
        """Pre-check should block crisis content"""
        result = await shield.pre_check(
            session_id="shield-002",
            user_input="I want to end it all",
            context={},
        )

        assert result.phase == ShieldPhase.PRE_HOC
        assert result.action in [ShieldAction.BLOCK, ShieldAction.ESCALATE]

    @pytest.mark.asyncio
    async def test_mid_check_safe_response(self, shield):
        """Mid-check should pass safe AI responses"""
        result = await shield.mid_check(
            session_id="shield-003",
            ai_response="Cold symptoms include runny nose and coughing.",
            decision_category=DecisionCategory.INFORMATIONAL,
            confidence=0.9,
        )

        assert result.phase == ShieldPhase.MID_HOC
        assert result.action == ShieldAction.ALLOW

    @pytest.mark.asyncio
    async def test_mid_check_phi_redaction(self, shield):
        """Mid-check should redact PHI in AI responses"""
        result = await shield.mid_check(
            session_id="shield-004",
            ai_response="Patient John Smith, SSN 123-45-6789, should take aspirin.",
            decision_category=DecisionCategory.INFORMATIONAL,
            confidence=0.8,
        )

        assert result.phase == ShieldPhase.MID_HOC
        # PHI should be flagged or redacted
        assert result.phi_detected or "SSN_REDACTED" in str(result.modifications)

    @pytest.mark.asyncio
    async def test_post_log_audit_trail(self, shield):
        """Post-log should create audit trail"""
        result = await shield.post_log(
            session_id="shield-005",
            conversation_summary="Patient asked about cold symptoms, AI provided general info.",
            outcome="completed",
            metadata={"duration_seconds": 120},
        )

        assert result.phase == ShieldPhase.POST_HOC
        assert result.audit_id is not None
        assert result.action == ShieldAction.LOG

    @pytest.mark.asyncio
    async def test_full_shield_flow(self, shield):
        """Test complete pre/mid/post flow"""
        session_id = "shield-flow-001"

        # Pre-check
        pre = await shield.pre_check(
            session_id=session_id,
            user_input="What is diabetes?",
            context={"ai_disclosed": True},
        )
        assert pre.action == ShieldAction.ALLOW

        # Mid-check
        mid = await shield.mid_check(
            session_id=session_id,
            ai_response="Diabetes is a condition affecting blood sugar levels.",
            decision_category=DecisionCategory.INFORMATIONAL,
            confidence=0.95,
        )
        assert mid.action == ShieldAction.ALLOW

        # Post-log
        post = await shield.post_log(
            session_id=session_id,
            conversation_summary="Diabetes information provided",
            outcome="completed",
        )
        assert post.action == ShieldAction.LOG


# =============================================================================
# Integration Helpers
# =============================================================================


class TestAuditTrailIntegrity:
    """Test audit trail functionality"""

    @pytest.mark.asyncio
    async def test_audit_ids_unique(self):
        """Each scan should generate unique audit ID"""
        engine = MedicalDLPEngine()

        result1 = await engine.scan("Test content 1")
        result2 = await engine.scan("Test content 2")

        assert result1.audit_id != result2.audit_id

    @pytest.mark.asyncio
    async def test_audit_trail_retrievable(self):
        """Audit trail should be retrievable"""
        engine = MedicalDLPEngine()

        await engine.scan("Patient SSN 123-45-6789")
        await engine.scan("Normal text")

        trail = engine.get_audit_trail(limit=10)

        assert len(trail) >= 2
        assert any(r.total_phi_count > 0 for r in trail)
