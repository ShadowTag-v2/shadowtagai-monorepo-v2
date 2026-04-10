"""
Decision Framework & Risk Assessment
ATP 5-19 Military Risk Management + Business Kill-Switches
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Probability(Enum):
    """Risk probability levels (ATP 5-19)"""

    A_FREQUENT = "A_frequent"
    B_LIKELY = "B_likely"
    C_OCCASIONAL = "C_occasional"
    D_SELDOM = "D_seldom"
    E_UNLIKELY = "E_unlikely"


class Severity(Enum):
    """Risk severity levels (ATP 5-19)"""

    I_CATASTROPHIC = "I_catastrophic"
    II_CRITICAL = "II_critical"
    III_MODERATE = "III_moderate"
    IV_NEGLIGIBLE = "IV_negligible"


class RiskLevel(Enum):
    """Composite risk assessment"""

    EH_EXTREMELY_HIGH = "EH_extremely_high"
    H_HIGH = "H_high"
    M_MEDIUM = "M_medium"
    L_LOW = "L_low"


@dataclass
class RiskAssessment:
    """ATP 5-19 Risk Matrix Implementation"""

    # Risk matrix mapping: (Probability, Severity) -> RiskLevel
    RISK_MATRIX: dict[tuple[str, str], RiskLevel] = None

    def __post_init__(self):
        """Initialize risk matrix"""
        if self.RISK_MATRIX is None:
            self.RISK_MATRIX = {
                ("A", "I"): RiskLevel.EH_EXTREMELY_HIGH,
                ("A", "II"): RiskLevel.H_HIGH,
                ("A", "III"): RiskLevel.H_HIGH,
                ("A", "IV"): RiskLevel.M_MEDIUM,
                ("B", "I"): RiskLevel.EH_EXTREMELY_HIGH,
                ("B", "II"): RiskLevel.H_HIGH,
                ("B", "III"): RiskLevel.M_MEDIUM,
                ("B", "IV"): RiskLevel.L_LOW,
                ("C", "I"): RiskLevel.H_HIGH,
                ("C", "II"): RiskLevel.H_HIGH,
                ("C", "III"): RiskLevel.M_MEDIUM,
                ("C", "IV"): RiskLevel.L_LOW,
                ("D", "I"): RiskLevel.M_MEDIUM,
                ("D", "II"): RiskLevel.M_MEDIUM,
                ("D", "III"): RiskLevel.L_LOW,
                ("D", "IV"): RiskLevel.L_LOW,
                ("E", "I"): RiskLevel.M_MEDIUM,
                ("E", "II"): RiskLevel.L_LOW,
                ("E", "III"): RiskLevel.L_LOW,
                ("E", "IV"): RiskLevel.L_LOW,
            }

    def assess(self, prob: str, sev: str) -> RiskLevel:
        """Calculate risk level"""
        return self.RISK_MATRIX.get((prob, sev), RiskLevel.M_MEDIUM)

    def get_action_gate(self, risk: RiskLevel) -> str:
        """Determine required approval"""
        gates = {
            RiskLevel.EH_EXTREMELY_HIGH: "BLOCK (non-negotiable)",
            RiskLevel.H_HIGH: "CFO_approval_required",
            RiskLevel.M_MEDIUM: "Manager_approval",
            RiskLevel.L_LOW: "ALLOW",
        }
        return gates[risk]


@dataclass
class DecisionProtocol:
    """Purpose/Reason/Brakes validation framework"""

    purpose: str = "ShadowTag-v2JR mission alignment check"
    reason: str = "Doctrine compliance (SOPs A-D)"
    brakes: str = "Army RM risk assessment (ATP 5-19)"
    human_in_loop: list[str] = None

    def __post_init__(self):
        if self.human_in_loop is None:
            self.human_in_loop = [
                "High-risk actions",
                "Financial >$50K",
                "Customer-facing edge cases",
            ]

    def validate_decision(self, action: str, risk_level: RiskLevel) -> bool:
        """Validate if action can proceed"""
        if risk_level == RiskLevel.EH_EXTREMELY_HIGH:
            return False
        if risk_level == RiskLevel.H_HIGH:
            # Requires human approval
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "purpose": self.purpose,
            "reason": self.reason,
            "brakes": self.brakes,
            "human_in_loop": self.human_in_loop,
        }


@dataclass
class KillSwitch:
    """Single kill-switch criterion"""

    phase: str
    condition: str
    action: str
    month: int


class KillSwitches:
    """Business viability gates with evidence-based shutdown criteria"""

    SWITCHES: list[KillSwitch] = [
        KillSwitch(
            phase="Month 3 Pilot Validation",
            condition="pilots < 5 OR mrr < 10_000",
            action="Pivot vertical or shut down",
            month=3,
        ),
        KillSwitch(
            phase="Month 6 Product-Market Fit",
            condition="mrr < 35_000",
            action="Reassess pricing/ICP",
            month=6,
        ),
        KillSwitch(
            phase="Month 12 Scale Gate",
            condition="mrr < 100_000 OR ltv_cac < 4.0",
            action="Scale or sell",
            month=12,
        ),
        KillSwitch(
            phase="Vertical Health Check",
            condition="vertical_mrr < 10_000 (90 days post-launch)",
            action="Kill vertical (no sunk cost fallacy)",
            month=0,  # Rolling check
        ),
    ]

    @classmethod
    def evaluate(
        cls, month: int, mrr: int, pilots: int = 0, ltv_cac: float = 0.0
    ) -> tuple[bool, str]:
        """
        Evaluate if kill-switch triggered
        Returns: (should_kill, reason)
        """
        if month == 3 and (pilots < 5 or mrr < 10_000):
            return (True, "Month 3: Insufficient pilots or MRR")

        if month == 6 and mrr < 35_000:
            return (True, "Month 6: Failed PMF threshold")

        if month >= 12 and (mrr < 100_000 or ltv_cac < 4.0):
            return (True, "Month 12: Scale gate failed")

        return (False, "All gates passing")

    @classmethod
    def to_dict(cls) -> list[dict[str, Any]]:
        return [
            {"phase": s.phase, "condition": s.condition, "action": s.action, "month": s.month}
            for s in cls.SWITCHES
        ]


# Singleton instances
RISK_ASSESSMENT = RiskAssessment()
DECISION_PROTOCOL = DecisionProtocol()
