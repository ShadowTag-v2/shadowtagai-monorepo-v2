# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""API-round message grouping — ported from grouping.ts.

Groups messages at API-round boundaries: one group per API round-trip.
A boundary fires when a NEW assistant response begins (different
message.id from the prior assistant).

For well-formed conversations this is an API-safe split point — the API
contract requires every tool_use to be resolved before the next assistant
turn, so pairing validity falls out of the assistant-id boundary.

For malformed inputs (dangling tool_use after resume/truncation) the
fork's ``ensure_tool_result_pairing`` repairs the split at API time.

Extracted to its own file to break circular imports (CC-1180).
"""

from __future__ import annotations

from packages.agnt_utils.compact.types import Message


def group_messages_by_api_round(messages: list[Message]) -> list[list[Message]]:
    """Partition *messages* into groups at API-round boundaries.

    A boundary fires when:
      1. The message is ``type == "assistant"``, AND
      2. Its ``message.id`` differs from the previous assistant's id, AND
      3. The current group is non-empty.

    Streaming chunks from the same API response share an id, so
    boundaries only fire at the start of a genuinely new round.

    Args:
        messages: Ordered list of Message dicts.

    Returns:
        List of groups, each a list of Message dicts.
    """
    groups: list[list[Message]] = []
    current: list[Message] = []
    last_assistant_id: str | None = None

    for msg in messages:
        msg_type = msg.get("type", "")
        inner = msg.get("message", {})
        msg_id = inner.get("id") if isinstance(inner, dict) else None

        # New API round boundary
        if msg_type == "assistant" and msg_id != last_assistant_id and current:
            groups.append(current)
            current = [msg]
        else:
            current.append(msg)

        if msg_type == "assistant":
            last_assistant_id = msg_id

    if current:
        groups.append(current)

    return groups
