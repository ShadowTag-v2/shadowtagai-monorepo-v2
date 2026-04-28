# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prompts package for n-autoresearch/Kosmos/BioAgents Cavalry Squadron.
Contains Antigravity system prompt and battle drills.
"""

from .antigravity_system import (
    ANTIGRAVITY_COMPACT_PROMPT,
    ANTIGRAVITY_SYSTEM_PROMPT,
    TROOP_SPECIALIZATIONS,
    build_prompt,
    build_task_prompt,
)
from .battle_drills import (
    BATTLE_DRILLS,
    BattleDrill,
    DrillDefinition,
    get_drill_for_mission,
    get_drill_phases,
    get_drill_tasks_for_troop,
)

__all__ = [
    # Antigravity
    "build_prompt",
    "build_task_prompt",
    "ANTIGRAVITY_SYSTEM_PROMPT",
    "ANTIGRAVITY_COMPACT_PROMPT",
    "TROOP_SPECIALIZATIONS",
    # Battle Drills
    "BattleDrill",
    "DrillDefinition",
    "BATTLE_DRILLS",
    "get_drill_for_mission",
    "get_drill_tasks_for_troop",
    "get_drill_phases",
]
