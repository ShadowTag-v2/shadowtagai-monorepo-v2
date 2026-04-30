"""Corp Engine Governance
=======================
JURA Protocol compliance integration.
"No Hot Water" principle - stay out of regulatory trouble.

Includes:
- JURA Compliance Integration
- EU AI Act Article 26
- California AI Minor Protection Act
- GDPR, CCPA, SOC 2, HIPAA, FedRAMP, CMMC, ITAR
"""

from .jura_compliance import (
    ComplianceLevel,
    ComplianceResult,
    JuraComplianceGate,
    jura_gate,
)
from .regulations.california_ai_minor import (
    CaliforniaAIMinorCompliance,
    MinorProtectionLevel,
    ca_minor_compliance,
)
from .regulations.eu_ai_act import (
    Article26Requirements,
    EUAIActCompliance,
    RiskClassification,
    eu_ai_compliance,
)

__all__ = [
    # JURA
    "JuraComplianceGate",
    "ComplianceResult",
    "ComplianceLevel",
    "jura_gate",
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
