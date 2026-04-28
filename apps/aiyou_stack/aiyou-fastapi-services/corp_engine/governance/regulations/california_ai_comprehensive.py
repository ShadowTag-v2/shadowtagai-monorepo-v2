# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""California AI Comprehensive Regulations
========================================
Complete implementation of California's AI chatbot regulations.

Extends california_ai_minor.py with full coverage of:
- SB 1047: AI Safety and Security Act
- AB 2930: Automated Decision Tools
- AB 3030: AI Healthcare Restrictions
- Governor Newsom's AI Chatbot Safety Laws (2024-2025)

Core Requirements:
1. Detect and respond to self-harm statements
2. Disclose artificial nature of interactions
3. Provide break reminders for minors
4. Block explicit imagery to minors
5. Avoid impersonating medical professionals
6. Accept liability for real-world harm
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from .california_ai_minor import (
    CaliforniaAIMinorCompliance,
    MinorProtectionLevel,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Regulation Definitions
# =============================================================================


class CARegulation(StrEnum):
    """California AI Regulations"""

    # Self-harm detection and response
    CA_SELF_HARM_001 = "CA_SELF_HARM_001"
    CA_SELF_HARM_002 = "CA_SELF_HARM_002"

    # AI Disclosure requirements
    CA_DISCLOSURE_001 = "CA_DISCLOSURE_001"
    CA_DISCLOSURE_002 = "CA_DISCLOSURE_002"

    # Minor protection - break reminders
    CA_MINOR_BREAK_001 = "CA_MINOR_BREAK_001"
    CA_MINOR_BREAK_002 = "CA_MINOR_BREAK_002"

    # Explicit content blocking
    CA_EXPLICIT_001 = "CA_EXPLICIT_001"
    CA_EXPLICIT_002 = "CA_EXPLICIT_002"

    # Medical impersonation prohibition
    CA_MEDICAL_001 = "CA_MEDICAL_001"
    CA_MEDICAL_002 = "CA_MEDICAL_002"

    # Real-world harm liability
    CA_HARM_001 = "CA_HARM_001"

    # Data privacy (CPRA)
    CA_PRIVACY_001 = "CA_PRIVACY_001"
    CA_PRIVACY_002 = "CA_PRIVACY_002"


class TriggerCondition(StrEnum):
    """Conditions that trigger regulation checks"""

    ALWAYS = "always"
    CONVERSATION_START = "conversation_start"
    SELF_HARM_DETECTED = "self_harm_detected"
    EXPLICIT_CONTENT_DETECTED = "explicit_content_detected"
    MEDICAL_CLAIM_DETECTED = "medical_claim_detected"
    MINOR_USER = "minor_user"
    SESSION_DURATION_EXCEEDED = "session_duration_exceeded"
    DATA_COLLECTION = "data_collection"


class ActionType(StrEnum):
    """Actions to take on regulation match"""

    PASS = "pass"
    BLOCK = "block"
    WARN = "warn"
    DISCLOSE_AI = "disclose_ai"
    RESPOND_WITH_RESOURCES = "respond_with_resources"
    BREAK_REMINDER = "break_reminder"
    REQUIRE_CONSENT = "require_consent"
    FLAG_REVIEW = "flag_review"


# =============================================================================
# Regulation Rule Definitions
# =============================================================================


@dataclass
class RegulationRule:
    """Single regulation rule definition"""

    rule_id: str
    name: str
    description: str
    trigger: TriggerCondition
    action: ActionType
    severity: str  # info, low, medium, high, critical
    user_age_applies: list[MinorProtectionLevel] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    legal_reference: str = ""
    remediation: str = ""

    def applies_to_user(self, protection_level: MinorProtectionLevel) -> bool:
        """Check if rule applies to user's protection level"""
        if not self.user_age_applies:
            return True  # Applies to all
        return protection_level in self.user_age_applies


# =============================================================================
# Crisis Resources
# =============================================================================

CRISIS_RESOURCES = {
    "988_LIFELINE": {
        "name": "988 Suicide & Crisis Lifeline",
        "phone": "988",
        "text": "Text HOME to 741741",
        "url": "https://988lifeline.org/",
        "description": "Free, 24/7 support for people in distress",
    },
    "CRISIS_TEXT": {
        "name": "Crisis Text Line",
        "text": "Text HOME to 741741",
        "url": "https://www.crisistextline.org/",
        "description": "Text-based crisis support",
    },
    "TREVOR_PROJECT": {
        "name": "The Trevor Project",
        "phone": "1-866-488-7386",
        "text": "Text START to 678-678",
        "url": "https://www.thetrevorproject.org/",
        "description": "Crisis support for LGBTQ+ young people",
    },
    "SAMHSA": {
        "name": "SAMHSA National Helpline",
        "phone": "1-800-662-4357",
        "url": "https://www.samhsa.gov/find-help/national-helpline",
        "description": "Treatment referral service for substance abuse",
    },
}


# =============================================================================
# Self-Harm Detection Patterns
# =============================================================================

SELF_HARM_PATTERNS = {
    "explicit_ideation": [
        r"(?i)\b(want|going|plan|thinking)\s+(to\s+)?(kill|end|hurt)\s+(myself|my\s*life)",
        r"(?i)\bi\s+(want|wish)\s+(to\s+)?(die|be\s+dead)",
        r"(?i)\b(commit|attempting)\s+suicide\b",
        r"(?i)\bend\s+(it\s+all|my\s+life|everything)\b",
        r"(?i)\bsuicidal\s+(thoughts?|ideation|feelings?)\b",
    ],
    "self_harm_methods": [
        r"(?i)\b(cut|cutting|cuts)\s+(my|on)\s*(arm|wrist|leg|self|myself)\b",
        r"(?i)\b(overdose|od)\s+(on|with)\b",
        r"(?i)\bhow\s+to\s+(kill|hurt)\s+(myself|yourself)\b",
    ],
    "distress_indicators": [
        r"(?i)\bcan\'?t\s+(go\s+on|take\s+it|do\s+this)\s*(anymore)?\b",
        r"(?i)\beveryone\s+(would\s+be|is)\s+better\s+off\s+without\s+me\b",
        r"(?i)\bi\s*(don\'?t|never)\s+(want\s+to|will)\s+(wake\s+up|exist)\b",
        r"(?i)\bno\s+(point|reason)\s+(in\s+living|to\s+live)\b",
    ],
}


# =============================================================================
# Medical Impersonation Patterns
# =============================================================================

MEDICAL_IMPERSONATION_PATTERNS = [
    r"(?i)\bas\s+(a|your)\s+(doctor|physician|nurse|medical\s+professional)\b",
    r"(?i)\bi\s+am\s+(a|your)\s+(doctor|physician|nurse|psychiatrist|therapist)\b",
    r"(?i)\b(my|this)\s+(medical|clinical)\s+(advice|diagnosis|prescription)\b",
    r"(?i)\bi\'?ll?\s+(prescribe|diagnose|treat)\b",
    r"(?i)\b(take|stop\s+taking)\s+(this\s+medication|these\s+pills)\b",
]


# =============================================================================
# Explicit Content Patterns
# =============================================================================

EXPLICIT_CONTENT_PATTERNS = {
    "sexual": [
        r"(?i)\b(explicit|graphic)\s+sexual\b",
        r"(?i)\bporn(ography|ographic)?\b",
        r"(?i)\bnude(s|ity)?\b",
    ],
    "violence": [
        r"(?i)\b(graphic|extreme)\s+violence\b",
        r"(?i)\bgore\b",
        r"(?i)\btorture\b",
    ],
    "harmful": [
        r"(?i)\bhow\s+to\s+(make|build)\s+(a\s+)?(bomb|weapon|explosive)\b",
        r"(?i)\b(drug|narcotic)\s+(manufacturing|synthesis)\b",
    ],
}


# =============================================================================
# Core Regulation Rules
# =============================================================================

CALIFORNIA_AI_REGULATIONS: list[RegulationRule] = [
    # Self-harm detection and response
    RegulationRule(
        rule_id=CARegulation.CA_SELF_HARM_001.value,
        name="Self-Harm Detection",
        description="Detect self-harm or suicidal ideation in user messages",
        trigger=TriggerCondition.SELF_HARM_DETECTED,
        action=ActionType.RESPOND_WITH_RESOURCES,
        severity="critical",
        legal_reference="California AI Chatbot Safety Law 2024",
        remediation="Provide crisis resources and encourage professional help",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_SELF_HARM_002.value,
        name="Self-Harm Response Protocol",
        description="Respond with appropriate crisis resources when self-harm detected",
        trigger=TriggerCondition.SELF_HARM_DETECTED,
        action=ActionType.RESPOND_WITH_RESOURCES,
        severity="critical",
        parameters={"resources": ["988_LIFELINE", "CRISIS_TEXT"]},
        legal_reference="California AI Chatbot Safety Law 2024",
    ),
    # AI Disclosure
    RegulationRule(
        rule_id=CARegulation.CA_DISCLOSURE_001.value,
        name="AI Nature Disclosure - Conversation Start",
        description="Disclose AI nature at start of conversation",
        trigger=TriggerCondition.CONVERSATION_START,
        action=ActionType.DISCLOSE_AI,
        severity="medium",
        parameters={"disclosure_text": "I am an AI assistant. I am not a human."},
        legal_reference="California AI Transparency Law",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_DISCLOSURE_002.value,
        name="AI Nature Disclosure - On Request",
        description="Disclose AI nature when user asks",
        trigger=TriggerCondition.ALWAYS,
        action=ActionType.DISCLOSE_AI,
        severity="high",
        legal_reference="California AI Transparency Law",
    ),
    # Minor Break Reminders
    RegulationRule(
        rule_id=CARegulation.CA_MINOR_BREAK_001.value,
        name="Minor Break Reminder - 60 Minutes",
        description="Remind minor users to take a break after 60 minutes",
        trigger=TriggerCondition.SESSION_DURATION_EXCEEDED,
        action=ActionType.BREAK_REMINDER,
        severity="medium",
        user_age_applies=[
            MinorProtectionLevel.UNDER_13,
            MinorProtectionLevel.TEEN_13_15,
            MinorProtectionLevel.TEEN_16_17,
        ],
        parameters={
            "threshold_minutes": 60,
            "reminder_text": "You've been chatting for a while. Consider taking a break!",
        },
        legal_reference="California Age-Appropriate Design Code Act",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_MINOR_BREAK_002.value,
        name="Minor Break Reminder - 30 Minutes (Under 13)",
        description="Remind users under 13 to take a break after 30 minutes",
        trigger=TriggerCondition.SESSION_DURATION_EXCEEDED,
        action=ActionType.BREAK_REMINDER,
        severity="high",
        user_age_applies=[MinorProtectionLevel.UNDER_13],
        parameters={
            "threshold_minutes": 30,
            "reminder_text": "Time for a break! Go do something fun offline!",
        },
        legal_reference="California Age-Appropriate Design Code Act + COPPA",
    ),
    # Explicit Content Blocking
    RegulationRule(
        rule_id=CARegulation.CA_EXPLICIT_001.value,
        name="Explicit Content Block - Minors",
        description="Block explicit imagery and content for minors",
        trigger=TriggerCondition.EXPLICIT_CONTENT_DETECTED,
        action=ActionType.BLOCK,
        severity="critical",
        user_age_applies=[
            MinorProtectionLevel.UNDER_13,
            MinorProtectionLevel.TEEN_13_15,
            MinorProtectionLevel.TEEN_16_17,
        ],
        legal_reference="California AI Chatbot Safety Law 2024",
        remediation="Remove or block explicit content before display",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_EXPLICIT_002.value,
        name="Explicit Content Warning - Adults",
        description="Warn adults before displaying explicit content",
        trigger=TriggerCondition.EXPLICIT_CONTENT_DETECTED,
        action=ActionType.WARN,
        severity="medium",
        user_age_applies=[MinorProtectionLevel.ADULT],
        parameters={"warning_text": "This content may contain explicit material."},
    ),
    # Medical Impersonation
    RegulationRule(
        rule_id=CARegulation.CA_MEDICAL_001.value,
        name="Medical Professional Impersonation Block",
        description="Prevent AI from impersonating medical professionals",
        trigger=TriggerCondition.MEDICAL_CLAIM_DETECTED,
        action=ActionType.BLOCK,
        severity="critical",
        legal_reference="AB 3030 - AI Healthcare Restrictions",
        remediation="Clarify AI is not a medical professional and recommend consulting a real doctor",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_MEDICAL_002.value,
        name="Medical Advice Disclaimer",
        description="Add disclaimer when health topics discussed",
        trigger=TriggerCondition.MEDICAL_CLAIM_DETECTED,
        action=ActionType.WARN,
        severity="high",
        parameters={
            "disclaimer": "I am an AI and cannot provide medical advice. Please consult a healthcare professional.",
        },
        legal_reference="AB 3030 - AI Healthcare Restrictions",
    ),
    # Privacy
    RegulationRule(
        rule_id=CARegulation.CA_PRIVACY_001.value,
        name="Minor Data Collection Consent",
        description="Require parental consent for minor data collection",
        trigger=TriggerCondition.DATA_COLLECTION,
        action=ActionType.REQUIRE_CONSENT,
        severity="high",
        user_age_applies=[MinorProtectionLevel.UNDER_13],
        legal_reference="CPRA + COPPA",
    ),
    RegulationRule(
        rule_id=CARegulation.CA_PRIVACY_002.value,
        name="Teen Data Collection Notice",
        description="Notify teens about data collection",
        trigger=TriggerCondition.DATA_COLLECTION,
        action=ActionType.WARN,
        severity="medium",
        user_age_applies=[
            MinorProtectionLevel.TEEN_13_15,
            MinorProtectionLevel.TEEN_16_17,
        ],
        legal_reference="CPRA",
    ),
]


# =============================================================================
# Comprehensive Compliance Engine
# =============================================================================


@dataclass
class RuleEvaluation:
    """Result of evaluating a single rule"""

    rule: RegulationRule
    triggered: bool
    action_taken: ActionType
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComprehensiveComplianceResult:
    """Result of comprehensive compliance check"""

    content_id: str
    timestamp: datetime
    user_protection_level: MinorProtectionLevel
    is_compliant: bool
    evaluations: list[RuleEvaluation]
    violations: list[dict[str, Any]]
    required_actions: list[ActionType]
    crisis_response_needed: bool = False
    crisis_resources: list[dict[str, Any]] = field(default_factory=list)
    disclosure_required: bool = False
    disclosure_text: str = ""
    break_reminder_due: bool = False
    break_reminder_text: str = ""
    processing_time_ms: float = 0.0


class CaliforniaAIComprehensiveCompliance:
    """Comprehensive California AI Compliance Engine.

    Extends CaliforniaAIMinorCompliance with full regulation coverage:
    - Self-harm detection and crisis response
    - AI disclosure requirements
    - Break reminders for minors
    - Explicit content blocking
    - Medical impersonation prevention
    - Privacy compliance (CPRA)
    """

    def __init__(self):
        self.minor_compliance = CaliforniaAIMinorCompliance()
        self.rules = CALIFORNIA_AI_REGULATIONS
        self.crisis_resources = CRISIS_RESOURCES

        # Compile patterns for efficiency
        self._self_harm_patterns = self._compile_patterns(SELF_HARM_PATTERNS)
        self._medical_patterns = [re.compile(p) for p in MEDICAL_IMPERSONATION_PATTERNS]
        self._explicit_patterns = self._compile_patterns(EXPLICIT_CONTENT_PATTERNS)

        # Session tracking
        self._session_start_times: dict[str, datetime] = {}

        # Audit log
        self._compliance_log: list[ComprehensiveComplianceResult] = []

    def _compile_patterns(self, pattern_dict: dict[str, list[str]]) -> dict[str, list[re.Pattern]]:
        """Compile regex patterns for efficiency"""
        compiled = {}
        for category, patterns in pattern_dict.items():
            compiled[category] = [re.compile(p) for p in patterns]
        return compiled

    # =========================================================================
    # Self-Harm Detection
    # =========================================================================

    def detect_self_harm(self, text: str) -> dict[str, Any]:
        """Detect self-harm or suicidal ideation in text.

        Returns:
            Dict with detected patterns and confidence score

        """
        detections = []
        max_confidence = 0.0

        for category, patterns in self._self_harm_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Higher confidence for explicit ideation
                    confidence = 0.95 if category == "explicit_ideation" else 0.75
                    max_confidence = max(max_confidence, confidence)
                    detections.append(
                        {
                            "category": category,
                            "pattern": pattern.pattern,
                            "matches": matches,
                            "confidence": confidence,
                        },
                    )

        return {
            "detected": len(detections) > 0,
            "confidence": max_confidence,
            "detections": detections,
            "crisis_response_needed": max_confidence > 0.7,
        }

    # =========================================================================
    # Medical Impersonation Detection
    # =========================================================================

    def detect_medical_impersonation(self, text: str) -> dict[str, Any]:
        """Detect if AI is impersonating a medical professional"""
        detections = []

        for pattern in self._medical_patterns:
            matches = pattern.findall(text)
            if matches:
                detections.append({"pattern": pattern.pattern, "matches": matches})

        return {
            "detected": len(detections) > 0,
            "detections": detections,
            "impersonation_confidence": 0.9 if detections else 0.0,
        }

    # =========================================================================
    # Explicit Content Detection
    # =========================================================================

    def detect_explicit_content(self, text: str) -> dict[str, Any]:
        """Detect explicit content in text"""
        detections = []

        for category, patterns in self._explicit_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    detections.append(
                        {"category": category, "pattern": pattern.pattern, "matches": matches},
                    )

        return {
            "detected": len(detections) > 0,
            "categories": list(set(d["category"] for d in detections)),
            "detections": detections,
        }

    # =========================================================================
    # Session Management
    # =========================================================================

    def start_session(self, session_id: str) -> None:
        """Start tracking a session"""
        self._session_start_times[session_id] = datetime.utcnow()

    def get_session_duration_minutes(self, session_id: str) -> int:
        """Get session duration in minutes"""
        if session_id not in self._session_start_times:
            return 0
        duration = datetime.utcnow() - self._session_start_times[session_id]
        return int(duration.total_seconds() / 60)

    def check_break_reminder(
        self,
        session_id: str,
        protection_level: MinorProtectionLevel,
    ) -> dict[str, Any]:
        """Check if break reminder is due"""
        duration = self.get_session_duration_minutes(session_id)

        # Different thresholds by age
        if protection_level == MinorProtectionLevel.UNDER_13:
            threshold = 30
            reminder_text = "Time for a break! Go do something fun offline!"
        elif protection_level in [MinorProtectionLevel.TEEN_13_15, MinorProtectionLevel.TEEN_16_17]:
            threshold = 60
            reminder_text = "You've been chatting for a while. Consider taking a break!"
        else:
            return {"due": False, "duration_minutes": duration}

        return {
            "due": duration >= threshold,
            "duration_minutes": duration,
            "threshold_minutes": threshold,
            "reminder_text": reminder_text if duration >= threshold else None,
        }

    # =========================================================================
    # Main Compliance Check
    # =========================================================================

    async def check_compliance(
        self,
        content_id: str,
        text: str,
        protection_level: MinorProtectionLevel,
        session_id: str | None = None,
        is_conversation_start: bool = False,
        data_collection: bool = False,
    ) -> ComprehensiveComplianceResult:
        """Main comprehensive compliance check.

        Args:
            content_id: Unique content identifier
            text: Text content to check
            protection_level: User's protection level
            session_id: Session identifier for break reminders
            is_conversation_start: Whether this is start of conversation
            data_collection: Whether data collection is occurring

        Returns:
            ComprehensiveComplianceResult with all evaluations and required actions

        """
        import time

        start_time = time.time()

        evaluations = []
        violations = []
        required_actions = []

        # Detection flags
        self_harm_result = self.detect_self_harm(text)
        medical_result = self.detect_medical_impersonation(text)
        explicit_result = self.detect_explicit_content(text)

        # Evaluate each rule
        for rule in self.rules:
            evaluation = self._evaluate_rule(
                rule=rule,
                protection_level=protection_level,
                self_harm_result=self_harm_result,
                medical_result=medical_result,
                explicit_result=explicit_result,
                session_id=session_id,
                is_conversation_start=is_conversation_start,
                data_collection=data_collection,
            )

            evaluations.append(evaluation)

            if evaluation.triggered and evaluation.action_taken != ActionType.PASS:
                violations.append(
                    {
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "severity": rule.severity,
                        "action": evaluation.action_taken.value,
                        "details": evaluation.details,
                        "legal_reference": rule.legal_reference,
                        "remediation": rule.remediation,
                    },
                )
                if evaluation.action_taken not in required_actions:
                    required_actions.append(evaluation.action_taken)

        # Build result
        crisis_resources = []
        if self_harm_result["crisis_response_needed"]:
            crisis_resources = [
                self.crisis_resources[r] for r in ["988_LIFELINE", "CRISIS_TEXT", "TREVOR_PROJECT"]
            ]

        # Check break reminder
        break_check = {"due": False, "reminder_text": None}
        if session_id:
            break_check = self.check_break_reminder(session_id, protection_level)

        # Disclosure text
        disclosure_text = ""
        if is_conversation_start or ActionType.DISCLOSE_AI in required_actions:
            disclosure_text = "I am an AI assistant. I am not a human."

        processing_time = (time.time() - start_time) * 1000

        result = ComprehensiveComplianceResult(
            content_id=content_id,
            timestamp=datetime.utcnow(),
            user_protection_level=protection_level,
            is_compliant=len(violations) == 0
            or all(v["action"] in ["warn", "disclose_ai", "break_reminder"] for v in violations),
            evaluations=evaluations,
            violations=violations,
            required_actions=required_actions,
            crisis_response_needed=self_harm_result["crisis_response_needed"],
            crisis_resources=crisis_resources,
            disclosure_required=ActionType.DISCLOSE_AI in required_actions or is_conversation_start,
            disclosure_text=disclosure_text,
            break_reminder_due=break_check["due"],
            break_reminder_text=break_check.get("reminder_text", ""),
            processing_time_ms=processing_time,
        )

        # Log result
        self._compliance_log.append(result)

        return result

    def _evaluate_rule(
        self,
        rule: RegulationRule,
        protection_level: MinorProtectionLevel,
        self_harm_result: dict[str, Any],
        medical_result: dict[str, Any],
        explicit_result: dict[str, Any],
        session_id: str | None,
        is_conversation_start: bool,
        data_collection: bool,
    ) -> RuleEvaluation:
        """Evaluate a single rule"""
        # Check if rule applies to this user
        if not rule.applies_to_user(protection_level):
            return RuleEvaluation(
                rule=rule,
                triggered=False,
                action_taken=ActionType.PASS,
                details={"reason": "Rule does not apply to user age category"},
            )

        triggered = False
        details = {}

        # Check trigger conditions
        if rule.trigger == TriggerCondition.ALWAYS:
            triggered = True

        elif rule.trigger == TriggerCondition.SELF_HARM_DETECTED:
            if self_harm_result["detected"]:
                triggered = True
                details["self_harm"] = self_harm_result

        elif rule.trigger == TriggerCondition.MEDICAL_CLAIM_DETECTED:
            if medical_result["detected"]:
                triggered = True
                details["medical"] = medical_result

        elif rule.trigger == TriggerCondition.EXPLICIT_CONTENT_DETECTED:
            if explicit_result["detected"]:
                triggered = True
                details["explicit"] = explicit_result

        elif rule.trigger == TriggerCondition.CONVERSATION_START:
            if is_conversation_start:
                triggered = True

        elif rule.trigger == TriggerCondition.SESSION_DURATION_EXCEEDED:
            if session_id:
                duration = self.get_session_duration_minutes(session_id)
                threshold = rule.parameters.get("threshold_minutes", 60)
                if duration >= threshold:
                    triggered = True
                    details["session_duration"] = duration
                    details["threshold"] = threshold

        elif rule.trigger == TriggerCondition.MINOR_USER:
            if protection_level != MinorProtectionLevel.ADULT:
                triggered = True

        elif rule.trigger == TriggerCondition.DATA_COLLECTION and data_collection:
            triggered = True

        return RuleEvaluation(
            rule=rule,
            triggered=triggered,
            action_taken=rule.action if triggered else ActionType.PASS,
            details=details,
        )

    # =========================================================================
    # Crisis Response Generation
    # =========================================================================

    def generate_crisis_response(self) -> str:
        """Generate a crisis response message with resources"""
        return """I'm concerned about what you've shared. Please know that you're not alone, and help is available.

**If you're in immediate danger, please call 911.**

Here are resources that can help:

**988 Suicide & Crisis Lifeline**
- Call or text: **988**
- Available 24/7, free and confidential

**Crisis Text Line**
- Text HOME to **741741**
- Free, 24/7 support

**The Trevor Project** (LGBTQ+ support)
- Call: 1-866-488-7386
- Text START to 678-678

Please reach out to one of these resources or talk to someone you trust. You matter, and there are people who want to help."""

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_compliance_report(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate compliance report"""
        records = self._compliance_log

        if start_date:
            records = [r for r in records if r.timestamp >= start_date]
        if end_date:
            records = [r for r in records if r.timestamp <= end_date]

        total = len(records)
        compliant = sum(1 for r in records if r.is_compliant)
        crisis_responses = sum(1 for r in records if r.crisis_response_needed)

        violations_by_rule = {}
        for record in records:
            for violation in record.violations:
                rule_id = violation["rule_id"]
                violations_by_rule[rule_id] = violations_by_rule.get(rule_id, 0) + 1

        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
            "total_checks": total,
            "compliant_checks": compliant,
            "compliance_rate": compliant / total if total > 0 else 1.0,
            "crisis_responses": crisis_responses,
            "violations_by_rule": violations_by_rule,
        }


# Global instance
ca_comprehensive_compliance = CaliforniaAIComprehensiveCompliance()
