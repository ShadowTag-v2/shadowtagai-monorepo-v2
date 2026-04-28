# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
LAWTRACK (LT): Live Rules Database + Dynamic Timelines

Rules DB → Timeline Engine → Configurable Enforcement + Mobile Critical Tiles

Value Proposition: Never miss a procedural step, ensure compliance

Revenue: Enterprise-focused (Government/LEO/Corporate)
Market: Restricted vertical (WCKD - Law Enforcement/Gov)
Structure: Separate from LegalTrack (different use case)

Key Differences from LegalTrack:
- LegalTrack: Court emails → calendar deadlines (lawyer tool)
- LawTrack: Jurisdiction rules → dynamic timelines → enforcement (compliance tool)
"""

__version__ = "1.0.0"

from .enforcement import (
    ComplianceCheck,
    EnforcementAction,
    EnforcementEngine,
)
from .rules_database import (
    JurisdictionRule,
    RulesDatabase,
    RuleType,
)
from .timeline_engine import (
    Timeline,
    TimelineEngine,
    TimelineEvent,
)

__all__ = [
    "RulesDatabase",
    "JurisdictionRule",
    "RuleType",
    "TimelineEngine",
    "TimelineEvent",
    "Timeline",
    "EnforcementEngine",
    "ComplianceCheck",
    "EnforcementAction",
]
