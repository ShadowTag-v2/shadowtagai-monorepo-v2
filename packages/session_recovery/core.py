# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Recovery — Core implementation.

Ported from Claude Code v2.1.91 conversationRecovery.ts:
  - deserializeMessages: Message deserialization pipeline
  - detectTurnInterruption: State machine for detecting interrupted turns
  - migrateLegacyAttachmentTypes: Attachment type normalization
  - isTerminalToolResult: Brief mode detection
  - restoreSkillStateFromMessages: Skill state restoration

All network I/O is stripped. This is a pure data-transform pipeline.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class InterruptionKind(str, Enum):
    """Type of turn interruption detected."""

    NONE = "none"
    INTERRUPTED_PROMPT = "interrupted_prompt"
    INTERRUPTED_TOOL = "interrupted_tool"
    CRASHED = "crashed"


@dataclass(frozen=True, slots=True)
class TurnInterruptionState:
    """Result of turn interruption detection."""

    kind: InterruptionKind = InterruptionKind.NONE
    interrupted_tool_name: str | None = None
    last_assistant_message_index: int = -1

    @property
    def is_interrupted(self) -> bool:
        return self.kind != InterruptionKind.NONE


class MessageRole(str, Enum):
    """Message role enum."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """Deserialized conversation message."""

    role: MessageRole
    content: str
    tool_use_id: str | None = None
    tool_name: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def is_tool_use(self) -> bool:
        return self.tool_use_id is not None

    @property
    def is_terminal_tool_result(self) -> bool:
        """Check if this is a terminal tool result (brief mode)."""
        if self.role != MessageRole.TOOL:
            return False
        return self.metadata.get("is_terminal", False)


@dataclass(frozen=True, slots=True)
class DeserializeResult:
    """Result of message deserialization."""

    messages: list[Message]
    interruption_state: TurnInterruptionState
    migrated_count: int = 0
    filtered_count: int = 0
    duration_ms: float = 0.0


class MessageFilter:
    """Pipeline-based message filtering.

    Filters are applied in order. Each filter receives the full message
    list and returns a filtered subset.
    """

    def __init__(self) -> None:
        self._filters: list[tuple[str, callable]] = []

    def add_filter(self, name: str, fn: callable) -> MessageFilter:
        """Add a named filter function. Returns self for chaining."""
        self._filters.append((name, fn))
        return self

    def apply(self, messages: list[Message]) -> tuple[list[Message], int]:
        """Apply all filters in order. Returns (filtered_messages, removed_count)."""
        original_count = len(messages)
        current = messages

        for name, fn in self._filters:
            try:
                current = fn(current)
            except (TypeError, ValueError) as e:
                logger.warning("Filter '%s' failed: %s — skipping", name, e)

        return current, original_count - len(current)


class SessionRecovery:
    """Core session recovery orchestrator.

    Handles deserialization, interruption detection, and state restoration.
    """

    def __init__(self, max_messages: int = 10000) -> None:
        self._max_messages = max_messages
        self._filter = MessageFilter()
        self._setup_default_filters()

    def _setup_default_filters(self) -> None:
        """Register default message filters."""
        self._filter.add_filter(
            "remove_empty",
            lambda msgs: [m for m in msgs if m.content.strip()],
        )
        self._filter.add_filter(
            "cap_max",
            lambda msgs: msgs[-self._max_messages :],
        )

    def deserialize_messages(self, serialized: list[dict] | str) -> DeserializeResult:
        """Deserialize and recover messages from storage.

        Args:
            serialized: JSON string or list of message dicts.

        Returns:
            DeserializeResult with parsed messages and interruption state.
        """
        start = time.monotonic()

        # Parse JSON if string
        if isinstance(serialized, str):
            try:
                raw_messages = json.loads(serialized)
            except json.JSONDecodeError:
                logger.error("Failed to parse serialized messages")
                return DeserializeResult(
                    messages=[],
                    interruption_state=TurnInterruptionState(),
                    duration_ms=(time.monotonic() - start) * 1000,
                )
        else:
            raw_messages = serialized

        # Deserialize
        messages, migrated = self._deserialize_raw(raw_messages)

        # Apply filters
        messages, filtered = self._filter.apply(messages)

        # Detect interruption
        interruption = self._detect_turn_interruption(messages)

        duration = (time.monotonic() - start) * 1000

        return DeserializeResult(
            messages=messages,
            interruption_state=interruption,
            migrated_count=migrated,
            filtered_count=filtered,
            duration_ms=duration,
        )

    def _deserialize_raw(self, raw: list[dict]) -> tuple[list[Message], int]:
        """Convert raw dicts to Message objects with legacy migration."""
        messages = []
        migrated = 0

        for item in raw:
            if not isinstance(item, dict):
                continue

            role_str = item.get("role", "user")
            try:
                role = MessageRole(role_str)
            except ValueError:
                role = MessageRole.USER
                migrated += 1

            content = item.get("content", "")
            if not isinstance(content, str):
                content = str(content)

            # Migrate legacy attachment types
            metadata = item.get("metadata", {})
            if "attachment_type" in metadata:
                old_type = metadata["attachment_type"]
                new_type = self._migrate_attachment_type(old_type)
                if new_type != old_type:
                    metadata["attachment_type"] = new_type
                    migrated += 1

            msg = Message(
                role=role,
                content=content,
                tool_use_id=item.get("tool_use_id"),
                tool_name=item.get("tool_name"),
                timestamp=item.get("timestamp", time.time()),
                metadata=metadata,
            )
            messages.append(msg)

        return messages, migrated

    @staticmethod
    def _migrate_attachment_type(attachment_type: str) -> str:
        """Migrate legacy attachment type names to current format."""
        migrations = {
            "file_content": "file",
            "image_url": "image",
            "code_block": "code",
            "terminal_output": "terminal",
        }
        return migrations.get(attachment_type, attachment_type)

    @staticmethod
    def _detect_turn_interruption(
        messages: list[Message],
    ) -> TurnInterruptionState:
        """State machine for detecting interrupted turns.

        Scans messages in reverse to find the last assistant turn
        and determines if it was interrupted mid-response.
        """
        if not messages:
            return TurnInterruptionState()

        last_assistant_idx = -1
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == MessageRole.ASSISTANT:
                last_assistant_idx = i
                break

        if last_assistant_idx == -1:
            return TurnInterruptionState()

        last_msg = messages[last_assistant_idx]

        # Check if assistant was using a tool and never got the result
        if last_msg.is_tool_use:
            # Look for corresponding tool result after this message
            has_result = any(m.role == MessageRole.TOOL and m.tool_use_id == last_msg.tool_use_id for m in messages[last_assistant_idx + 1 :])
            if not has_result:
                return TurnInterruptionState(
                    kind=InterruptionKind.INTERRUPTED_TOOL,
                    interrupted_tool_name=last_msg.tool_name,
                    last_assistant_message_index=last_assistant_idx,
                )

        # Check if the last message is from assistant (no user follow-up)
        if last_assistant_idx == len(messages) - 1:
            # Could be a crash or normal end — check for truncation markers
            if last_msg.metadata.get("truncated", False):
                return TurnInterruptionState(
                    kind=InterruptionKind.CRASHED,
                    last_assistant_message_index=last_assistant_idx,
                )
            return TurnInterruptionState(
                kind=InterruptionKind.INTERRUPTED_PROMPT,
                last_assistant_message_index=last_assistant_idx,
            )

        return TurnInterruptionState(
            last_assistant_message_index=last_assistant_idx,
        )

    def restore_skill_state(self, messages: list[Message]) -> dict[str, dict]:
        """Extract and restore skill state from message history.

        Scans messages for skill activation/deactivation markers and
        reconstructs the current skill state.
        """
        skill_state: dict[str, dict] = {}

        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                continue
            skill_meta = msg.metadata.get("skill_state")
            if skill_meta and isinstance(skill_meta, dict):
                skill_name = skill_meta.get("name", "")
                if skill_name:
                    skill_state[skill_name] = skill_meta

        return skill_state
