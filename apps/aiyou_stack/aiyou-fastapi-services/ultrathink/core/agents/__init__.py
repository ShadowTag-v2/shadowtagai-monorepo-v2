# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Multi-agent systems: MAD, PanelGPT, AgentCoder, DTE.

When multiple perspectives beat single-model responses.
"""

from ultrathink.core.agents.agent_coder import AgentCoder
from ultrathink.core.agents.mad import MultiAgentDebate
from ultrathink.core.agents.panel_gpt import PanelGPT

__all__ = ["AgentCoder", "MultiAgentDebate", "PanelGPT"]
