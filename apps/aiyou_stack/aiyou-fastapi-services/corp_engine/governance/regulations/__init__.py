"""Corp Engine Governance Regulations
===================================
Specific regulatory compliance modules.
"""

from .california_ai_minor import (
    CaliforniaAIMinorCompliance,
    MinorProtectionLevel,
    ca_minor_compliance,
)
from .eu_ai_act import (
    Article26Requirements,
    EUAIActCompliance,
    RiskClassification,
    eu_ai_compliance,
)

__all__ = [
    # EU AI Act
    "EUAIActCompliance",
    "Article26Requirements",
    "RiskClassification",
    "eu_ai_compliance",
    # California AI Minor
    "CaliforniaAIMinorCompliance",
    "MinorProtectionLevel",
    "ca_minor_compliance",
]
