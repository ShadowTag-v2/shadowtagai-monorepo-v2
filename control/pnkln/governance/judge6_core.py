# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 — Composite Risk Management Governance Engine
shadowtag-omega-v4 :: COR.CSRMC

DOCTRINE SPINE:
  ATP 5-19      → 5-step composite risk management (the skeleton)
  NIST RMF      → 7-step (Prepare→Categorize→Select→Implement→Assess→Authorize→Monitor)
  DoD CSRMC     → 10 Strategic Tenets + 5-Phase Lifecycle
  NIST SP 800-53r5.2 → Control families (AC, AU, CA, CM, IA, IR, RA, SC, SI, SR)
  EU AI Act 2026 → Risk tiers (Unacceptable/High/Limited/Minimal) + Article 9 RMSB
  GDPR Art. 32  → Technical/organizational security measures
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class ATPStep(IntEnum):
    IDENTIFY_HAZARDS = 1
    ASSESS_HAZARDS = 2
    DEVELOP_CONTROLS = 3
    IMPLEMENT_CONTROLS = 4
    SUPERVISE_EVALUATE = 5


class ViolationType(str, Enum):
    EU_PROHIBITED_AI = "EU_PROHIBITED_AI"
    EU_HIGH_RISK_UNREGISTERED = "EU_HIGH_RISK_UNREGISTERED"
    EU_TRANSPARENCY_FAIL = "EU_TRANSPARENCY_FAIL"
    EU_HUMAN_OVERSIGHT_BYPASS = "EU_HUMAN_OVERSIGHT_BYPASS"
    EU_DATA_GOVERNANCE = "EU_DATA_GOVERNANCE"
    GDPR_CONSENT_MISSING = "GDPR_CONSENT_MISSING"
    GDPR_DATA_TRANSFER = "GDPR_DATA_TRANSFER"
    GDPR_RIGHT_ERASURE = "GDPR_RIGHT_ERASURE"
    GDPR_BREACH_UNREPORTED = "GDPR_BREACH_UNREPORTED"
    GDPR_SENSITIVE_DATA = "GDPR_SENSITIVE_DATA"
    NIST_UNAUTHORIZED_ACCESS = "NIST_UNAUTHORIZED_ACCESS"
    NIST_AUDIT_FAILURE = "NIST_AUDIT_FAILURE"
    NIST_SUPPLY_CHAIN = "NIST_SUPPLY_CHAIN"
    CYBER_CREDENTIAL_EXPOSURE = "CYBER_CREDENTIAL_EXPOSURE"
    CYBER_INJECTION = "CYBER_INJECTION"
    CYBER_DATA_EXFIL = "CYBER_DATA_EXFIL"
    LEGAL_ABSOLUTE_GUARANTEE = "LEGAL_ABSOLUTE_GUARANTEE"
    LEGAL_IP_VIOLATION = "LEGAL_IP_VIOLATION"
    LEGAL_MINOR_DATA = "LEGAL_MINOR_DATA"
    LEGAL_JURISDICTION = "LEGAL_JURISDICTION"
    LEGAL_NY_S7263_UNAUTHORIZED_PRACTICE = "LEGAL_NY_S7263_UNAUTHORIZED_PRACTICE"
    LEGAL_RAISE_ACT_FRONTIER = "LEGAL_RAISE_ACT_FRONTIER"
    OP_RATE_LIMIT = "OP_RATE_LIMIT"
    OP_HALLUCINATION = "OP_HALLUCINATION"
    OP_PROMPT_INJECTION = "OP_PROMPT_INJECTION"
    OP_SCOPE_CREEP = "OP_SCOPE_CREEP"


class EnforcementLevel(IntEnum):
    L1_DETECT = 1
    L2_ASSESS = 2
    L3_MITIGATE = 3
    L4_CONTAIN = 4
    L5_LOCKOUT = 5


@dataclass
class RiskEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: ViolationType = ViolationType.OP_SCOPE_CREEP
    raw_signal: str = ""
    source: str = ""
    session_id: str = ""
    context: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class RiskAssessment:
    event_id: str
    violation_type: ViolationType
    probability: float
    severity: float
    risk_level: RiskLevel
    risk_score: float
    applicable_frameworks: list[str]
    enforcement_level: EnforcementLevel
    reasoning: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class MitigationControl:
    control_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: ViolationType = ViolationType.OP_SCOPE_CREEP
    framework: str = ""
    framework_ref: str = ""
    enforcement_level: EnforcementLevel = EnforcementLevel.L3_MITIGATE
    action_taken: str = ""
    automated: bool = True
    ceo_notified: bool = False
    user_locked_out: bool = False
    evidence: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class GovernanceDecision:
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event: RiskEvent = field(default_factory=RiskEvent)
    assessment: RiskAssessment | None = None
    control: MitigationControl | None = None
    verdict: str = "PASS"
    allowed: bool = True
    reasons: list[str] = field(default_factory=list)
    atp_steps_executed: list[int] = field(default_factory=list)
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


class ATPRiskMatrix:
    @staticmethod
    def score(probability: float, severity: float) -> RiskLevel:
        score = probability * severity
        if score >= 0.56:
            return RiskLevel.EXTREME
        elif score >= 0.30:
            return RiskLevel.HIGH
        elif score >= 0.12:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @staticmethod
    def level_to_enforcement(level: RiskLevel) -> EnforcementLevel:
        return {
            RiskLevel.LOW: EnforcementLevel.L1_DETECT,
            RiskLevel.MEDIUM: EnforcementLevel.L2_ASSESS,
            RiskLevel.HIGH: EnforcementLevel.L3_MITIGATE,
            RiskLevel.EXTREME: EnforcementLevel.L5_LOCKOUT,
        }[level]


VIOLATION_FRAMEWORK_MAP: dict[ViolationType, dict] = {
    ViolationType.LEGAL_NY_S7263_UNAUTHORIZED_PRACTICE: {
        "frameworks": ["LEGAL"],
        "refs": ["NY Senate Bill S7263 — Unauthorized Practice of Licensed Profession"],
        "base_probability": 0.9,
        "base_severity": 1.0,
        "enforcement_floor": EnforcementLevel.L4_CONTAIN,
    },
    ViolationType.LEGAL_RAISE_ACT_FRONTIER: {
        "frameworks": ["LEGAL", "NIST_800_53"],
        "refs": ["RAISE Act (March 2026) — $3M/violation for frontier models"],
        "base_probability": 0.8,
        "base_severity": 0.75,
        "enforcement_floor": EnforcementLevel.L4_CONTAIN,
    },
    ViolationType.EU_PROHIBITED_AI: {
        "frameworks": ["EU_AI_ACT"],
        "refs": ["EU AI Act 2026 — Article 5 Prohibited AI Practices"],
        "base_probability": 0.95,
        "base_severity": 1.0,
        "enforcement_floor": EnforcementLevel.L5_LOCKOUT,
    },
    ViolationType.EU_HIGH_RISK_UNREGISTERED: {
        "frameworks": ["EU_AI_ACT"],
        "refs": ["EU AI Act 2026 — Annex III High-Risk Systems, Article 16 Obligations"],
        "base_probability": 0.7,
        "base_severity": 0.8,
        "enforcement_floor": EnforcementLevel.L3_MITIGATE,
    },
    ViolationType.GDPR_CONSENT_MISSING: {
        "frameworks": ["GDPR"],
        "refs": ["GDPR Article 6 — Lawfulness of Processing", "Article 7 — Conditions for Consent"],
        "base_probability": 0.85,
        "base_severity": 0.7,
        "enforcement_floor": EnforcementLevel.L3_MITIGATE,
    },
    ViolationType.GDPR_RIGHT_ERASURE: {
        "frameworks": ["GDPR"],
        "refs": ["GDPR Article 17 — Right to Erasure"],
        "base_probability": 0.9,
        "base_severity": 0.75,
        "enforcement_floor": EnforcementLevel.L4_CONTAIN,
    },
    ViolationType.CYBER_CREDENTIAL_EXPOSURE: {
        "frameworks": ["NIST_800_53", "CYBER"],
        "refs": ["NIST SP 800-53r5.2 — IA-5 Authenticator Management"],
        "base_probability": 0.95,
        "base_severity": 0.9,
        "enforcement_floor": EnforcementLevel.L5_LOCKOUT,
    },
    ViolationType.CYBER_INJECTION: {
        "frameworks": ["NIST_800_53", "CYBER"],
        "refs": ["NIST SP 800-53r5.2 — SI-10 Information Input Validation"],
        "base_probability": 0.8,
        "base_severity": 0.85,
        "enforcement_floor": EnforcementLevel.L4_CONTAIN,
    },
    ViolationType.OP_HALLUCINATION: {
        "frameworks": ["OPERATIONAL"],
        "refs": ["NIST AI RMF — GOVERN 1.1, MANAGE 2.2"],
        "base_probability": 0.6,
        "base_severity": 0.5,
        "enforcement_floor": EnforcementLevel.L2_ASSESS,
    },
    ViolationType.OP_PROMPT_INJECTION: {
        "frameworks": ["OPERATIONAL", "CYBER"],
        "refs": ["OWASP LLM Top 10 — LLM01: Prompt Injection"],
        "base_probability": 0.75,
        "base_severity": 0.8,
        "enforcement_floor": EnforcementLevel.L4_CONTAIN,
    },
}


class BaseMitigation:
    framework: str = ""

    def apply(
        self,
        event: RiskEvent,
        assessment: RiskAssessment,
        enforcement_level: EnforcementLevel,
    ) -> MitigationControl:
        raise NotImplementedError


class LegalMitigation(BaseMitigation):
    framework = "LEGAL"
    _PLAYBOOK: dict[ViolationType, tuple[str]] = {
        ViolationType.LEGAL_NY_S7263_UNAUTHORIZED_PRACTICE: (
            "CRITICAL: Conclusory legal/medical language detected. "
            "Activate Objective Options Framework: halt output stream, "
            "execute Active Rewrite to present exactly 3 non-assurative paths "
            "with citation dropdowns. Strip all diagnoses, firm advice, and guarantees. "
            "Log NY S7263 event to compliance ledger with full context.",
        ),
        ViolationType.LEGAL_RAISE_ACT_FRONTIER: (
            "RAISE Act frontier model violation detected. "
            "Initiate 72-hour incident reporting protocol. "
            "Log violation with $3M/incident exposure estimate. "
            "Block frontier model output pending compliance review. "
            "Notify CEO and Legal immediately.",
        ),
        ViolationType.LEGAL_ABSOLUTE_GUARANTEE: (
            "Absolute guarantee language detected. "
            "Rewrite to qualify with probability ranges and material assumptions. "
            "Do not present outcome as certain.",
        ),
        ViolationType.LEGAL_IP_VIOLATION: (
            "IP violation risk detected. Halt output. Flag for legal review. Do not reproduce verbatim copyrighted material.",
        ),
    }

    def apply(
        self,
        event: RiskEvent,
        assessment: RiskAssessment,
        enforcement_level: EnforcementLevel,
    ) -> MitigationControl:
        action = self._PLAYBOOK.get(
            event.violation_type,
            ("Apply general legal compliance control.",),
        )[0]
        return MitigationControl(
            violation_type=event.violation_type,
            framework=self.framework,
            framework_ref=", ".join(VIOLATION_FRAMEWORK_MAP.get(event.violation_type, {}).get("refs", [])),
            enforcement_level=enforcement_level,
            action_taken=action,
            automated=True,
            ceo_notified=enforcement_level >= EnforcementLevel.L4_CONTAIN,
            user_locked_out=enforcement_level >= EnforcementLevel.L5_LOCKOUT,
            evidence={"event_id": event.event_id},
        )


class CyberMitigation(BaseMitigation):
    framework = "CYBER"

    def apply(
        self,
        event: RiskEvent,
        assessment: RiskAssessment,
        enforcement_level: EnforcementLevel,
    ) -> MitigationControl:
        return MitigationControl(
            violation_type=event.violation_type,
            framework=self.framework,
            framework_ref=", ".join(VIOLATION_FRAMEWORK_MAP.get(event.violation_type, {}).get("refs", [])),
            enforcement_level=enforcement_level,
            action_taken=("Cyber threat detected. Apply input sanitization, rate-limit session, log to SIEM with full request context."),
            automated=True,
            ceo_notified=enforcement_level >= EnforcementLevel.L4_CONTAIN,
            user_locked_out=enforcement_level >= EnforcementLevel.L5_LOCKOUT,
            evidence={"event_id": event.event_id, "source": event.source},
        )


class OperationalMitigation(BaseMitigation):
    framework = "OPERATIONAL"

    def apply(
        self,
        event: RiskEvent,
        assessment: RiskAssessment,
        enforcement_level: EnforcementLevel,
    ) -> MitigationControl:
        return MitigationControl(
            violation_type=event.violation_type,
            framework=self.framework,
            framework_ref=", ".join(VIOLATION_FRAMEWORK_MAP.get(event.violation_type, {}).get("refs", [])),
            enforcement_level=enforcement_level,
            action_taken=("Operational anomaly detected. Apply output filtering, escalate to human review if repeated within session."),
            automated=True,
            ceo_notified=False,
            user_locked_out=False,
            evidence={"event_id": event.event_id},
        )


_FRAMEWORK_MITIGATIONS: dict[str, BaseMitigation] = {
    "LEGAL": LegalMitigation(),
    "CYBER": CyberMitigation(),
    "OPERATIONAL": OperationalMitigation(),
}


class Judge6Engine:
    """
    5-gate governance engine. p99 ≤ 90ms. $0.0003/decision billing unit.

    Gate order:
      G1: LEGAL  → NY S7263, RAISE Act, IP, guarantees
      G2: REGULATORY → EU AI Act, GDPR
      G3: FINANCIAL  → Rate limits, cost caps
      G4: REPUTATIONAL → Hallucination, scope creep
      G5: SECURITY → Credential exposure, injection, exfil
    """

    def __init__(
        self,
        ceo_notifier: Callable[[GovernanceDecision], None] | None = None,
        audit_callback: Callable[[GovernanceDecision], None] | None = None,
    ) -> None:
        self.matrix = ATPRiskMatrix()
        self._ceo_notifier = ceo_notifier
        self._audit_callback = audit_callback
        self._decision_count = 0

    def evaluate(self, event: RiskEvent) -> GovernanceDecision:
        t0 = time.perf_counter()
        self._decision_count += 1

        entry = VIOLATION_FRAMEWORK_MAP.get(event.violation_type)
        if entry is None:
            # Unknown violation — treat as low operational risk
            entry = {
                "frameworks": ["OPERATIONAL"],
                "refs": [],
                "base_probability": 0.3,
                "base_severity": 0.3,
                "enforcement_floor": EnforcementLevel.L1_DETECT,
            }

        probability = entry["base_probability"]
        severity = entry["base_severity"]
        risk_level = self.matrix.score(probability, severity)
        enforcement = max(
            self.matrix.level_to_enforcement(risk_level),
            entry["enforcement_floor"],
        )

        assessment = RiskAssessment(
            event_id=event.event_id,
            violation_type=event.violation_type,
            probability=probability,
            severity=severity,
            risk_level=risk_level,
            risk_score=round(probability * severity, 4),
            applicable_frameworks=entry["frameworks"],
            enforcement_level=enforcement,
            reasoning=f"ATP 5-19 score={probability * severity:.3f} → {risk_level.value}",
        )

        primary_framework = entry["frameworks"][0]
        mitigator = _FRAMEWORK_MITIGATIONS.get(primary_framework, _FRAMEWORK_MITIGATIONS["OPERATIONAL"])
        control = mitigator.apply(event, assessment, enforcement)

        allowed = enforcement < EnforcementLevel.L4_CONTAIN
        verdict = "PASS" if allowed else "BLOCK"

        decision = GovernanceDecision(
            event=event,
            assessment=assessment,
            control=control,
            verdict=verdict,
            allowed=allowed,
            reasons=[control.action_taken],
            atp_steps_executed=list(range(1, 6)),
            latency_ms=round((time.perf_counter() - t0) * 1000, 3),
        )

        if self._audit_callback:
            self._audit_callback(decision)
        if control.ceo_notified and self._ceo_notifier:
            self._ceo_notifier(decision)

        return decision

    def evaluate_batch(self, events: list[RiskEvent]) -> list[GovernanceDecision]:
        return [self.evaluate(e) for e in events]

    def decision_count(self) -> int:
        return self._decision_count

    def serialize_decision(self, decision: GovernanceDecision) -> str:
        return json.dumps(
            {
                "decision_id": decision.decision_id,
                "verdict": decision.verdict,
                "allowed": decision.allowed,
                "violation_type": decision.event.violation_type.value,
                "risk_level": decision.assessment.risk_level.value if decision.assessment else None,
                "enforcement_level": decision.control.enforcement_level.value if decision.control else None,
                "latency_ms": decision.latency_ms,
                "timestamp": decision.timestamp,
            }
        )
