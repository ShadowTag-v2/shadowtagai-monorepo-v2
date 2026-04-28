# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass


@dataclass
class DebateRound:
    """Single round of multi-agent debate"""

    round_number: int
    agents: list[str]
    proposals: list[str]
    critiques: list[str]
    synthesis: str
    consensus_score: float
