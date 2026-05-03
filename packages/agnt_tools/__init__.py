# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Tools — Runtime configuration and speculation engine.

Ported from Claude Code's hidden ant-gated tools:
- ConfigTool → config_tool.py (runtime flag modification)
- Speculation Engine → MIGRATED to packages/speculation_engine/ (v14.0)

Migration guide:
  OLD: from packages.agnt_tools.speculation_engine import PromptSpeculationEngine
  NEW: from speculation_engine import SpeculationEngine, SuggestionManager
"""

from packages.agnt_tools.config_tool import ConfigTool

__all__ = ["ConfigTool"]
