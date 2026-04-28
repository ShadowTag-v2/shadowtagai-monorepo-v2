# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Kosmos Doctrine Module - Army FM/ATP/ADP Integration
=====================================================

Integrates complete Army leadership and command doctrine:

1. ADP 6-22: Army Leadership and the Profession
2. FM 6-0: Commander and Staff Organization and Operations
3. ATP 5-19: Composite Risk Management
4. FM 3-0: Operations (Warfighting Functions)
5. FM 7-8: Infantry Rifle Platoon and Squad (Battle Drills)
"""

from .adp_6_22 import (
    LDRSHIP_VALUES,
    AgentAttributes,
    CharacterAttribute,
    IntellectAttribute,
    LeaderCompetencies,
    PresenceAttribute,
)
from .atp_5_19 import (
    Control,
    Hazard,
    Probability,
    RiskLevel,
    RiskManager,
    RiskMatrix,
    Severity,
)
from .battle_drills import (
    BattleDrill,
    BreakContact,
    EnterClearRoom,
    KnockOutBunker,
    ReactToAmbush,
    ReactToContact,
    ReactToIED,
)
from .fm_3_0 import (
    CommandControl,
    Fires,
    Intelligence,
    Movement,
    Protection,
    Sustainment,
    WarfightingFunction,
)
from .fm_6_0 import (
    MDMPPipeline,
    MDMPStep,
    StaffSection,
    StaffSectionType,
    TLPPipeline,
    TLPStep,
)

__all__ = [
    # ADP 6-22
    "AgentAttributes",
    "LeaderCompetencies",
    "CharacterAttribute",
    "PresenceAttribute",
    "IntellectAttribute",
    "LDRSHIP_VALUES",
    # FM 6-0
    "MDMPPipeline",
    "TLPPipeline",
    "StaffSection",
    "StaffSectionType",
    "MDMPStep",
    "TLPStep",
    # ATP 5-19
    "RiskManager",
    "RiskLevel",
    "RiskMatrix",
    "Hazard",
    "Control",
    "Probability",
    "Severity",
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
    "ReactToAmbush",
    "ReactToIED",
    "KnockOutBunker",
    "EnterClearRoom",
]
