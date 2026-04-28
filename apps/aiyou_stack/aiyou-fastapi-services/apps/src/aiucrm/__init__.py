# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AiUCRM - AI Unified Compliance & Risk Management
Adapted from U.S. Military Composite Risk Management System

Pre-execution governance framework for all AI operations.
Ensures legal, ethical, and operational compliance before inference.
"""

from .audit import AuditLogger, ComplianceReport
from .core import AiUCRM, ComplianceStatus, RiskLevel
from .validators import (
    DataSovereigntyValidator,
    EthicalValidator,
    LegalComplianceValidator,
    OperationalSafetyValidator,
)

__version__ = "1.0.0"
__all__ = [
    "AiUCRM",
    "AuditLogger",
    "ComplianceReport",
    "ComplianceStatus",
    "DataSovereigntyValidator",
    "EthicalValidator",
    "LegalComplianceValidator",
    "OperationalSafetyValidator",
    "RiskLevel",
]
