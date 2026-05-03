# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Tools — Runtime configuration, reasoning, and planning instruments.

Ported from Claude Code's hidden ant-gated tools:
- ConfigTool → config_tool.py (runtime flag modification)
- ThinkTool → think_tool.py (scratchpad reasoning, +54% tau-bench accuracy)
- ArchitectTool → architect_tool.py (read-only architectural analysis)
- PlanModeTools → plan_mode_tools.py (enter/exit plan mode transitions)
- Speculation Engine → MIGRATED to packages/speculation_engine/ (v14.0)

Migration guide:
  OLD: from packages.agnt_tools.speculation_engine import PromptSpeculationEngine
  NEW: from speculation_engine import SpeculationEngine, SuggestionManager
"""

from packages.agnt_tools.architect_tool import create_architect_tool
from packages.agnt_tools.config_tool import ConfigTool
from packages.agnt_tools.plan_mode_tools import (
    create_enter_plan_mode_tool,
    create_exit_plan_mode_tool,
)
from packages.agnt_tools.think_tool import create_think_tool

__all__ = [
    "ConfigTool",
    "create_architect_tool",
    "create_enter_plan_mode_tool",
    "create_exit_plan_mode_tool",
    "create_think_tool",
]
