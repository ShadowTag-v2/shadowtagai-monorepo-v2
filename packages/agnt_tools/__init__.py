# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Tools — Runtime configuration and speculation engine.

Ported from Claude Code's hidden ant-gated tools:
- ConfigTool → config_tool.py (runtime flag modification)
- Speculation Engine → speculation_engine.py (prompt pre-computation)
"""

from packages.agnt_tools.config_tool import ConfigTool
from packages.agnt_tools.speculation_engine import PromptSpeculationEngine

__all__ = ["ConfigTool", "PromptSpeculationEngine"]
