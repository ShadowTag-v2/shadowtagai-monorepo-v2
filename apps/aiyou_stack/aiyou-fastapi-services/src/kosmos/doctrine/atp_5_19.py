"""ATP 5-19: Composite Risk Management
====================================

Source: ATP 5-19 (April 2014)

Five-step risk management process:
1. Identify hazards
2. Assess hazards (probability × severity)
3. Develop controls
4. Implement controls
5. Supervise and evaluate

Risk levels: LOW, MEDIUM, HIGH, EXTREMELY HIGH
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Probability(Enum):
    """ATP 5-19 Table 1-1: Probability Levels"""

    FREQUENT = "A"  # Continuously experienced
    LIKELY = "B"  # Occurs several times
    OCCASIONAL = "C"  # Occurs sporadically
    SELDOM = "D"  # Unlikely but possible
    UNLIKELY = "E"  # Probability approaching zero


class Severity(Enum):
    """ATP 5-19 Table 1-2: Severity Categories"""

    CATASTROPHIC = "I"  # Death, total system loss, $10M+ loss
    CRITICAL = "II"  # Permanent injury, major system damage, $1M-$10M
    MARGINAL = "III"  # Minor injury, minor system damage, $100K-$1M
    NEGLIGIBLE = "IV"  # First aid, slight damage, <$100K


class RiskLevel(Enum):
    """ATP 5-19 Figure 1-3: Risk Levels"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREMELY_HIGH = "EXTREMELY_HIGH"


# ATP 5-19 Risk Assessment Matrix (Figure 1-3)
RISK_MATRIX = {
    # (Probability, Severity) -> Risk Level
    (Probability.FREQUENT, Severity.CATASTROPHIC): RiskLevel.EXTREMELY_HIGH,
    (Probability.FREQUENT, Severity.CRITICAL): RiskLevel.EXTREMELY_HIGH,
    (Probability.FREQUENT, Severity.MARGINAL): RiskLevel.HIGH,
    (Probability.FREQUENT, Severity.NEGLIGIBLE): RiskLevel.MEDIUM,
    (Probability.LIKELY, Severity.CATASTROPHIC): RiskLevel.EXTREMELY_HIGH,
    (Probability.LIKELY, Severity.CRITICAL): RiskLevel.HIGH,
    (Probability.LIKELY, Severity.MARGINAL): RiskLevel.MEDIUM,
    (Probability.LIKELY, Severity.NEGLIGIBLE): RiskLevel.LOW,
    (Probability.OCCASIONAL, Severity.CATASTROPHIC): RiskLevel.HIGH,
    (Probability.OCCASIONAL, Severity.CRITICAL): RiskLevel.HIGH,
    (Probability.OCCASIONAL, Severity.MARGINAL): RiskLevel.MEDIUM,
    (Probability.OCCASIONAL, Severity.NEGLIGIBLE): RiskLevel.LOW,
    (Probability.SELDOM, Severity.CATASTROPHIC): RiskLevel.HIGH,
    (Probability.SELDOM, Severity.CRITICAL): RiskLevel.MEDIUM,
    (Probability.SELDOM, Severity.MARGINAL): RiskLevel.LOW,
    (Probability.SELDOM, Severity.NEGLIGIBLE): RiskLevel.LOW,
    (Probability.UNLIKELY, Severity.CATASTROPHIC): RiskLevel.MEDIUM,
    (Probability.UNLIKELY, Severity.CRITICAL): RiskLevel.MEDIUM,
    (Probability.UNLIKELY, Severity.MARGINAL): RiskLevel.LOW,
    (Probability.UNLIKELY, Severity.NEGLIGIBLE): RiskLevel.LOW,
}

# Consensus thresholds per risk level
CONSENSUS_THRESHOLDS = {
    RiskLevel.LOW: 0.50,  # Screen security (50%)
    RiskLevel.MEDIUM: 0.60,  # Standard consensus
    RiskLevel.HIGH: 0.75,  # Guard security (75%)
    RiskLevel.EXTREMELY_HIGH: 0.90,  # Cover security (90%)
}

# Approval authority per risk level (ATP 5-19 Table 1-3)
APPROVAL_AUTHORITY = {
    RiskLevel.LOW: "First-line supervisor",
    RiskLevel.MEDIUM: "Company commander or equivalent",
    RiskLevel.HIGH: "Battalion commander or equivalent",
    RiskLevel.EXTREMELY_HIGH: "Brigade commander or higher",
}


@dataclass
class Hazard:
    """ATP 5-19 Step 1: Identify Hazards

    A hazard is any condition, actual or potential, that could cause
    injury, illness, or death; damage to or loss of equipment, property,
    or mission degradation.
    """

    id: str
    description: str
    category: str  # tactical, accident, health, environmental
    source: str  # Where/what creates the hazard

    # Assessment (Step 2)
    probability: Probability | None = None
    severity: Severity | None = None
    risk_level: RiskLevel | None = None

    # Metadata
    identified_at: datetime = field(default_factory=datetime.utcnow)
    identified_by: str = ""

    def assess(self, probability: Probability, severity: Severity) -> RiskLevel:
        """ATP 5-19 Step 2: Assess Hazards

        Use risk matrix to determine risk level.
        """
        self.probability = probability
        self.severity = severity
        self.risk_level = RISK_MATRIX.get((probability, severity), RiskLevel.MEDIUM)
        return self.risk_level

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "source": self.source,
            "probability": self.probability.value if self.probability else None,
            "severity": self.severity.value if self.severity else None,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "atp_reference": "ATP 5-19",
        }


@dataclass
class Control:
    """ATP 5-19 Step 3: Develop Controls

    Controls eliminate hazards or reduce their risk.
    Types: Engineering, Administrative, PPE
    """

    id: str
    hazard_id: str
    description: str
    control_type: str  # engineering, administrative, ppe

    # Effectiveness
    reduces_probability_to: Probability | None = None
    reduces_severity_to: Severity | None = None
    residual_risk: RiskLevel | None = None

    # Implementation (Step 4)
    implemented: bool = False
    implemented_at: datetime | None = None
    implemented_by: str = ""

    # Supervision (Step 5)
    last_evaluated: datetime | None = None
    evaluation_result: str = ""

    def calculate_residual_risk(self, hazard: Hazard) -> RiskLevel:
        """Calculate risk after control is applied"""
        prob = self.reduces_probability_to or hazard.probability
        sev = self.reduces_severity_to or hazard.severity

        if prob and sev:
            self.residual_risk = RISK_MATRIX.get((prob, sev), RiskLevel.MEDIUM)
        return self.residual_risk

    def implement(self, by: str):
        """ATP 5-19 Step 4: Implement Controls"""
        self.implemented = True
        self.implemented_at = datetime.utcnow()
        self.implemented_by = by

    def evaluate(self, result: str):
        """ATP 5-19 Step 5: Supervise and Evaluate"""
        self.last_evaluated = datetime.utcnow()
        self.evaluation_result = result

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "hazard_id": self.hazard_id,
            "description": self.description,
            "control_type": self.control_type,
            "implemented": self.implemented,
            "residual_risk": self.residual_risk.value if self.residual_risk else None,
            "atp_reference": "ATP 5-19",
        }


class RiskMatrix:
    """ATP 5-19 Risk Assessment Matrix utility class.

    Provides methods to assess and visualize risk.
    """

    @staticmethod
    def assess(probability: Probability, severity: Severity) -> RiskLevel:
        """Get risk level from probability and severity"""
        return RISK_MATRIX.get((probability, severity), RiskLevel.MEDIUM)

    @staticmethod
    def get_threshold(risk_level: RiskLevel) -> float:
        """Get consensus threshold for risk level"""
        return CONSENSUS_THRESHOLDS.get(risk_level, 0.60)

    @staticmethod
    def get_approval_authority(risk_level: RiskLevel) -> str:
        """Get required approval authority for risk level"""
        return APPROVAL_AUTHORITY.get(risk_level, "Commander")

    @staticmethod
    def render_matrix() -> str:
        """Render ASCII risk matrix"""
        return """
ATP 5-19 RISK ASSESSMENT MATRIX
═══════════════════════════════════════════════════════════════
                           SEVERITY
           │ Catastrophic│ Critical │ Marginal │ Negligible │
           │     (I)     │   (II)   │  (III)   │    (IV)    │
───────────┼─────────────┼──────────┼──────────┼────────────┤
Frequent   │  EXTREMELY  │ EXTREMELY│   HIGH   │   MEDIUM   │
  (A)      │    HIGH     │   HIGH   │          │            │
───────────┼─────────────┼──────────┼──────────┼────────────┤
Likely     │  EXTREMELY  │   HIGH   │  MEDIUM  │    LOW     │
  (B)      │    HIGH     │          │          │            │
───────────┼─────────────┼──────────┼──────────┼────────────┤
Occasional │    HIGH     │   HIGH   │  MEDIUM  │    LOW     │
  (C)      │             │          │          │            │
───────────┼─────────────┼──────────┼──────────┼────────────┤
Seldom     │    HIGH     │  MEDIUM  │   LOW    │    LOW     │
  (D)      │             │          │          │            │
───────────┼─────────────┼──────────┼──────────┼────────────┤
Unlikely   │   MEDIUM    │  MEDIUM  │   LOW    │    LOW     │
  (E)      │             │          │          │            │
═══════════════════════════════════════════════════════════════
"""


@dataclass
class RiskManager:
    """ATP 5-19 Composite Risk Management Engine

    Implements the 5-step CRM process for AI agent tasks.
    """

    session_id: str
    hazards: list[Hazard] = field(default_factory=list)
    controls: list[Control] = field(default_factory=list)

    # Overall assessment
    initial_risk: RiskLevel | None = None
    residual_risk: RiskLevel | None = None

    async def step1_identify_hazards(
        self, task: str, context: dict[str, Any] = None,
    ) -> list[Hazard]:
        """Step 1: Identify Hazards

        Identify conditions that could cause mission degradation.
        For AI agents: errors, security issues, resource exhaustion, etc.
        """
        hazards = []

        # Standard AI task hazards
        hazard_templates = [
            ("H001", "API failure or timeout", "technical", "External service dependency"),
            ("H002", "Invalid or malicious input", "security", "User input"),
            ("H003", "Resource exhaustion (tokens/compute)", "operational", "System limits"),
            ("H004", "Data leakage or privacy violation", "security", "Output generation"),
            ("H005", "Incorrect output affecting decisions", "operational", "Model inference"),
        ]

        for hid, desc, cat, src in hazard_templates:
            hazard = Hazard(
                id=hid, description=desc, category=cat, source=src, identified_by="RiskManager",
            )
            hazards.append(hazard)

        self.hazards = hazards
        return hazards

    async def step2_assess_hazards(self) -> RiskLevel:
        """Step 2: Assess Hazards

        Determine probability and severity for each hazard.
        Calculate overall initial risk.
        """
        max_risk = RiskLevel.LOW

        for hazard in self.hazards:
            # Default assessment (should be customized per task)
            if hazard.category == "security":
                hazard.assess(Probability.OCCASIONAL, Severity.CRITICAL)
            elif hazard.category == "technical":
                hazard.assess(Probability.LIKELY, Severity.MARGINAL)
            else:
                hazard.assess(Probability.OCCASIONAL, Severity.MARGINAL)

            # Track highest risk
            if hazard.risk_level:
                risk_order = [
                    RiskLevel.LOW,
                    RiskLevel.MEDIUM,
                    RiskLevel.HIGH,
                    RiskLevel.EXTREMELY_HIGH,
                ]
                if risk_order.index(hazard.risk_level) > risk_order.index(max_risk):
                    max_risk = hazard.risk_level

        self.initial_risk = max_risk
        return max_risk

    async def step3_develop_controls(self) -> list[Control]:
        """Step 3: Develop Controls

        Create controls to mitigate each hazard.
        """
        controls = []

        control_templates = {
            "H001": ("C001", "Implement retry logic with exponential backoff", "engineering"),
            "H002": ("C002", "Input validation and sanitization", "engineering"),
            "H003": ("C003", "Token budget limits and monitoring", "administrative"),
            "H004": ("C004", "Output filtering and PII detection", "engineering"),
            "H005": ("C005", "Confidence thresholds and human review", "administrative"),
        }

        for hazard in self.hazards:
            if hazard.id in control_templates:
                cid, desc, ctype = control_templates[hazard.id]
                control = Control(
                    id=cid,
                    hazard_id=hazard.id,
                    description=desc,
                    control_type=ctype,
                    reduces_probability_to=Probability.SELDOM,
                )
                control.calculate_residual_risk(hazard)
                controls.append(control)

        self.controls = controls
        return controls

    async def step4_implement_controls(self, implementer: str = "System") -> int:
        """Step 4: Implement Controls

        Activate all developed controls.
        Returns count of implemented controls.
        """
        count = 0
        for control in self.controls:
            if not control.implemented:
                control.implement(implementer)
                count += 1
        return count

    async def step5_supervise_evaluate(self) -> dict[str, Any]:
        """Step 5: Supervise and Evaluate

        Monitor effectiveness of controls.
        Calculate residual risk.
        """
        # Evaluate each control
        for control in self.controls:
            if control.implemented:
                control.evaluate("Effective")

        # Calculate residual risk (lowest of all residual risks)
        residual_risks = [c.residual_risk for c in self.controls if c.residual_risk]
        if residual_risks:
            risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]
            self.residual_risk = max(residual_risks, key=lambda r: risk_order.index(r))
        else:
            self.residual_risk = self.initial_risk

        return {
            "initial_risk": self.initial_risk.value if self.initial_risk else None,
            "residual_risk": self.residual_risk.value if self.residual_risk else None,
            "controls_implemented": sum(1 for c in self.controls if c.implemented),
            "controls_effective": sum(
                1 for c in self.controls if c.evaluation_result == "Effective"
            ),
            "consensus_threshold": CONSENSUS_THRESHOLDS.get(self.residual_risk, 0.60),
            "approval_authority": APPROVAL_AUTHORITY.get(self.residual_risk, "Commander"),
        }

    async def full_assessment(self, task: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Run complete 5-step CRM process.
        """
        await self.step1_identify_hazards(task, context)
        await self.step2_assess_hazards()
        await self.step3_develop_controls()
        await self.step4_implement_controls()
        result = await self.step5_supervise_evaluate()

        return {
            "session_id": self.session_id,
            "task": task,
            "hazards_identified": len(self.hazards),
            "controls_developed": len(self.controls),
            **result,
            "atp_reference": "ATP 5-19",
        }

    def get_consensus_threshold(self) -> float:
        """Get consensus threshold based on residual risk"""
        risk = self.residual_risk or self.initial_risk or RiskLevel.MEDIUM
        return CONSENSUS_THRESHOLDS.get(risk, 0.60)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "hazards": [h.to_dict() for h in self.hazards],
            "controls": [c.to_dict() for c in self.controls],
            "initial_risk": self.initial_risk.value if self.initial_risk else None,
            "residual_risk": self.residual_risk.value if self.residual_risk else None,
            "atp_reference": "ATP 5-19",
        }
