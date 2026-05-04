# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Typed inter-daemon messaging module.

Ported from ECC2 comms/mod.rs (157L Rust). Provides structured,
priority-aware message passing between the 5-daemon fleet:
KAIROS, Dream Consolidation, Loop Steward, GCA Autolint, pnkln-evolve.

Architecture:
    - MessageType enum with 5 variants (TaskHandoff, Query, Response, Completed, Conflict)
    - TaskPriority enum with 4 levels (Low, Normal, High, Critical)
    - Pydantic models for type-safe serialization
    - JSON file persistence in .beads/messages/
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, UTC
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# uuid7 import with monorepo / container fallback (Core Truth #1)
# ---------------------------------------------------------------------------
try:
    from apps.counselconduit.api.uuid7 import uuid7  # type: ignore[import-not-found]
except ImportError:
    try:
        from api.uuid7 import uuid7  # type: ignore[import-not-found]
    except ImportError:
        import uuid as _uuid

        def uuid7() -> str:  # type: ignore[misc]
            """Fallback to uuid4 when uuid7 is not available."""
            return str(_uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TaskPriority(StrEnum):
    """Priority levels for task handoff messages."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(StrEnum):
    """Discriminator for inter-daemon message variants."""

    TASK_HANDOFF = "task_handoff"
    QUERY = "query"
    RESPONSE = "response"
    COMPLETED = "completed"
    CONFLICT = "conflict"


# ---------------------------------------------------------------------------
# Message Variant Models
# ---------------------------------------------------------------------------


class TaskHandoff(BaseModel):
    """Task delegation from one daemon to another."""

    task: str
    context: str = ""
    priority: TaskPriority = TaskPriority.NORMAL


class Query(BaseModel):
    """Information request between daemons."""

    question: str


class Response(BaseModel):
    """Reply to a query."""

    answer: str


class Completed(BaseModel):
    """Notification of task completion."""

    summary: str
    files_changed: list[str] = Field(default_factory=list)


class Conflict(BaseModel):
    """Concurrent edit conflict detection."""

    file: str
    description: str


# Union type for all message variants
MessageVariant = TaskHandoff | Query | Response | Completed | Conflict


# ---------------------------------------------------------------------------
# Wire Protocol
# ---------------------------------------------------------------------------


class DaemonMessage(BaseModel):
    """Envelope for typed inter-daemon messages."""

    id: str = Field(default_factory=lambda: str(uuid7()))
    timestamp: float = Field(default_factory=time.time)
    from_daemon: str
    to_daemon: str
    msg_type: MessageType
    payload: str  # JSON-serialized MessageVariant

    @property
    def age_seconds(self) -> float:
        """How old this message is."""
        return time.time() - self.timestamp


# ---------------------------------------------------------------------------
# Core Functions (ported from comms/mod.rs)
# ---------------------------------------------------------------------------

# Maximum message payload size (64KB)
MAX_MESSAGE_SIZE = 65536

# Default message directory
_DEFAULT_MSG_DIR = ".beads/messages"


def _variant_to_type(msg: MessageVariant) -> MessageType:
    """Map a message variant to its MessageType discriminator."""
    if isinstance(msg, TaskHandoff):
        return MessageType.TASK_HANDOFF
    if isinstance(msg, Query):
        return MessageType.QUERY
    if isinstance(msg, Response):
        return MessageType.RESPONSE
    if isinstance(msg, Completed):
        return MessageType.COMPLETED
    if isinstance(msg, Conflict):
        return MessageType.CONFLICT
    raise TypeError(f"Unknown message variant: {type(msg)}")


def send(
    from_: str,
    to: str,
    msg: MessageVariant,
    *,
    msg_dir: str | Path = _DEFAULT_MSG_DIR,
) -> str:
    """Serialize and persist a typed message.

    Args:
        from_: Source daemon identifier (e.g., "kairos", "dream").
        to: Target daemon identifier.
        msg: A typed message variant.
        msg_dir: Directory for message persistence.

    Returns:
        The message ID (uuid7).

    Raises:
        ValueError: If the serialized payload exceeds MAX_MESSAGE_SIZE.
    """
    payload = msg.model_dump_json()
    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message payload exceeds {MAX_MESSAGE_SIZE} bytes: {len(payload)}")

    envelope = DaemonMessage(
        from_daemon=from_,
        to_daemon=to,
        msg_type=_variant_to_type(msg),
        payload=payload,
    )

    # Persist to filesystem
    msg_path = Path(msg_dir)
    msg_path.mkdir(parents=True, exist_ok=True)

    ts = datetime.fromtimestamp(envelope.timestamp, tz=UTC)
    filename = f"{ts.strftime('%Y-%m-%dT%H-%M-%S')}_{from_}_{to}_{envelope.msg_type.value}.json"
    filepath = msg_path / filename

    filepath.write_text(envelope.model_dump_json(indent=2), encoding="utf-8")

    return envelope.id


def parse(content: str) -> MessageVariant | None:
    """Safely deserialize a message payload.

    Tries each variant type in order. Returns None if content
    is not valid JSON or doesn't match any variant.

    Args:
        content: JSON string to parse.

    Returns:
        A MessageVariant instance, or None if parsing fails.
    """
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    # Try each variant based on field presence
    if "task" in data:
        try:
            return TaskHandoff.model_validate(data)
        except Exception:
            pass
    if "question" in data:
        try:
            return Query.model_validate(data)
        except Exception:
            pass
    if "answer" in data:
        try:
            return Response.model_validate(data)
        except Exception:
            pass
    if "summary" in data:
        try:
            return Completed.model_validate(data)
        except Exception:
            pass
    if "file" in data and "description" in data:
        try:
            return Conflict.model_validate(data)
        except Exception:
            pass

    return None


def preview(msg: DaemonMessage) -> str:
    """Generate a human-readable message preview.

    Ported from comms/mod.rs preview() function.

    Args:
        msg: The daemon message envelope.

    Returns:
        A truncated, human-readable summary string.
    """
    variant = parse(msg.payload)

    if isinstance(variant, TaskHandoff):
        if variant.priority == TaskPriority.NORMAL:
            return f"handoff {truncate(variant.task, 56)}"
        return f"handoff [{variant.priority}] {truncate(variant.task, 48)}"

    if isinstance(variant, Query):
        return f"query {truncate(variant.question, 56)}"

    if isinstance(variant, Response):
        return f"response {truncate(variant.answer, 56)}"

    if isinstance(variant, Completed):
        if not variant.files_changed:
            return f"completed {truncate(variant.summary, 48)}"
        return f"completed {truncate(variant.summary, 40)} | {len(variant.files_changed)} files"

    if isinstance(variant, Conflict):
        return f"conflict {variant.file} | {truncate(variant.description, 40)}"

    # Fallback for unparseable payloads
    type_label = msg.msg_type.value.replace("_", " ")
    return f"{type_label} {truncate(msg.payload, 56)}"


def handoff_priority(msg: DaemonMessage) -> TaskPriority:
    """Extract priority from a message, with legacy JSON fallback.

    Ported from comms/mod.rs handoff_priority() + extract_legacy_handoff_priority().

    Args:
        msg: The daemon message envelope.

    Returns:
        The task priority level.
    """
    variant = parse(msg.payload)
    if isinstance(variant, TaskHandoff):
        return variant.priority

    # Legacy fallback: try raw JSON extraction
    return _extract_legacy_priority(msg.payload)


def _extract_legacy_priority(content: str) -> TaskPriority:
    """Extract priority from legacy untyped JSON."""
    try:
        data = json.loads(content)
        raw = data.get("priority", "normal")
        return TaskPriority(raw) if raw in TaskPriority.__members__.values() else TaskPriority.NORMAL
    except json.JSONDecodeError, TypeError, ValueError:
        return TaskPriority.NORMAL


def truncate(value: str, max_chars: int = 56) -> str:
    """Unicode-safe string truncation with ellipsis.

    Ported from comms/mod.rs truncate() function.

    Args:
        value: String to truncate.
        max_chars: Maximum character count (default 56).

    Returns:
        Truncated string with trailing ellipsis if shortened.
    """
    trimmed = value.strip()
    if len(trimmed) <= max_chars:
        return trimmed
    return trimmed[: max_chars - 1] + "…"


def list_messages(
    msg_dir: str | Path = _DEFAULT_MSG_DIR,
    *,
    daemon: str | None = None,
    since: float | None = None,
) -> list[DaemonMessage]:
    """List persisted messages, optionally filtered.

    Args:
        msg_dir: Directory containing message files.
        daemon: If set, only return messages to/from this daemon.
        since: If set, only return messages after this timestamp.

    Returns:
        List of DaemonMessage instances, sorted by timestamp (newest first).
    """
    msg_path = Path(msg_dir)
    if not msg_path.exists():
        return []

    messages: list[DaemonMessage] = []
    for f in msg_path.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            msg = DaemonMessage.model_validate(data)
            if daemon and msg.from_daemon != daemon and msg.to_daemon != daemon:
                continue
            if since and msg.timestamp < since:
                continue
            messages.append(msg)
        except Exception:
            continue

    return sorted(messages, key=lambda m: m.timestamp, reverse=True)


def cleanup_old_messages(
    msg_dir: str | Path = _DEFAULT_MSG_DIR,
    *,
    max_age_days: int = 7,
) -> int:
    """Remove messages older than max_age_days.

    Args:
        msg_dir: Directory containing message files.
        max_age_days: Maximum message age in days.

    Returns:
        Number of messages removed.
    """
    msg_path = Path(msg_dir)
    if not msg_path.exists():
        return 0

    cutoff = time.time() - (max_age_days * 86400)
    removed = 0

    for f in msg_path.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("timestamp", 0) < cutoff:
                os.remove(f)
                removed += 1
        except Exception:
            continue

    return removed
