# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API-Round Message Grouping — splits messages at assistant-turn boundaries.

Ported from: compact/grouping.ts
Reference: CC-1180 — extracted to break compact.ts ↔ compactMessages.ts cycle.

Groups messages at API-round boundaries: one group per API round-trip.
A boundary fires when a NEW assistant response begins (different message ID
from the prior assistant). For well-formed conversations this is an API-safe
split point — the API contract requires every tool_use to be resolved before
the next assistant turn.
"""

from __future__ import annotations

from typing import Any


def group_messages_by_api_round(
    messages: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    """Group messages at API-round boundaries.

    A boundary fires when a new assistant response begins (different
    ``message_id`` from the prior assistant). For well-formed conversations
    this is an API-safe split point.

    Works with both the Claude-format messages (``type``/``message.id``) and
    our internal ``Message`` dataclass (``role``/``metadata.message_id``).

    Args:
        messages: List of message dicts or Message-like objects.

    Returns:
        List of message groups, each group representing one API round.
    """
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    last_assistant_id: str | None = None

    for msg in messages:
        # Resolve assistant ID from either format
        msg_role = _get_role(msg)
        msg_id = _get_assistant_id(msg)

        if msg_role == "assistant" and last_assistant_id is not None and msg_id != last_assistant_id and len(current) > 0:
            groups.append(current)
            current = [msg]
        else:
            current.append(msg)

        if msg_role == "assistant":
            last_assistant_id = msg_id

    if current:
        groups.append(current)

    return groups


def _get_role(msg: Any) -> str:
    """Extract role from a message, supporting dict and dataclass formats."""
    # Dict with 'type' key (Claude format)
    if isinstance(msg, dict):
        return msg.get("type", msg.get("role", ""))
    # Dataclass with role attribute
    return getattr(msg, "role", getattr(msg, "type", ""))


def _get_assistant_id(msg: Any) -> str | None:
    """Extract assistant message ID from either format.

    Claude format: ``msg.message.id``
    Internal format: ``msg.metadata.get("message_id")``
    """
    if isinstance(msg, dict):
        inner = msg.get("message", {})
        if isinstance(inner, dict):
            return inner.get("id")
        return msg.get("metadata", {}).get("message_id")
    # Dataclass
    inner = getattr(msg, "message", None)
    if inner and hasattr(inner, "id"):
        return inner.id
    metadata = getattr(msg, "metadata", {})
    if isinstance(metadata, dict):
        return metadata.get("message_id")
    return None
