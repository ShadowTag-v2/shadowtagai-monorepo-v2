import re
from enum import Enum
from typing import Any


class Severity(Enum):
    CATASTROPHIC = "I"
    CRITICAL = "II"
    MODERATE = "III"
    NEGLIGIBLE = "IV"


class Probability(Enum):
    FREQUENT = "A"
    LIKELY = "B"
    OCCASIONAL = "C"
    SELDOM = "D"
    UNLIKELY = "E"


class RiskLevel(Enum):
    EXTREMELY_HIGH = "E"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


class RiskAssessmentMatrix:
    """US Army ATP 5-19 Risk Assessment Matrix Implementation."""

    _matrix = {
        (Severity.CATASTROPHIC, Probability.FREQUENT): RiskLevel.EXTREMELY_HIGH,
        (Severity.CATASTROPHIC, Probability.LIKELY): RiskLevel.EXTREMELY_HIGH,
        (Severity.CATASTROPHIC, Probability.OCCASIONAL): RiskLevel.EXTREMELY_HIGH,
        (Severity.CATASTROPHIC, Probability.SELDOM): RiskLevel.HIGH,
        (Severity.CATASTROPHIC, Probability.UNLIKELY): RiskLevel.MEDIUM,
        (Severity.CRITICAL, Probability.FREQUENT): RiskLevel.EXTREMELY_HIGH,
        (Severity.CRITICAL, Probability.LIKELY): RiskLevel.HIGH,
        (Severity.CRITICAL, Probability.OCCASIONAL): RiskLevel.HIGH,
        (Severity.CRITICAL, Probability.SELDOM): RiskLevel.MEDIUM,
        (Severity.CRITICAL, Probability.UNLIKELY): RiskLevel.LOW,
        (Severity.MODERATE, Probability.FREQUENT): RiskLevel.HIGH,
        (Severity.MODERATE, Probability.LIKELY): RiskLevel.MEDIUM,
        (Severity.MODERATE, Probability.OCCASIONAL): RiskLevel.MEDIUM,
        (Severity.MODERATE, Probability.SELDOM): RiskLevel.LOW,
        (Severity.MODERATE, Probability.UNLIKELY): RiskLevel.LOW,
        (Severity.NEGLIGIBLE, Probability.FREQUENT): RiskLevel.MEDIUM,
        (Severity.NEGLIGIBLE, Probability.LIKELY): RiskLevel.LOW,
        (Severity.NEGLIGIBLE, Probability.OCCASIONAL): RiskLevel.LOW,
        (Severity.NEGLIGIBLE, Probability.SELDOM): RiskLevel.LOW,
        (Severity.NEGLIGIBLE, Probability.UNLIKELY): RiskLevel.LOW,
    }

    @classmethod
    def assess(cls, severity: Severity, probability: Probability) -> RiskLevel:
        return cls._matrix.get((severity, probability), RiskLevel.HIGH)  # Default to HIGH on error


class JudgeSentinel:
    """Judge 6 Implementation: Enforces Risk Gates."""

    def vet_code(self, code: str) -> dict[str, Any]:
        """Analyzes code for risks and assigns a Risk Level."""
        hazards = []

        # Hazard 1: Private Keys (Severity: I, Probability: A) -> E (Extremely High)
        if re.search(r"BEGIN PRIVATE KEY", code):
            hazards.append(
                {
                    "hazard": "Private Key Exposed",
                    "risk": RiskAssessmentMatrix.assess(
                        Severity.CATASTROPHIC,
                        Probability.FREQUENT,
                    ).value,
                },
            )

        # Hazard 2: Low Entropy Keys (Severity: II, Probability: B) -> H (High)
        if re.search(r"(api_key|token)\s*=\s*['\"]sk-", code):
            hazards.append(
                {
                    "hazard": "Hardcoded API Token",
                    "risk": RiskAssessmentMatrix.assess(
                        Severity.CRITICAL,
                        Probability.LIKELY,
                    ).value,
                },
            )

        # Decision Logic
        if not hazards:
            return {"approved": True, "risk_level": RiskLevel.LOW.value}

        highest_risk = max([h["risk"] for h in hazards], default="L")
        return {"approved": False, "risk_level": highest_risk, "hazards": hazards}


judge_6 = JudgeSentinel()
