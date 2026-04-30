"""Live Rules Database for LawTrack

Jurisdiction-specific procedural rules with:
- Real-time updates (when rules change)
- Version control (historical rules)
- Structured format (machine-readable)

Coverage:
- Federal Rules of Civil/Criminal Procedure
- State rules (50 states)
- Local court rules (districts)
- Specialized rules (bankruptcy, immigration, etc.)
"""

from dataclasses import dataclass
from enum import Enum


class Jurisdiction(Enum):
    FEDERAL = "federal"
    STATE_CA = "state_ca"
    STATE_NY = "state_ny"
    STATE_TX = "state_tx"


@dataclass
class Rule:
    id: str
    jurisdiction: Jurisdiction
    code: str
    description: str
    days: int
    trigger_event: str


class RulesDatabase:
    """Live rules database"""

    def get_rules(self, jurisdiction: Jurisdiction) -> list[Rule]:
        # Mock rules
        return [
            Rule("r1", jurisdiction, "FRCP 12(a)", "Answer to Complaint", 21, "Service of Summons"),
        ]
