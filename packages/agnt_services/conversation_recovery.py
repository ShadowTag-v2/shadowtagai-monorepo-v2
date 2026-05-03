# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Conversation Recovery — Session resilience and message deserialization.

Ported from src/utils/conversationRecovery.ts (598 lines).

Provides machinery for resuming interrupted conversations by:
  - Deserializing persisted message logs
  - Detecting turn interruptions (interrupted_prompt, interrupted_turn)
  - Migrating legacy attachment types (new_file → file, new_directory → directory)
  - Filtering orphaned thinking-only assistant messages
  - Filtering unresolved tool uses
  - Filtering whitespace-only assistant messages
  - Restoring invoked skill state from attachment messages
  - Loading conversation chains from JSONL transcript files
  - Appending synthetic continuation messages for interrupted turns

The pipeline mirrors the upstream TypeScript exactly:
  migrate → validate_permissions → filter_tool_uses → filter_thinking →
  filter_whitespace → detect_interruption → append_sentinel → return
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

# --- Permission modes (mirrors types/permissions.ts PERMISSION_MODES) ---
PERMISSION_MODES: frozenset[str] = frozenset(
    {
        "default",
        "plan",
        "bypassPermissions",
    }
)

# Terminal tool names that legitimately end a turn (brief mode).
# In the upstream these are conditionally imported via bun:bundle feature().
# We use sentinel strings that match the tool prompt exports.
BRIEF_TOOL_NAME: str | None = "brief"
LEGACY_BRIEF_TOOL_NAME: str | None = "legacyBrief"
SEND_USER_FILE_TOOL_NAME: str | None = "sendUserFile"

NO_RESPONSE_REQUESTED = "[no response requested]"


# ─── Data Types ────────────────────────────────────────────────────────

Message = dict[str, Any]
NormalizedMessage = dict[str, Any]
NormalizedUserMessage = dict[str, Any]

TurnInterruptionKind = Literal["none", "interrupted_prompt", "interrupted_turn"]


@dataclass(slots=True)
class TurnInterruptionState:
    """Represents the state of turn interruption detection."""

    kind: TurnInterruptionKind = "none"
    message: NormalizedUserMessage | None = None


@dataclass(slots=True)
class DeserializeResult:
    """Result from message deserialization with interruption detection."""

    messages: list[Message] = field(default_factory=list)
    turn_interruption_state: TurnInterruptionState = field(
        default_factory=TurnInterruptionState,
    )


@dataclass(slots=True)
class SessionMetadata:
    """Session metadata for restoring agent context on resume."""

    agent_name: str | None = None
    agent_color: str | None = None
    agent_setting: str | None = None
    custom_title: str | None = None
    tag: str | None = None
    mode: str | None = None  # "coordinator" | "normal"
    worktree_session: dict[str, Any] | None = None
    pr_number: int | None = None
    pr_url: str | None = None
    pr_repository: str | None = None
    full_path: str | None = None


@dataclass(slots=True)
class ResumeResult:
    """Full result from loading a conversation for resume."""

    messages: list[Message]
    turn_interruption_state: TurnInterruptionState
    session_id: str | None = None
    file_history_snapshots: list[dict[str, Any]] | None = None
    attribution_snapshots: list[dict[str, Any]] | None = None
    content_replacements: list[dict[str, Any]] | None = None
    context_collapse_commits: list[dict[str, Any]] | None = None
    context_collapse_snapshot: dict[str, Any] | None = None
    metadata: SessionMetadata = field(default_factory=SessionMetadata)


# ─── Message Helpers ───────────────────────────────────────────────────


def create_user_message(
    content: str,
    *,
    is_meta: bool = False,
) -> Message:
    """Create a synthetic user message."""
    msg: Message = {"type": "user", "message": {"role": "user", "content": content}}
    if is_meta:
        msg["isMeta"] = True
    return msg


def create_assistant_message(content: str) -> Message:
    """Create a synthetic assistant message."""
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": content},
    }


def is_tool_use_result_message(msg: Message) -> bool:
    """Check if a message is a tool_result response."""
    content = msg.get("message", {}).get("content")
    if isinstance(content, list) and content:
        return content[0].get("type") == "tool_result"
    return False


# ─── Filters ───────────────────────────────────────────────────────────


def filter_unresolved_tool_uses(messages: list[Message]) -> list[Message]:
    """Remove assistant messages with tool_use blocks that lack matching results.

    Walks forward collecting tool_use IDs from assistants, then marks them
    resolved when a matching tool_result appears. Drops assistants whose
    tool_uses never got results (session was killed mid-execution).
    """
    resolved_ids: set[str] = set()

    # First pass: collect all tool_result IDs
    for msg in messages:
        content = msg.get("message", {}).get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tool_use_id = block.get("tool_use_id")
                    if tool_use_id:
                        resolved_ids.add(tool_use_id)

    # Second pass: identify unresolved tool_use blocks
    unresolved_indices: set[int] = set()
    for i, msg in enumerate(messages):
        if msg.get("type") != "assistant":
            continue
        content = msg.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_id = block.get("id")
                if tool_id and tool_id not in resolved_ids:
                    unresolved_indices.add(i)
                    break

    return [msg for i, msg in enumerate(messages) if i not in unresolved_indices]


def filter_orphaned_thinking_only_messages(
    messages: list[Message],
) -> list[Message]:
    """Remove assistant messages that contain ONLY thinking blocks.

    These occur when streaming yields separate messages per content block
    and interleaved user messages prevent proper merging by message.id.
    """
    result: list[Message] = []
    for msg in messages:
        if msg.get("type") != "assistant":
            result.append(msg)
            continue
        content = msg.get("message", {}).get("content")
        if not isinstance(content, list):
            result.append(msg)
            continue
        has_non_thinking = any(isinstance(b, dict) and b.get("type") != "thinking" for b in content)
        if has_non_thinking or not content:
            result.append(msg)
    return result


def filter_whitespace_only_assistant_messages(
    messages: list[Message],
) -> list[Message]:
    """Remove assistant messages with only whitespace text content.

    This can happen when model outputs "\\n\\n" before thinking,
    user cancels mid-stream.
    """
    result: list[Message] = []
    for msg in messages:
        if msg.get("type") != "assistant":
            result.append(msg)
            continue
        content = msg.get("message", {}).get("content")
        if isinstance(content, str):
            if content.strip():
                result.append(msg)
            continue
        if isinstance(content, list):
            has_substance = False
            for block in content:
                if not isinstance(block, dict):
                    has_substance = True
                    break
                if block.get("type") == "text":
                    if block.get("text", "").strip():
                        has_substance = True
                        break
                elif block.get("type") != "thinking":
                    has_substance = True
                    break
            if has_substance:
                result.append(msg)
            continue
        result.append(msg)
    return result


# ─── Legacy Migration ──────────────────────────────────────────────────


def migrate_legacy_attachment_types(
    message: Message,
    *,
    cwd: str = "",
) -> Message:
    """Transform legacy attachment types to current types for backward compat.

    - new_file → file (with displayPath)
    - new_directory → directory (with displayPath)
    - Backfills displayPath for attachments missing it
    """
    if message.get("type") != "attachment":
        return message

    attachment = message.get("attachment", {})
    if not isinstance(attachment, dict):
        return message

    att_type = attachment.get("type", "")

    if att_type == "new_file":
        new_att = {**attachment, "type": "file"}
        filename = attachment.get("filename", "")
        if filename and cwd:
            new_att["displayPath"] = os.path.relpath(filename, cwd)
        elif filename:
            new_att["displayPath"] = filename
        return {**message, "attachment": new_att}

    if att_type == "new_directory":
        new_att = {**attachment, "type": "directory"}
        path = attachment.get("path", "")
        if path and cwd:
            new_att["displayPath"] = os.path.relpath(path, cwd)
        elif path:
            new_att["displayPath"] = path
        return {**message, "attachment": new_att}

    # Backfill displayPath for old attachments
    if "displayPath" not in attachment:
        path = attachment.get("filename") or attachment.get("path") or attachment.get("skillDir")
        if path:
            display = os.path.relpath(path, cwd) if cwd else path
            new_att = {**attachment, "displayPath": display}
            return {**message, "attachment": new_att}

    return message


# ─── Interruption Detection ───────────────────────────────────────────


def _is_terminal_tool_result(
    result: NormalizedUserMessage,
    messages: list[NormalizedMessage],
    result_idx: int,
) -> bool:
    """Is this tool_result the output of a tool that legitimately terminates a turn?

    SendUserMessage is the canonical case: in brief mode, calling it is
    the turn's final act. Walks back to find the matching assistant tool_use.
    """
    content = result.get("message", {}).get("content")
    if not isinstance(content, list) or not content:
        return False

    block = content[0]
    if not isinstance(block, dict) or block.get("type") != "tool_result":
        return False

    tool_use_id = block.get("tool_use_id")
    if not tool_use_id:
        return False

    for i in range(result_idx - 1, -1, -1):
        msg = messages[i]
        if msg.get("type") != "assistant":
            continue
        msg_content = msg.get("message", {}).get("content")
        if not isinstance(msg_content, list):
            continue
        for b in msg_content:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") == tool_use_id:
                name = b.get("name")
                return name in (
                    BRIEF_TOOL_NAME,
                    LEGACY_BRIEF_TOOL_NAME,
                    SEND_USER_FILE_TOOL_NAME,
                )
    return False


def _detect_turn_interruption(
    messages: list[NormalizedMessage],
) -> TurnInterruptionState:
    """Determine whether the conversation was interrupted mid-turn.

    Skips system/progress messages and synthetic API error assistants.
    Returns one of:
      - none: turn completed normally
      - interrupted_prompt: user sent prompt but assistant never responded
      - interrupted_turn: assistant was mid-execution when killed
    """
    if not messages:
        return TurnInterruptionState(kind="none")

    # Find last turn-relevant message, skipping system/progress/error-assistants
    last_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        m = messages[i]
        m_type = m.get("type", "")
        if m_type in ("system", "progress"):
            continue
        if m_type == "assistant" and m.get("isApiErrorMessage"):
            continue
        last_idx = i
        break

    if last_idx == -1:
        return TurnInterruptionState(kind="none")

    last_message = messages[last_idx]
    last_type = last_message.get("type", "")

    if last_type == "assistant":
        return TurnInterruptionState(kind="none")

    if last_type == "user":
        if last_message.get("isMeta") or last_message.get("isCompactSummary"):
            return TurnInterruptionState(kind="none")
        if is_tool_use_result_message(last_message):
            if _is_terminal_tool_result(last_message, messages, last_idx):
                return TurnInterruptionState(kind="none")
            return TurnInterruptionState(kind="interrupted_turn")
        # Plain text user prompt — assistant hadn't started responding
        return TurnInterruptionState(
            kind="interrupted_prompt",
            message=last_message,
        )

    if last_type == "attachment":
        return TurnInterruptionState(kind="interrupted_turn")

    return TurnInterruptionState(kind="none")


# ─── Core Deserialization ──────────────────────────────────────────────


def deserialize_messages(serialized_messages: list[Message]) -> list[Message]:
    """Deserialize messages from a log file into the format expected by the REPL.

    Filters unresolved tool uses, orphaned thinking messages, and appends a
    synthetic assistant sentinel when the last message is from the user.
    """
    return deserialize_messages_with_interrupt_detection(
        serialized_messages,
    ).messages


def deserialize_messages_with_interrupt_detection(
    serialized_messages: list[Message],
) -> DeserializeResult:
    """Like deserialize_messages, but also detects session interruptions.

    Pipeline:
      1. Migrate legacy attachment types
      2. Strip invalid permissionMode values
      3. Filter unresolved tool uses
      4. Filter orphaned thinking-only messages
      5. Filter whitespace-only assistant messages
      6. Detect turn interruption
      7. Transform interrupted_turn → interrupted_prompt with continuation
      8. Append synthetic assistant sentinel if last msg is user
    """
    # Step 1: Migrate legacy attachment types
    migrated = [migrate_legacy_attachment_types(m) for m in serialized_messages]

    # Step 2: Strip invalid permissionMode values from user messages
    for msg in migrated:
        if msg.get("type") == "user" and msg.get("permissionMode") is not None and msg.get("permissionMode") not in PERMISSION_MODES:
            msg["permissionMode"] = None

    # Step 3: Filter unresolved tool uses
    filtered = filter_unresolved_tool_uses(migrated)

    # Step 4: Filter orphaned thinking-only assistant messages
    filtered = filter_orphaned_thinking_only_messages(filtered)

    # Step 5: Filter whitespace-only assistant messages
    filtered = filter_whitespace_only_assistant_messages(filtered)

    # Step 6: Detect turn interruption
    internal_state = _detect_turn_interruption(filtered)

    # Step 7: Transform interrupted_turn → interrupted_prompt
    if internal_state.kind == "interrupted_turn":
        continuation = create_user_message(
            "Continue from where you left off.",
            is_meta=True,
        )
        filtered.append(continuation)
        turn_state = TurnInterruptionState(
            kind="interrupted_prompt",
            message=continuation,
        )
    else:
        turn_state = internal_state

    # Step 8: Append synthetic assistant sentinel after last user message
    last_relevant_idx = -1
    for i in range(len(filtered) - 1, -1, -1):
        if filtered[i].get("type") not in ("system", "progress"):
            last_relevant_idx = i
            break

    if last_relevant_idx != -1 and filtered[last_relevant_idx].get("type") == "user":
        sentinel = create_assistant_message(NO_RESPONSE_REQUESTED)
        filtered.insert(last_relevant_idx + 1, sentinel)

    return DeserializeResult(
        messages=filtered,
        turn_interruption_state=turn_state,
    )


# ─── Skill State Restoration ──────────────────────────────────────────

# Registry for restored skills (populated during resume)
_restored_skills: list[dict[str, str]] = []
_skill_listing_suppressed = False


def restore_skill_state_from_messages(messages: list[Message]) -> None:
    """Restore invoked skill state from attachment messages.

    Ensures skills survive multiple compaction cycles after resume.
    Without this, subsequent compactions would lose skill references
    because the in-memory skill set would be empty.
    """
    global _skill_listing_suppressed
    for message in messages:
        if message.get("type") != "attachment":
            continue
        attachment = message.get("attachment", {})
        if not isinstance(attachment, dict):
            continue

        if attachment.get("type") == "invoked_skills":
            for skill in attachment.get("skills", []):
                if isinstance(skill, dict) and skill.get("name") and skill.get("path") and skill.get("content"):
                    _restored_skills.append(
                        {
                            "name": skill["name"],
                            "path": skill["path"],
                            "content": skill["content"],
                        }
                    )

        if attachment.get("type") == "skill_listing":
            _skill_listing_suppressed = True


def get_restored_skills() -> list[dict[str, str]]:
    """Get the list of skills restored from message attachments."""
    return list(_restored_skills)


def is_skill_listing_suppressed() -> bool:
    """Check if the skill listing announcement should be suppressed."""
    return _skill_listing_suppressed


# ─── JSONL Transcript Loading ──────────────────────────────────────────


def load_messages_from_jsonl_path(path: str) -> tuple[list[Message], str | None]:
    """Chain-walk a transcript JSONL file and return the main conversation.

    Finds the newest non-sidechain leaf message, then walks its parentUuid
    chain to reconstruct the full conversation in order.

    Returns:
        Tuple of (messages, session_id).
    """
    if not os.path.isfile(path):
        return [], None

    by_uuid: dict[str, dict[str, Any]] = {}
    parent_targets: set[str] = set()

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            uuid = entry.get("uuid")
            if uuid:
                by_uuid[uuid] = entry
                parent_uuid = entry.get("parentUuid")
                if parent_uuid:
                    parent_targets.add(parent_uuid)

    if not by_uuid:
        return [], None

    # Find leaf UUIDs (not pointed to by any parentUuid)
    leaf_uuids = set(by_uuid.keys()) - parent_targets

    # Find the newest non-sidechain leaf
    tip: dict[str, Any] | None = None
    tip_ts = 0.0
    for uuid in leaf_uuids:
        entry = by_uuid[uuid]
        if entry.get("isSidechain"):
            continue
        ts_str = entry.get("timestamp", "")
        try:
            # Parse ISO timestamp to epoch
            from datetime import datetime

            ts = datetime.fromisoformat(
                ts_str.replace("Z", "+00:00"),
            ).timestamp()
        except ValueError, TypeError:
            ts = 0.0
        if ts > tip_ts:
            tip_ts = ts
            tip = entry

    if tip is None:
        return [], None

    # Walk the chain from tip → root via parentUuid
    chain: list[dict[str, Any]] = []
    current: dict[str, Any] | None = tip
    visited: set[str] = set()
    while current is not None:
        uuid = current.get("uuid", "")
        if uuid in visited:
            break  # Cycle guard
        visited.add(uuid)
        chain.append(current)
        parent_uuid = current.get("parentUuid")
        current = by_uuid.get(parent_uuid) if parent_uuid else None

    chain.reverse()

    # Extract the serialized messages, stripping internal fields
    messages: list[Message] = []
    for entry in chain:
        msg = _remove_extra_fields(entry)
        if msg:
            messages.append(msg)

    session_id = tip.get("sessionId")
    return messages, session_id


def _remove_extra_fields(entry: dict[str, Any]) -> Message | None:
    """Strip internal transcript fields, returning the message payload."""
    # The transcript entry IS the message — strip bookkeeping keys
    internal_keys = {
        "uuid",
        "parentUuid",
        "sessionId",
        "isSidechain",
        "timestamp",
        "leafUuids",
    }
    cleaned = {k: v for k, v in entry.items() if k not in internal_keys}
    if not cleaned.get("type"):
        return None
    return cleaned


# ─── Main Resume Pipeline ─────────────────────────────────────────────


def load_conversation_for_resume(
    *,
    session_id: str | None = None,
    source_jsonl_file: str | None = None,
    log_option: dict[str, Any] | None = None,
) -> ResumeResult | None:
    """Load a conversation for resume from various sources.

    This is the centralized function for loading and deserializing
    conversations. Mirrors the upstream TypeScript function exactly.

    Args:
        session_id: Specific session ID to load.
        source_jsonl_file: Path to a transcript JSONL file.
        log_option: Already-loaded conversation log dict.

    Returns:
        ResumeResult with deserialized messages and metadata, or None.
    """
    log: dict[str, Any] | None = None
    messages: list[Message] | None = None
    resolved_session_id: str | None = session_id

    if source_jsonl_file:
        loaded_messages, loaded_sid = load_messages_from_jsonl_path(
            source_jsonl_file,
        )
        messages = loaded_messages
        resolved_session_id = loaded_sid or resolved_session_id
    elif log_option is not None:
        log = log_option
        messages = log.get("messages")
        if not resolved_session_id:
            resolved_session_id = log.get("sessionId")
    elif session_id:
        # Caller must provide the log or JSONL — we don't access the
        # filesystem for session storage directly (that's the caller's
        # responsibility via session_recovery or similar).
        logger.warning(
            "session_id provided without log_option or source_jsonl_file — cannot load conversation for resume",
        )
        return None
    else:
        return None

    if not messages:
        return None

    # Restore skill state from invoked_skills attachments
    restore_skill_state_from_messages(messages)

    # Deserialize with interruption detection
    deserialized = deserialize_messages_with_interrupt_detection(messages)

    # Build metadata from log
    metadata = SessionMetadata()
    if log:
        metadata = SessionMetadata(
            agent_name=log.get("agentName"),
            agent_color=log.get("agentColor"),
            agent_setting=log.get("agentSetting"),
            custom_title=log.get("customTitle"),
            tag=log.get("tag"),
            mode=log.get("mode"),
            worktree_session=log.get("worktreeSession"),
            pr_number=log.get("prNumber"),
            pr_url=log.get("prUrl"),
            pr_repository=log.get("prRepository"),
            full_path=log.get("fullPath"),
        )

    return ResumeResult(
        messages=deserialized.messages,
        turn_interruption_state=deserialized.turn_interruption_state,
        session_id=resolved_session_id,
        file_history_snapshots=log.get("fileHistorySnapshots") if log else None,
        attribution_snapshots=log.get("attributionSnapshots") if log else None,
        content_replacements=log.get("contentReplacements") if log else None,
        context_collapse_commits=log.get("contextCollapseCommits") if log else None,
        context_collapse_snapshot=log.get("contextCollapseSnapshot") if log else None,
        metadata=metadata,
    )


__all__ = [
    "BRIEF_TOOL_NAME",
    "DeserializeResult",
    "NO_RESPONSE_REQUESTED",
    "PERMISSION_MODES",
    "ResumeResult",
    "SessionMetadata",
    "TurnInterruptionState",
    "create_assistant_message",
    "create_user_message",
    "deserialize_messages",
    "deserialize_messages_with_interrupt_detection",
    "filter_orphaned_thinking_only_messages",
    "filter_unresolved_tool_uses",
    "filter_whitespace_only_assistant_messages",
    "get_restored_skills",
    "is_skill_listing_suppressed",
    "is_tool_use_result_message",
    "load_conversation_for_resume",
    "load_messages_from_jsonl_path",
    "migrate_legacy_attachment_types",
    "restore_skill_state_from_messages",
]
