# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LAWTRACK (LT): Live Rules Database + Dynamic Timelines

Rules DB → Timeline Engine → Configurable Enforcement + Mobile Critical Tiles

Value Proposition: Never miss a procedural step, ensure compliance
Revenue: Enterprise-focused (Government/LEO/Corporate)
Market: Restricted vertical (WCKD - Law Enforcement/Gov)
Structure: Separate from LegalTrack (different use case)
"""

__version__ = "1.0.0"

from .enforcement import (
    ComplianceCheck,  # noqa: F401
    EnforcementEngine,  # noqa: F401
    EnforcementLevel,  # noqa: F401
)
from .rules_database import (
    Jurisdiction,  # noqa: F401
    Rule,  # noqa: F401
    RulesDatabase,  # noqa: F401
)
from .timeline_engine import (
    Timeline,  # noqa: F401
    TimelineEngine,  # noqa: F401
    TimelineEvent,  # noqa: F401
)
