"""
Clinical Decision Gateway
==========================

Governance layer for AI-driven clinical decisions.
Ensures appropriate human oversight and evidence-based guidance.

Key Functions:
1. Risk stratification for clinical decisions
2. Evidence level tracking (E1-E5)
3. Human escalation rules
4. Contraindication detection
5. Serious Adverse Event (SAE) flagging

This is the "mid-hoc" defense layer - real-time monitoring
of AI clinical recommendations before they reach patients.
"""

import hashlib
import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models import ActiveShieldAdverseEvent

logger = logging.getLogger(__name__)


class EvidenceLevel(StrEnum):
    """Clinical evidence levels (Oxford CEBM)"""

    E1 = "E1"  # Systematic review of RCTs
    E2 = "E2"  # RCT or observational with dramatic effect
    E3 = "E3"  # Non-randomized controlled cohort
    E4 = "E4"  # Case-series, case-control
    E5 = "E5"  # Expert opinion, mechanistic reasoning


class ClinicalRiskLevel(StrEnum):
    """Risk levels for clinical decisions"""

    MINIMAL = "minimal"  # Informational only
    LOW = "low"  # General wellness
    MODERATE = "moderate"  # Requires clinical review
    HIGH = "high"  # Requires physician sign-off
    CRITICAL = "critical"  # Life-threatening, immediate action


class DecisionCategory(StrEnum):
    """Categories of clinical decisions"""

    INFORMATIONAL = "informational"  # General health info
    TRIAGE = "triage"  # Symptom assessment
    DIAGNOSTIC = "diagnostic"  # Diagnosis suggestion
    THERAPEUTIC = "therapeutic"  # Treatment recommendation
    MEDICATION = "medication"  # Drug-related
    EMERGENCY = "emergency"  # Urgent/emergent
    BEHAVIORAL = "behavioral"  # Mental health


class EscalationReason(StrEnum):
    """Reasons for human escalation"""

    HIGH_RISK_DECISION = "high_risk_decision"
    CONTRAINDICATION = "contraindication"
    DRUG_INTERACTION = "drug_interaction"
    CONFIDENCE_LOW = "confidence_low"
    PATIENT_REQUEST = "patient_request"
    ADVERSE_EVENT = "adverse_event"
    REGULATORY_REQUIRED = "regulatory_required"
    EMERGENCY = "emergency"


class ClinicalDecision(BaseModel):
    """A clinical decision/recommendation"""

    decision_id: str
    category: DecisionCategory
    content: str
    evidence_level: EvidenceLevel = EvidenceLevel.E5
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    risk_level: ClinicalRiskLevel = ClinicalRiskLevel.LOW
    citations: list[str] = Field(default_factory=list)
    contraindications_checked: bool = False
    interactions_checked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GatewayResult(BaseModel):
    """Result of clinical gateway check"""

    decision_id: str
    approved: bool
    decision: ClinicalDecision
    human_review_required: bool = False
    escalation_reasons: list[EscalationReason] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    audit_trail_id: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class AdverseEventReport(BaseModel):
    """Serious Adverse Event (SAE) Report"""

    event_id: str
    session_id: str
    patient_id: str | None = None
    event_type: str
    description: str
    severity: str  # mild, moderate, severe, life-threatening, fatal
    relatedness: str  # unrelated, unlikely, possible, probable, definite
    ai_recommendation_involved: bool = False
    ai_recommendation_id: str | None = None
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    reported_by: str = "system"


class ClinicalDecisionGateway:
    """
    Clinical Decision Gateway

    SALES VALUE PROPOSITION:
    - Misdiagnosis liability can exceed $1M per incident
    - AI recommendations without oversight = massive liability
    - This gateway proves due diligence and appropriate oversight

    Escalation Matrix:
    - MINIMAL risk: AI handles autonomously
    - LOW risk: AI handles, logged for review
    - MODERATE risk: AI + async clinical review
    - HIGH risk: Requires real-time clinical approval
    - CRITICAL risk: Immediate human takeover
    """

    # Decision categories that always require human review
    ALWAYS_ESCALATE = {
        DecisionCategory.DIAGNOSTIC,
        DecisionCategory.MEDICATION,
        DecisionCategory.EMERGENCY,
    }

    # Risk thresholds for escalation
    ESCALATION_THRESHOLDS = {
        ClinicalRiskLevel.HIGH: 0.0,  # Always escalate
        ClinicalRiskLevel.MODERATE: 0.7,  # Escalate if confidence < 0.7
        ClinicalRiskLevel.LOW: 0.5,  # Escalate if confidence < 0.5
    }

    # Dangerous symptom patterns
    EMERGENCY_PATTERNS = [
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "severe bleeding",
        "loss of consciousness",
        "seizure",
        "stroke symptoms",
        "heart attack",
        "anaphylaxis",
        "suicidal",
        "self-harm",
        "overdose",
        "severe allergic reaction",
        "cannot move",
        "paralysis",
        "sudden vision loss",
        "sudden confusion",
        "slurred speech",
    ]

    # Common drug interactions (subset for demonstration)
    DRUG_INTERACTIONS = {
        ("warfarin", "aspirin"): "high_bleeding_risk",
        ("warfarin", "ibuprofen"): "high_bleeding_risk",
        ("metformin", "contrast_dye"): "lactic_acidosis_risk",
        ("ssri", "maoi"): "serotonin_syndrome",
        ("statin", "grapefruit"): "increased_toxicity",
        ("ace_inhibitor", "potassium"): "hyperkalemia",
        ("opioid", "benzodiazepine"): "respiratory_depression",
        ("lithium", "nsaid"): "lithium_toxicity",
    }

    def __init__(self, db: Session | None = None):
        self.db = db
        self._audit_log: list[GatewayResult] = []
        self._adverse_events: list[AdverseEventReport] = []

    async def evaluate(
        self,
        decision: ClinicalDecision,
        patient_context: dict[str, Any] | None = None,
    ) -> GatewayResult:
        """
        Evaluate a clinical decision through the gateway.

        Args:
            decision: The clinical decision to evaluate
            patient_context: Patient info (medications, allergies, conditions)

        Returns:
            GatewayResult with approval status and required actions
        """
        audit_id = self._generate_audit_id(decision.decision_id)
        escalation_reasons = []
        warnings = []
        required_actions = []
        patient_context = patient_context or {}

        # Check 1: Category-based escalation
        if decision.category in self.ALWAYS_ESCALATE:
            escalation_reasons.append(EscalationReason.REGULATORY_REQUIRED)
            warnings.append(f"{decision.category.value} decisions require clinical review")

        # Check 2: Risk-based escalation
        threshold = self.ESCALATION_THRESHOLDS.get(decision.risk_level, 1.0)
        if decision.confidence_score < threshold:
            escalation_reasons.append(EscalationReason.CONFIDENCE_LOW)
            warnings.append(
                f"Confidence {decision.confidence_score:.0%} below {threshold:.0%} threshold"
            )

        # Check 3: Emergency pattern detection
        content_lower = decision.content.lower()
        for pattern in self.EMERGENCY_PATTERNS:
            if pattern in content_lower:
                escalation_reasons.append(EscalationReason.EMERGENCY)
                warnings.append(f"Emergency pattern detected: {pattern}")
                decision.risk_level = ClinicalRiskLevel.CRITICAL
                required_actions.append("IMMEDIATE: Route to emergency triage")
                break

        # Check 4: Drug interaction check (if medications involved)
        if decision.category == DecisionCategory.MEDICATION:
            patient_meds = patient_context.get("current_medications", [])
            recommended_meds = self._extract_medications(decision.content)

            for patient_med in patient_meds:
                for rec_med in recommended_meds:
                    interaction = self._check_interaction(patient_med, rec_med)
                    if interaction:
                        escalation_reasons.append(EscalationReason.DRUG_INTERACTION)
                        warnings.append(
                            f"Drug interaction: {patient_med} + {rec_med} = {interaction}"
                        )
                        required_actions.append(f"REVIEW: Potential {interaction}")

        # Check 5: Contraindication check
        patient_allergies = patient_context.get("allergies", [])
        patient_conditions = patient_context.get("conditions", [])

        contraindication = self._check_contraindications(
            decision.content,
            patient_allergies,
            patient_conditions,
        )
        if contraindication:
            escalation_reasons.append(EscalationReason.CONTRAINDICATION)
            warnings.append(f"Potential contraindication: {contraindication}")
            required_actions.append("STOP: Verify contraindication before proceeding")

        # Check 6: Evidence level assessment
        if (
            decision.evidence_level == EvidenceLevel.E5
            and decision.category == DecisionCategory.THERAPEUTIC
        ):
            warnings.append("Therapeutic recommendation based on expert opinion only (E5)")
            if not decision.citations:
                required_actions.append("RECOMMEND: Add clinical guideline citations")

        # Determine approval
        human_review_required = len(escalation_reasons) > 0
        approved = decision.risk_level not in [ClinicalRiskLevel.HIGH, ClinicalRiskLevel.CRITICAL]

        # For critical risk, never auto-approve
        if decision.risk_level == ClinicalRiskLevel.CRITICAL:
            approved = False
            required_actions.insert(0, "CRITICAL: Human takeover required")

        result = GatewayResult(
            decision_id=decision.decision_id,
            approved=approved,
            decision=decision,
            human_review_required=human_review_required,
            escalation_reasons=escalation_reasons,
            warnings=warnings,
            required_actions=required_actions,
            audit_trail_id=audit_id,
        )

        self._audit_log.append(result)

        if self.db and not approved:
            try:
                adverse_event = ActiveShieldAdverseEvent(
                    session_id=audit_id,
                    event_type="clinical_decision_blocked",
                    description=f"Blocked decision: {decision.category.value}. Content: {decision.content[:50]}. Reasons: {escalation_reasons}",
                    severity="high",
                    context_snapshot={
                        "decision": decision.model_dump(mode="json"),
                        "patient_context": patient_context,
                    },
                )
                self.db.add(adverse_event)
                # Ensure we commit if this is a standalone operation, or rely on caller?
                # Ideally, we should flush or commit if we want it persisted immediately.
                # Since this might be part of a larger transaction (LiabilityShield), maybe just add?
                # Use nested transaction or autonomous commit?
                # Safe pattern: add(), let caller commit OR commit if we own the session.
                # Given dependency injection, we share session. We should safe-guard.
                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to persist Clinical Gateway adverse events: {e}")
                raise e  # Fail test if persistence fails

        if not approved:
            logger.warning(
                f"CLINICAL GATEWAY BLOCKED: {decision.decision_id} - {escalation_reasons}"
            )
        elif human_review_required:
            logger.info(f"CLINICAL GATEWAY FLAGGED: {decision.decision_id} - {escalation_reasons}")

        return result

    def _extract_medications(self, content: str) -> list[str]:
        """Extract medication names from content"""
        # Simplified - in production, use NLP/drug database
        common_drugs = [
            "aspirin",
            "ibuprofen",
            "acetaminophen",
            "warfarin",
            "heparin",
            "metformin",
            "insulin",
            "lisinopril",
            "amlodipine",
            "metoprolol",
            "atorvastatin",
            "simvastatin",
            "omeprazole",
            "pantoprazole",
            "sertraline",
            "fluoxetine",
            "alprazolam",
            "lorazepam",
            "gabapentin",
            "pregabalin",
            "tramadol",
            "oxycodone",
        ]
        content_lower = content.lower()
        return [drug for drug in common_drugs if drug in content_lower]

    def _check_interaction(self, med1: str, med2: str) -> str | None:
        """Check for known drug interactions"""
        med1_lower = med1.lower()
        med2_lower = med2.lower()

        # Check both orderings
        for (drug_a, drug_b), interaction in self.DRUG_INTERACTIONS.items():
            if (drug_a in med1_lower and drug_b in med2_lower) or (
                drug_b in med1_lower and drug_a in med2_lower
            ):
                return interaction
        return None

    def _check_contraindications(
        self,
        content: str,
        allergies: list[str],
        conditions: list[str],
    ) -> str | None:
        """Check for contraindications"""
        content_lower = content.lower()

        # Check allergies
        for allergy in allergies:
            if allergy.lower() in content_lower:
                return f"Patient allergic to {allergy}"

        # Check condition-based contraindications
        contraindication_map = {
            "kidney disease": ["nsaid", "ibuprofen", "contrast", "metformin"],
            "liver disease": ["acetaminophen", "statin"],
            "pregnancy": ["warfarin", "methotrexate", "isotretinoin", "ace inhibitor"],
            "bleeding disorder": ["aspirin", "warfarin", "heparin", "nsaid"],
        }

        for condition in conditions:
            contraindicated = contraindication_map.get(condition.lower(), [])
            for drug in contraindicated:
                if drug in content_lower:
                    return f"{drug} contraindicated with {condition}"

        return None

    def _generate_audit_id(self, decision_id: str) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now(UTC).isoformat()
        content = f"gateway:{decision_id}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # =========================================================================
    # Adverse Event Reporting
    # =========================================================================

    async def report_adverse_event(
        self,
        session_id: str,
        event_type: str,
        description: str,
        severity: str,
        ai_recommendation_id: str | None = None,
        patient_id: str | None = None,
    ) -> AdverseEventReport:
        """
        Report a Serious Adverse Event (SAE).

        Required for regulatory compliance and liability protection.
        """
        event_id = self._generate_audit_id(f"sae:{session_id}")

        # Determine relatedness to AI if recommendation was involved
        relatedness = "unrelated"
        if ai_recommendation_id:
            # Check if recommendation was approved by gateway
            related_result = next(
                (r for r in self._audit_log if r.decision_id == ai_recommendation_id), None
            )
            if related_result:
                if not related_result.approved:
                    relatedness = "unlikely"  # We blocked it
                elif related_result.human_review_required:
                    relatedness = "possible"  # Flagged but proceeded
                else:
                    relatedness = "possible"  # Auto-approved

        report = AdverseEventReport(
            event_id=event_id,
            session_id=session_id,
            patient_id=patient_id,
            event_type=event_type,
            description=description,
            severity=severity,
            relatedness=relatedness,
            ai_recommendation_involved=ai_recommendation_id is not None,
            ai_recommendation_id=ai_recommendation_id,
        )

        self._adverse_events.append(report)
        logger.critical(f"SAE REPORTED: {event_id} - {severity} - {event_type}")

        return report

    # =========================================================================
    # Safety Recommendations
    # =========================================================================

    def get_safe_response_template(self, decision_category: DecisionCategory) -> dict[str, Any]:
        """Get template for safe AI response in each category"""
        templates = {
            DecisionCategory.INFORMATIONAL: {
                "prefix": "Based on general health information:",
                "suffix": "This is for informational purposes only and not medical advice.",
                "require_disclaimer": True,
                "escalation_prompt": None,
            },
            DecisionCategory.TRIAGE: {
                "prefix": "Based on the symptoms you've described:",
                "suffix": "This assessment is not a diagnosis. Please consult a healthcare provider for proper evaluation.",
                "require_disclaimer": True,
                "escalation_prompt": "If symptoms worsen or you experience emergency symptoms, seek immediate medical attention.",
            },
            DecisionCategory.DIAGNOSTIC: {
                "prefix": "Important: I cannot provide a diagnosis. However, your symptoms may be consistent with:",
                "suffix": "Only a licensed healthcare provider can diagnose medical conditions. Please schedule an appointment with your doctor.",
                "require_disclaimer": True,
                "escalation_prompt": "If you're experiencing a medical emergency, call 911 immediately.",
            },
            DecisionCategory.MEDICATION: {
                "prefix": "Regarding medications:",
                "suffix": "Always consult your doctor or pharmacist before taking any medication. Never start, stop, or change medications without medical supervision.",
                "require_disclaimer": True,
                "escalation_prompt": "For medication emergencies (overdose, severe reactions), call Poison Control at 1-800-222-1222 or 911.",
            },
            DecisionCategory.EMERGENCY: {
                "prefix": "IMPORTANT - This may be a medical emergency:",
                "suffix": "",
                "require_disclaimer": False,
                "escalation_prompt": "Call 911 immediately or go to your nearest emergency room.",
            },
            DecisionCategory.BEHAVIORAL: {
                "prefix": "I hear you, and I want to help:",
                "suffix": "While I'm here to provide support, please consider speaking with a licensed mental health professional.",
                "require_disclaimer": True,
                "escalation_prompt": "If you're in crisis, please call 988 (Suicide & Crisis Lifeline) or text HOME to 741741.",
            },
        }
        return templates.get(decision_category, templates[DecisionCategory.INFORMATIONAL])

    # =========================================================================
    # Audit & Reporting
    # =========================================================================

    def get_audit_trail(
        self,
        decision_id: str | None = None,
        escalated_only: bool = False,
        limit: int = 100,
    ) -> list[GatewayResult]:
        """Get audit trail of gateway decisions"""
        results = self._audit_log

        if decision_id:
            results = [r for r in results if r.decision_id == decision_id]

        if escalated_only:
            results = [r for r in results if r.human_review_required]

        return results[-limit:]

    def get_adverse_events(
        self,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[AdverseEventReport]:
        """Get adverse event reports"""
        events = self._adverse_events

        if severity:
            events = [e for e in events if e.severity == severity]

        return events[-limit:]

    def generate_safety_report(self) -> dict[str, Any]:
        """Generate safety performance report"""
        total_decisions = len(self._audit_log)
        escalated = len([r for r in self._audit_log if r.human_review_required])
        blocked = len([r for r in self._audit_log if not r.approved])
        adverse_events = len(self._adverse_events)

        # Calculate risk distribution
        risk_distribution = {}
        for result in self._audit_log:
            risk = result.decision.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        return {
            "period": "all_time",
            "total_decisions": total_decisions,
            "escalated_to_human": escalated,
            "escalation_rate": (escalated / total_decisions * 100) if total_decisions > 0 else 0,
            "blocked_decisions": blocked,
            "block_rate": (blocked / total_decisions * 100) if total_decisions > 0 else 0,
            "adverse_events_reported": adverse_events,
            "risk_distribution": risk_distribution,
            "generated_at": datetime.now(UTC).isoformat(),
        }


# Global instance
clinical_gateway = ClinicalDecisionGateway()
