# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Recovery — Conversation state restoration with interruption detection.

Synthesized from Claude Code v2.1.91 production patterns:
  - conversationRecovery.ts: deserializeMessages, detectTurnInterruption
  - conversationRecovery.ts L77-132: migrateLegacyAttachmentTypes
  - conversationRecovery.ts L164-252: deserializeMessagesWithInterruptDetection
  - conversationRecovery.ts L272-333: detectTurnInterruption state machine
  - conversationRecovery.ts L348-373: isTerminalToolResult (brief mode)
  - conversationRecovery.ts L382-400: restoreSkillStateFromMessages

Adds typed Python dataclasses, pipeline-based message filtering, and
proper state machine for turn interruption detection that CC handles
inline.

Usage:
    from session_recovery import (
        SessionRecovery, TurnInterruptionState, DeserializeResult,
    )

    recovery = SessionRecovery()
    result = recovery.deserialize_messages(serialized_messages)
    if result.interruption_state.kind == "interrupted_prompt":
        # Auto-continue the interrupted prompt
        pass
"""

from session_recovery.core import (
  DeserializeResult,
  MessageFilter,
  SessionRecovery,
  TurnInterruptionState,
)

__all__ = [
  "DeserializeResult",
  "MessageFilter",
  "SessionRecovery",
  "TurnInterruptionState",
]
