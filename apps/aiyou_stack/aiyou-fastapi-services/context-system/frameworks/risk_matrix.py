# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Decision Framework - ATP 5-19 Risk Assessment Matrix Integration
Military risk management adapted for business decisions
"""

from dataclasses import dataclass
from enum import Enum


class Probability(Enum):
    """Risk probability levels (ATP 5-19)"""

    A_FREQUENT = "A"  # Occurs very often, continuously experienced
    B_LIKELY = "B"  # Occurs several times
    C_OCCASIONAL = "C"  # Occurs sporadically
    D_SELDOM = "D"  # Remotely possible, could occur at some time
    E_UNLIKELY = "E"  # Can assume it will not occur


class Severity(Enum):
    """Impact severity levels (ATP 5-19)"""

    I_CATASTROPHIC = "I"  # Death, system loss, major property damage
    II_CRITICAL = "II"  # Severe injury/illness, major system damage
    III_MODERATE = "III"  # Minor injury/illness, minor system damage
    IV_NEGLIGIBLE = "IV"  # First aid, minimal threat to system


class RiskLevel(Enum):
    """Aggregated risk levels"""

    EH_EXTREMELY_HIGH = "EH"  # BLOCK (non-negotiable)
    H_HIGH = "H"  # CFO approval required
    M_MEDIUM = "M"  # Manager approval
    L_LOW = "L"  # ALLOW


# ATP 5-19 Risk Assessment Matrix
RISK_MATRIX: dict[tuple[str, str], str] = {
    # Probability A (Frequent)
    ("A", "I"): "EH",
    ("A", "II"): "EH",
    ("A", "III"): "H",
    ("A", "IV"): "M",
    # Probability B (Likely)
    ("B", "I"): "EH",
    ("B", "II"): "H",
    ("B", "III"): "H",
    ("B", "IV"): "M",
    # Probability C (Occasional)
    ("C", "I"): "H",
    ("C", "II"): "H",
    ("C", "III"): "M",
    ("C", "IV"): "L",
    # Probability D (Seldom)
    ("D", "I"): "H",
    ("D", "II"): "M",
    ("D", "III"): "M",
    ("D", "IV"): "L",
    # Probability E (Unlikely)
    ("E", "I"): "M",
    ("E", "II"): "M",
    ("E", "III"): "L",
    ("E", "IV"): "L",
}


ACTION_GATES: dict[str, str] = {
    "EH": "BLOCK - Non-negotiable. Do not proceed.",
    "H": "CFO/CEO approval required. Document justification.",
    "M": "Manager approval required. Standard process.",
    "L": "ALLOW - Proceed with standard monitoring.",
}


@dataclass
class RiskAssessment:
    """Risk assessment result"""

    probability: str
    severity: str
    risk_level: str
    action_gate: str
    justification: str
    mitigation: list[str]


class RiskMatrix:
    """ATP 5-19 Risk Assessment Matrix implementation"""

    @staticmethod
    def assess_risk(probability: str, severity: str) -> str:
        """Assess risk level based on probability and severity

        Args:
            probability: A-E (Frequent to Unlikely)
            severity: I-IV (Catastrophic to Negligible)

        Returns:
            Risk level: EH, H, M, or L

        """
        key = (probability.upper(), severity.upper())
        return RISK_MATRIX.get(key, "EH")  # Default to EH if invalid input

    @staticmethod
    def get_action_gate(risk_level: str) -> str:
        """Get required action for risk level"""
        return ACTION_GATES.get(risk_level.upper(), ACTION_GATES["EH"])

    @staticmethod
    def evaluate_decision(
        probability: str,
        severity: str,
        justification: str,
        mitigation: list[str],
    ) -> RiskAssessment:
        """Evaluate a business decision through risk matrix

        Returns comprehensive risk assessment with action gate
        """
        risk_level = RiskMatrix.assess_risk(probability, severity)
        action_gate = RiskMatrix.get_action_gate(risk_level)

        return RiskAssessment(
            probability=probability,
            severity=severity,
            risk_level=risk_level,
            action_gate=action_gate,
            justification=justification,
            mitigation=mitigation,
        )


@dataclass
class DecisionProtocol:
    """Purpose/Reason/Brakes decision framework"""

    purpose: str = "ShadowTag-v2JR mission alignment check"
    reason: str = "Doctrine compliance (SOPs A-D)"
    brakes: str = "Army RM risk assessment (ATP 5-19)"
    human_in_loop: list[str] = None

    def __post_init__(self):
        if self.human_in_loop is None:
            self.human_in_loop = [
                "High-risk actions (EH, H)",
                "Financial decisions >$50K",
                "Customer-facing edge cases",
                "Security vulnerabilities",
                "Regulatory compliance questions",
            ]


class FrameworkRegistry:
    """Registry of all operational frameworks"""

    FRAMEWORKS = {
        "sop_a": {
            "name": "Upload Triage",
            "benefit": "2× speed, −90% errors",
            "description": "Automated triage of incoming requests and data",
        },
        "sop_b": {
            "name": "Change & Release",
            "benefit": "2× cadence, clearer audits",
            "description": "Streamlined change management and deployment",
        },
        "sop_c": {
            "name": "Decision Protocol",
            "benefit": "2× faster, +1.8× robustness",
            "description": "Purpose/Reason/Brakes decision framework",
        },
        "sop_d": {
            "name": "Code Review",
            "benefit": "+2× defect capture",
            "description": "Rigorous code review process with automated checks",
        },
        "atp_5_19": {
            "name": "Risk Management (Military)",
            "benefit": "Probability × severity → action gates",
            "description": "Military-grade risk assessment framework",
        },
        "business_judgment_rule": {
            "name": "Defensible Decisions",
            "benefit": "Legal defensibility under uncertainty",
            "description": "Evidence-based decision making with documented rationale",
        },
        "boy_scout_rule": {
            "name": "Code Quality",
            "benefit": "Continuous improvement",
            "description": "Leave code cleaner than you found it",
        },
        "reality_distortion_field": {
            "name": "Innovation Catalyst",
            "benefit": "Breakthrough thinking",
            "description": "Treat impossibles as invitations to innovate",
        },
    }


def example_risk_assessments() -> list[dict]:
    """Example risk assessments for common business scenarios"""
    examples = [
        {
            "scenario": "Launch new vertical without pilot customers",
            "assessment": RiskMatrix.evaluate_decision(
                probability="B",  # Likely to fail without validation
                severity="II",  # Critical - wastes resources, damages reputation
                justification="No market validation, pure speculation",
                mitigation=[
                    "Require $5K+ pilot demand before launch",
                    "Interview n≥10 potential customers",
                    "Build MVP in 2 weeks, not 2 months",
                ],
            ),
        },
        {
            "scenario": "Deploy to production without SOC 2 compliance",
            "assessment": RiskMatrix.evaluate_decision(
                probability="A",  # Frequent - security issues common
                severity="I",  # Catastrophic - data breach, legal liability
                justification="Security absolute: 100% operational gate",
                mitigation=[
                    "BLOCK deployment until compliant",
                    "Implement GCP Secret Manager",
                    "Enable audit logging",
                    "MFA enforcement",
                ],
            ),
        },
        {
            "scenario": "Hire engineer before founder validates workflow",
            "assessment": RiskMatrix.evaluate_decision(
                probability="B",  # Likely - common startup mistake
                severity="III",  # Moderate - wasted salary, poor delegation
                justification="Premature scaling without process documentation",
                mitigation=[
                    "Founder does job 3+ months first",
                    "Document workflow in SOP",
                    "Create training materials",
                    "Then hire and delegate",
                ],
            ),
        },
        {
            "scenario": "Add feature based on one customer request",
            "assessment": RiskMatrix.evaluate_decision(
                probability="C",  # Occasional - feature bloat risk
                severity="IV",  # Negligible - can be removed later
                justification="Single data point, not pattern",
                mitigation=[
                    "Interview n≥10 users first",
                    "Validate demand with pilot pricing",
                    "Build as optional add-on, not core",
                    "Track adoption metrics",
                ],
            ),
        },
    ]

    return [
        {
            "scenario": ex["scenario"],
            "probability": ex["assessment"].probability,
            "severity": ex["assessment"].severity,
            "risk_level": ex["assessment"].risk_level,
            "action_gate": ex["assessment"].action_gate,
            "justification": ex["assessment"].justification,
            "mitigation": ex["assessment"].mitigation,
        }
        for ex in examples
    ]


def get_framework_config() -> dict:
    """Generate complete framework configuration"""
    protocol = DecisionProtocol()

    return {
        "decision_protocol": {
            "purpose": protocol.purpose,
            "reason": protocol.reason,
            "brakes": protocol.brakes,
            "human_in_loop": protocol.human_in_loop,
        },
        "risk_matrix": {
            "levels": {
                "EH": "Extremely High - BLOCK",
                "H": "High - CFO approval",
                "M": "Medium - Manager approval",
                "L": "Low - ALLOW",
            },
            "matrix": RISK_MATRIX,
        },
        "frameworks": FrameworkRegistry.FRAMEWORKS,
        "example_assessments": example_risk_assessments(),
    }


if __name__ == "__main__":
    import json

    config = get_framework_config()
    print(json.dumps(config, indent=2))
