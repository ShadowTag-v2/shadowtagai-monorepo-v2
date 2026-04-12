"""
Kosmos - Army Doctrine-Aligned Multi-Agent AI Framework
========================================================

Implements ATP 3-20.96 Cavalry Squadron structure (430 agents) with
full Army doctrine integration:

- ADP 6-22: Leadership attributes & competencies
- FM 6-0: MDMP/TLP planning processes
- ATP 5-19: Composite Risk Management
- FM 3-0: Warfighting functions
- FM 7-8: Battle drills

Total: 5,590 agents (13 Kosmos × 430 agents)
"""

from .doctrine import (
    LDRSHIP_VALUES,
    # ADP 6-22 Leadership
    AgentAttributes,
    # FM 7-8 Battle Drills
    BattleDrill,
    BreakContact,
    CommandControl,
    Fires,
    Intelligence,
    LeaderCompetencies,
    # FM 6-0 Command & Staff
    MDMPPipeline,
    Movement,
    Protection,
    ReactToContact,
    RiskLevel,
    # ATP 5-19 Risk Management
    RiskManager,
    RiskMatrix,
    StaffSection,
    Sustainment,
    TLPPipeline,
    # FM 3-0 Warfighting Functions
    WarfightingFunction,
)

__all__ = [
    # ADP 6-22
    "AgentAttributes",
    "LeaderCompetencies",
    "LDRSHIP_VALUES",
    # FM 6-0
    "MDMPPipeline",
    "TLPPipeline",
    "StaffSection",
    # ATP 5-19
    "RiskManager",
    "RiskLevel",
    "RiskMatrix",
    # FM 3-0
    "WarfightingFunction",
    "CommandControl",
    "Intelligence",
    "Fires",
    "Movement",
    "Sustainment",
    "Protection",
    # FM 7-8
    "BattleDrill",
    "ReactToContact",
    "BreakContact",
]

__version__ = "1.0.0"
