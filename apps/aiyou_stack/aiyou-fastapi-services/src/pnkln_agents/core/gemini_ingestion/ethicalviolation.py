from dataclasses import dataclass
from datetime import datetime

from .ethicalviolationtype import EthicalViolationType


@dataclass
class EthicalViolation:
    """Represents an ethical compliance violation"""

    violation_type: EthicalViolationType
    source: str
    description: str
    severity: str
    timestamp: datetime
    remediation: str
