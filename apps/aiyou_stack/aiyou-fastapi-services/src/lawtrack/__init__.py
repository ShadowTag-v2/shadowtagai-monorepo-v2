"""
LAWTRACK (LT): Live Rules Database + Dynamic Timelines

Rules DB → Timeline Engine → Configurable Enforcement + Mobile Critical Tiles

Value Proposition: Never miss a procedural step, ensure compliance
Revenue: Enterprise-focused (Government/LEO/Corporate)
Market: Restricted vertical (WCKD - Law Enforcement/Gov)
Structure: Separate from LegalTrack (different use case)
"""

__version__ = "1.0.0"

from .enforcement import (
    ComplianceCheck,
    EnforcementEngine,
    EnforcementLevel,
)
from .rules_database import (
    Jurisdiction,
    Rule,
    RulesDatabase,
)
from .timeline_engine import (
    Timeline,
    TimelineEngine,
    TimelineEvent,
)
