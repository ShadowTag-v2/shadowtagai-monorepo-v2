# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
SB 243 Compliance Engine - California AI Transparency Law
==========================================================

Senate Bill 243 (California) Key Requirements:
1. Transparency: Users must know they're interacting with AI
2. Minor Protection: Enhanced safeguards for users under 18
3. Self-Harm Prevention: Crisis detection and escalation protocols
4. Private Right of Action: Affected parties can sue for violations

This is the PRIMARY compliance wedge for ActiveShieldMedical sales.
Health tech companies face significant liability without this layer.

References:
- SB 243 Text: https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB243
- Effective: January 2025
"""

import hashlib
import logging
import re
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models import ActiveShieldAdverseEvent

logger = logging.getLogger(__name__)


class SB243ViolationType(str, Enum):
    """Types of SB 243 violations"""

    MISSING_AI_DISCLOSURE = "missing_ai_disclosure"
    INADEQUATE_MINOR_PROTECTION = "inadequate_minor_protection"
    SELF_HARM_DETECTION_FAILURE = "self_harm_detection_failure"
    CRISIS_ESCALATION_FAILURE = "crisis_escalation_failure"
    DECEPTIVE_PERSONA = "deceptive_persona"
    MISSING_CONSENT = "missing_consent"
    DATA_RETENTION_VIOLATION = "data_retention_violation"


class SB243Severity(str, Enum):
    """Violation severity levels"""

    CRITICAL = "critical"  # Immediate legal exposure
    HIGH = "high"  # Significant liability risk
    MEDIUM = "medium"  # Compliance gap
    LOW = "low"  # Best practice issue


class CrisisLevel(str, Enum):
    """Crisis detection levels"""

    NONE = "none"
    MILD = "mild"  # General distress
    MODERATE = "moderate"  # Concerning indicators
    SEVERE = "severe"  # Immediate intervention needed
    CRITICAL = "critical"  # Life-threatening - escalate NOW


class SB243Violation(BaseModel):
    """A specific SB 243 violation"""

    violation_id: str
    violation_type: SB243ViolationType
    severity: SB243Severity
    description: str
    legal_reference: str
    remediation: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class SB243CheckResult(BaseModel):
    """Result of SB 243 compliance check"""

    passed: bool
    session_id: str
    user_type: str  # minor, adult, unknown
    ai_disclosure_present: bool
    consent_verified: bool
    crisis_level: CrisisLevel
    violations: list[SB243Violation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    escalation_reason: str | None = None
    audit_trail_id: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class SB243ComplianceEngine:
    """
    SB 243 Compliance Engine for Digital Health AI

    SALES VALUE PROPOSITION:
    - Private right of action means users can SUE for violations
    - Health chatbots face wrongful death exposure for self-harm failures
    - $500K+ liability per incident without proper compliance layer

    Key Checks:
    1. AI Disclosure - User knows they're talking to AI
    2. Minor Protection - Age verification + parental consent
    3. Crisis Detection - Self-harm/suicide ideation scanning
    4. Consent Trail - Documented user agreement
    5. Audit Archive - Immutable evidence for litigation defense
    """

    # Crisis detection patterns (self-harm, suicide ideation)
    CRISIS_PATTERNS = {
        CrisisLevel.CRITICAL: [
            r"(i('m| am) going to|i('ll| will)) (kill|end|hurt) (myself|my life)",
            r"(suicide|suicidal|end (it all|my life))",
            r"(don'?t want to|can'?t) (live|go on|continue)",
            r"(goodbye|farewell).*(forever|final|last)",
            r"(planning|decided) to (die|end it)",
            r"(overdose|od|pills to end)",
            r"(method|plan) to (kill|hurt) myself",
        ],
        CrisisLevel.SEVERE: [
            r"(want to|wanna|going to) (die|disappear)",
            r"(cutting|self[- ]?harm|hurting myself)",
            r"(no reason to|what'?s the point of) (live|living|life)",
            r"(better off|world would be better) (dead|without me)",
            r"(giving away|saying goodbye to) (my stuff|everything)",
        ],
        CrisisLevel.MODERATE: [
            r"(feel|feeling) (hopeless|helpless|worthless|empty)",
            r"(can'?t|cannot) (cope|handle|take it|deal)",
            r"(tired of|exhausted by) (living|life|everything)",
            r"(no one|nobody) (cares|would miss|loves)",
            r"(burden|trouble) to (everyone|family|friends)",
        ],
        CrisisLevel.MILD: [
            r"(stressed|anxious|depressed|overwhelmed)",
            r"(struggling|having a hard time|difficult)",
            r"(lonely|isolated|alone|no friends)",
        ],
    }

    # Minor protection - age-related patterns
    AGE_INDICATORS = {
        "likely_minor": [
            r"(i('m| am)|i'?m) (\d{1,2}) (years? old|yo|y\.?o\.?)",
            r"(in|at) (middle|high|junior|elementary) school",
            r"(my parents|mom and dad|my teacher)",
            r"(homework|school project|test tomorrow)",
        ],
        "parental_reference": [
            r"(without|hide from|don'?t tell) (my )?(parents?|mom|dad|guardian)",
            r"(parents? (don'?t|won'?t) (know|find out|let me))",
        ],
    }

    # AI persona deception patterns
    DECEPTION_PATTERNS = [
        r"(i('m| am)|i'?m) (a )?(real|actual|human) (person|doctor|nurse|therapist)",
        r"(as your|i'?m your) (doctor|physician|nurse|therapist|counselor)",
        r"(can prescribe|write you a prescription|give you meds)",
        r"(diagnos(e|ing)|this is definitely|you have) (?!possibly|might|could)",
    ]

    def __init__(self, db: Session | None = None):
        self.db = db
        self._audit_log: list[SB243CheckResult] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance"""
        self._crisis_compiled = {level: [re.compile(p, re.IGNORECASE) for p in patterns] for level, patterns in self.CRISIS_PATTERNS.items()}
        self._age_compiled = {key: [re.compile(p, re.IGNORECASE) for p in patterns] for key, patterns in self.AGE_INDICATORS.items()}
        self._deception_compiled = [re.compile(p, re.IGNORECASE) for p in self.DECEPTION_PATTERNS]

    async def check(
        self,
        session_id: str,
        content: str,
        context: dict[str, Any],
        is_ai_response: bool = False,
    ) -> SB243CheckResult:
        """
        Main SB 243 compliance check.

        Args:
            session_id: Unique session identifier
            content: Text to check (user input or AI response)
            context: Session context (age, consent status, disclosure shown, etc.)
            is_ai_response: True if checking AI output, False for user input

        Returns:
            SB243CheckResult with pass/fail and detailed violations
        """
        audit_id = self._generate_audit_id(session_id)
        violations = []
        warnings = []

        # Determine user type
        user_age = context.get("user_age")
        user_type = self._determine_user_type(user_age, content)

        # Check 1: AI Disclosure
        ai_disclosure_present = context.get("ai_disclosure_shown", False)
        if not ai_disclosure_present:
            violations.append(
                SB243Violation(
                    violation_id=f"{audit_id}-001",
                    violation_type=SB243ViolationType.MISSING_AI_DISCLOSURE,
                    severity=SB243Severity.HIGH,
                    description="User has not been informed they are interacting with AI",
                    legal_reference="SB 243 Section 3(a) - AI Transparency Requirement",
                    remediation="Display clear AI disclosure before interaction begins",
                    evidence={"session_id": session_id, "disclosure_shown": False},
                )
            )

        # Check 2: Minor Protection
        consent_verified = context.get("consent_verified", False)
        if user_type == "minor":
            if not context.get("parental_consent"):
                violations.append(
                    SB243Violation(
                        violation_id=f"{audit_id}-002",
                        violation_type=SB243ViolationType.INADEQUATE_MINOR_PROTECTION,
                        severity=SB243Severity.CRITICAL,
                        description="Minor user without parental consent verification",
                        legal_reference="SB 243 Section 4(b) - Minor Protection Requirements",
                        remediation="Obtain verifiable parental consent before proceeding",
                        evidence={"user_type": "minor", "age": user_age},
                    )
                )

            # Check for hidden interaction attempts
            if self._check_age_bypass_attempts(content):
                violations.append(
                    SB243Violation(
                        violation_id=f"{audit_id}-003",
                        violation_type=SB243ViolationType.INADEQUATE_MINOR_PROTECTION,
                        severity=SB243Severity.HIGH,
                        description="Minor attempting to hide interaction from parents",
                        legal_reference="SB 243 Section 4(c) - Parental Notification",
                        remediation="Flag session for parental notification",
                        evidence={"bypass_detected": True, "content_sample": content[:100]},
                    )
                )

        # Check 3: Crisis Detection (CRITICAL for health apps)
        crisis_level = self._detect_crisis_level(content)
        escalation_required = crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.SEVERE]
        escalation_reason = None

        if crisis_level == CrisisLevel.CRITICAL:
            escalation_reason = "CRITICAL: Immediate suicide/self-harm risk detected"
            warnings.append("URGENT: Activate crisis intervention protocol immediately")
        elif crisis_level == CrisisLevel.SEVERE:
            escalation_reason = "SEVERE: High-risk self-harm indicators detected"
            warnings.append("HIGH PRIORITY: Route to human counselor")

        # Check if crisis response is adequate (for AI responses)
        if is_ai_response and crisis_level != CrisisLevel.NONE:
            if not context.get("crisis_resources_provided"):
                violations.append(
                    SB243Violation(
                        violation_id=f"{audit_id}-004",
                        violation_type=SB243ViolationType.CRISIS_ESCALATION_FAILURE,
                        severity=SB243Severity.CRITICAL,
                        description="AI response to crisis without providing resources",
                        legal_reference="SB 243 Section 5 - Crisis Response Requirements",
                        remediation="Include crisis hotline (988) and escalation path",
                        evidence={"crisis_level": crisis_level.value},
                    )
                )

        # Check 4: AI Persona Deception (for AI responses)
        if is_ai_response:
            deception_found = self._check_deception(content)
            if deception_found:
                violations.append(
                    SB243Violation(
                        violation_id=f"{audit_id}-005",
                        violation_type=SB243ViolationType.DECEPTIVE_PERSONA,
                        severity=SB243Severity.CRITICAL,
                        description="AI claiming to be human medical professional",
                        legal_reference="SB 243 Section 3(b) - Deceptive Persona Prohibition",
                        remediation="Remove claims of human identity; maintain AI transparency",
                        evidence={"deceptive_content": content[:200]},
                    )
                )

        # Check 5: Consent Trail
        if not consent_verified and context.get("processing_health_data"):
            violations.append(
                SB243Violation(
                    violation_id=f"{audit_id}-006",
                    violation_type=SB243ViolationType.MISSING_CONSENT,
                    severity=SB243Severity.HIGH,
                    description="Health data processing without explicit consent",
                    legal_reference="SB 243 Section 6 + CCPA 1798.100",
                    remediation="Obtain explicit consent before health data processing",
                    evidence={"health_data_present": True, "consent": False},
                )
            )

        # Build result
        passed = len([v for v in violations if v.severity in [SB243Severity.CRITICAL, SB243Severity.HIGH]]) == 0

        result = SB243CheckResult(
            passed=passed,
            session_id=session_id,
            user_type=user_type,
            ai_disclosure_present=ai_disclosure_present,
            consent_verified=consent_verified,
            crisis_level=crisis_level,
            violations=violations,
            warnings=warnings,
            escalation_required=escalation_required,
            escalation_reason=escalation_reason,
            audit_trail_id=audit_id,
        )

        # Log to audit trail
        self._audit_log.append(result)

        if not passed:
            logger.warning(f"SB243 VIOLATION: {session_id} - {[v.violation_type.value for v in violations]}")

        if escalation_required:
            logger.critical(f"SB243 CRISIS ESCALATION: {session_id} - {escalation_reason}")

        if self.db and (not passed or escalation_required):
            try:
                # Log critical/severe violations as adverse events
                for v in violations:
                    if v.severity in [SB243Severity.CRITICAL, SB243Severity.HIGH]:
                        event = ActiveShieldAdverseEvent(
                            session_id=audit_id,
                            event_type=f"sb243_violation_{v.violation_type.value}",
                            description=f"{v.description}. Remediation: {v.remediation}",
                            severity=v.severity.value,
                            context_snapshot=v.evidence,
                        )
                        self.db.add(event)

                # If crisis escalated, log that too
                if escalation_required:
                    event = ActiveShieldAdverseEvent(
                        session_id=audit_id,
                        event_type="crisis_escalation",
                        description=f"Crisis detected: {crisis_level.value}. {escalation_reason}",
                        severity="critical",
                        context_snapshot={
                            "content_sample": content[:200],
                            "resources_provided": context.get("crisis_resources_provided"),
                        },
                    )
                    self.db.add(event)

                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to persist SB243 adverse events: {e}")
                self.db.rollback()

        return result

    def _determine_user_type(self, user_age: int | None, content: str) -> str:
        """Determine if user is minor, adult, or unknown"""
        if user_age is not None:
            return "minor" if user_age < 18 else "adult"

        # Check content for age indicators
        for pattern in self._age_compiled.get("likely_minor", []):
            if pattern.search(content):
                return "minor"

        return "unknown"

    def _check_age_bypass_attempts(self, content: str) -> bool:
        """Check if minor is trying to hide interaction from parents"""
        for pattern in self._age_compiled.get("parental_reference", []):
            if pattern.search(content):
                return True
        return False

    def _detect_crisis_level(self, content: str) -> CrisisLevel:
        """Detect crisis/self-harm level in content"""
        # Check from most severe to least
        for level in [
            CrisisLevel.CRITICAL,
            CrisisLevel.SEVERE,
            CrisisLevel.MODERATE,
            CrisisLevel.MILD,
        ]:
            patterns = self._crisis_compiled.get(level, [])
            for pattern in patterns:
                if pattern.search(content):
                    return level
        return CrisisLevel.NONE

    def _check_deception(self, content: str) -> bool:
        """Check if AI is claiming to be human"""
        for pattern in self._deception_compiled:
            if pattern.search(content):
                return True
        return False

    def _generate_audit_id(self, session_id: str) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now(UTC).isoformat()
        content = f"sb243:{session_id}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # =========================================================================
    # Crisis Response Helpers
    # =========================================================================

    def get_crisis_response(self, crisis_level: CrisisLevel) -> dict[str, Any]:
        """Get appropriate crisis response for detected level"""
        responses = {
            CrisisLevel.CRITICAL: {
                "action": "IMMEDIATE_ESCALATION",
                "message": "I'm concerned about what you're sharing. Your safety matters. "
                "Please call 988 (Suicide & Crisis Lifeline) right now, or text HOME to 741741. "
                "I'm connecting you with a human counselor immediately.",
                "resources": [
                    {"name": "988 Suicide & Crisis Lifeline", "phone": "988", "available": "24/7"},
                    {"name": "Crisis Text Line", "text": "HOME to 741741", "available": "24/7"},
                    {
                        "name": "Emergency Services",
                        "phone": "911",
                        "when": "If in immediate danger",
                    },
                ],
                "escalate_to_human": True,
                "notify_emergency_contact": True,
            },
            CrisisLevel.SEVERE: {
                "action": "URGENT_ESCALATION",
                "message": "I hear that you're going through a really difficult time. "
                "I want to make sure you get the support you need. "
                "Would you like me to connect you with a counselor who can help?",
                "resources": [
                    {"name": "988 Suicide & Crisis Lifeline", "phone": "988", "available": "24/7"},
                    {"name": "Crisis Text Line", "text": "HOME to 741741", "available": "24/7"},
                ],
                "escalate_to_human": True,
                "notify_emergency_contact": False,
            },
            CrisisLevel.MODERATE: {
                "action": "OFFER_SUPPORT",
                "message": "It sounds like you're dealing with a lot right now. "
                "I'm here to listen, and I also want you to know that "
                "professional support is available if you'd find it helpful.",
                "resources": [
                    {"name": "988 Suicide & Crisis Lifeline", "phone": "988", "available": "24/7"},
                ],
                "escalate_to_human": False,
                "notify_emergency_contact": False,
            },
            CrisisLevel.MILD: {
                "action": "ACKNOWLEDGE",
                "message": "I hear you. It's completely normal to feel this way sometimes.",
                "resources": [],
                "escalate_to_human": False,
                "notify_emergency_contact": False,
            },
        }
        return responses.get(crisis_level, {"action": "CONTINUE", "escalate_to_human": False})

    def generate_ai_disclosure(self, platform_name: str = "this platform") -> str:
        """Generate compliant AI disclosure statement"""
        return (
            f"Before we continue, I want to be clear: I am an AI assistant, not a human. "
            f"I'm here to provide information and support on {platform_name}, but I am not "
            f"a licensed medical professional, therapist, or counselor. "
            f"For medical emergencies, please call 911. "
            f"For mental health crises, please call 988 (Suicide & Crisis Lifeline). "
            f"By continuing this conversation, you acknowledge that you are interacting with an AI system."
        )

    # =========================================================================
    # Audit & Reporting
    # =========================================================================

    def get_audit_trail(
        self,
        session_id: str | None = None,
        since: datetime | None = None,
        violations_only: bool = False,
        limit: int = 100,
    ) -> list[SB243CheckResult]:
        """Get audit trail for compliance reporting"""
        results = self._audit_log

        if session_id:
            results = [r for r in results if r.session_id == session_id]

        if since:
            results = [r for r in results if r.checked_at >= since]

        if violations_only:
            results = [r for r in results if not r.passed]

        return results[-limit:]

    def generate_compliance_summary(
        self,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate compliance summary for reporting"""
        results = self.get_audit_trail(since=since)

        total = len(results)
        passed = len([r for r in results if r.passed])
        violations_by_type: dict[str, int] = {}
        crisis_events: list[dict] = []

        for result in results:
            for violation in result.violations:
                vtype = violation.violation_type.value
                violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

            if result.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.SEVERE]:
                crisis_events.append(
                    {
                        "session_id": result.session_id,
                        "level": result.crisis_level.value,
                        "timestamp": result.checked_at.isoformat(),
                        "escalated": result.escalation_required,
                    }
                )

        return {
            "period_start": since.isoformat() if since else "all_time",
            "period_end": datetime.now(UTC).isoformat(),
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "compliance_rate": (passed / total * 100) if total > 0 else 100.0,
            "violations_by_type": violations_by_type,
            "crisis_events": len(crisis_events),
            "crisis_details": crisis_events,
        }


# Global instance
sb243_engine = SB243ComplianceEngine()
