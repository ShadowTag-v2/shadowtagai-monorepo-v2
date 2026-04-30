# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context compactor package — 4-layer compaction pipeline with microcompaction.

Public API:
  - ContextCompactor: Main orchestrator (L1→L4 pipeline)
  - microcompact_messages: Pre-request microcompaction entry point
  - group_messages_by_api_round: API-round message grouping
  - estimate_message_tokens: Conservative token estimation
  - TimeBasedMCConfig: Time-based MC configuration
"""

from context_compactor.grouping import group_messages_by_api_round
from context_compactor.micro_compact import (
    COMPACTABLE_TOOLS,
    TIME_BASED_MC_CLEARED_MESSAGE,
    MicrocompactResult,
    TimeBasedMCConfig,
    estimate_message_tokens,
    microcompact_messages,
)

__all__ = [
    "COMPACTABLE_TOOLS",
    "MicrocompactResult",
    "TIME_BASED_MC_CLEARED_MESSAGE",
    "TimeBasedMCConfig",
    "estimate_message_tokens",
    "group_messages_by_api_round",
    "microcompact_messages",
]
