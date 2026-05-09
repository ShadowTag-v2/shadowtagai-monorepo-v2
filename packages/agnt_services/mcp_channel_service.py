# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""MCP Channel Services — Permission relay, allowlist, and channel management.

Ported from Claude Code v2.1.91 src/services/mcp/:
  - channelPermissions.ts (240L) → Channel permission relay via Telegram/Discord
  - channelAllowlist.ts (76L) → Runtime allowlist for MCP channel servers
  - channelNotification.ts (316L) → Structured event notifications to channels

Key patterns:
  - tengu_harbor feature flag gates channel functionality
  - tengu_harbor_permissions gates permission relay specifically
  - Short request IDs: FNV-1a hash → base-25 (no 'l') → 5-char string
  - Blocklist filtering prevents offensive generated IDs
  - Server-parsed permission replies (not client regex)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
import contextlib

logger = logging.getLogger(__name__)

# ── Channel permission constants ────────────────────────────────────

# 25-letter alphabet: a-z minus 'l' (looks like 1/I in many fonts)
ID_ALPHABET = "abcdefghijkmnopqrstuvwxyz"

# Blocklist for generated IDs — re-hash with salt suffix if matched
ID_AVOID_SUBSTRINGS = frozenset(
    {
        "fuck",
        "shit",
        "cunt",
        "cock",
        "dick",
        "twat",
        "piss",
        "crap",
        "ass",
        "tit",
        "cum",
        "fag",
        "nig",
        "rape",
        "nazi",
        "damn",
        "poo",
        "wank",
        "anus",
    }
)

# Reply format: /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i
PERMISSION_REPLY_RE = re.compile(r"^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$", re.IGNORECASE)


class ChannelCapability(StrEnum):
    """MCP channel experimental capabilities."""

    CHANNEL = "claude/channel"
    CHANNEL_PERMISSION = "claude/channel/permission"


@dataclass
class ChannelPermissionResponse:
    """Response from a channel permission relay."""

    behavior: str  # "allow" | "deny"
    from_server: str  # e.g. "plugin:telegram:tg"


@dataclass
class PermissionRequest:
    """Pending permission request awaiting channel response."""

    request_id: str
    tool_name: str
    tool_input_preview: str
    callbacks: list = field(default_factory=list)


# ── ID generation ───────────────────────────────────────────────────


def _fnv1a_hash(data: str) -> int:
    """FNV-1a hash → uint32. Not crypto, just a stable short ID generator."""
    h = 0x811C9DC5
    for ch in data:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def _hash_to_id(input_str: str) -> str:
    """Convert a string to a 5-char base-25 ID (no 'l')."""
    h = _fnv1a_hash(input_str)
    chars = []
    for _ in range(5):
        chars.append(ID_ALPHABET[h % 25])
        h //= 25
    return "".join(chars)


def short_request_id(tool_use_id: str) -> str:
    """Generate a 5-char short ID from a tool use ID.

    Letters-only so phone users don't switch keyboard modes.
    Re-hashes with salt if result contains blocklisted substring.
    25^5 ≈ 9.8M space — birthday collision needs ~3K simultaneous pending.
    """
    candidate = _hash_to_id(tool_use_id)
    for salt in range(10):
        if not any(bad in candidate for bad in ID_AVOID_SUBSTRINGS):
            return candidate
        candidate = _hash_to_id(f"{tool_use_id}:{salt}")
    return candidate


def truncate_for_preview(input_data: object, max_len: int = 200) -> str:
    """Truncate tool input to a phone-sized JSON preview."""
    import json

    try:
        s = json.dumps(input_data, default=str)
        return s[:max_len] + "…" if len(s) > max_len else s
    except TypeError, ValueError:
        return "(unserializable)"


# ── Channel allowlist ───────────────────────────────────────────────


@dataclass
class ChannelAllowlist:
    """Runtime allowlist for MCP channel servers.

    Mirrors CC's tengu_harbor flag — when enabled, only listed server
    names can act as communication channels.
    """

    enabled: bool = False
    _allowed_names: set[str] = field(default_factory=set)

    def add(self, server_name: str) -> None:
        self._allowed_names.add(server_name)

    def is_allowed(self, server_name: str) -> bool:
        if not self.enabled:
            return False
        return server_name in self._allowed_names

    def clear(self) -> None:
        self._allowed_names.clear()


# ── Permission callbacks ────────────────────────────────────────────


class ChannelPermissionCallbacks:
    """Factory for permission callback management.

    The pending dict is instance-scoped (not module-level) for test isolation.
    Same lifetime pattern as CC's replBridgePermissionCallbacks.
    """

    def __init__(self) -> None:
        self._pending: dict[str, list] = {}

    def on_response(self, request_id: str, handler: object) -> object:
        """Register a resolver for a request ID. Returns unsubscribe callable."""
        if request_id not in self._pending:
            self._pending[request_id] = []
        self._pending[request_id].append(handler)

        def unsubscribe():
            if request_id in self._pending:
                with contextlib.suppress(ValueError):
                    self._pending[request_id].remove(handler)
                if not self._pending[request_id]:
                    del self._pending[request_id]

        return unsubscribe

    def resolve(self, request_id: str, behavior: str, from_server: str) -> bool:
        """Resolve a pending request from a structured channel event.

        Returns True if the ID was pending.
        """
        handlers = self._pending.pop(request_id, None)
        if handlers is None:
            return False
        response = ChannelPermissionResponse(behavior=behavior, from_server=from_server)
        for handler in handlers:
            if callable(handler):
                handler(response)
        return True

    @property
    def pending_count(self) -> int:
        return len(self._pending)


# ── Filter for permission-relay capable clients ─────────────────────


def filter_permission_relay_clients(
    clients: list[dict],
    is_in_allowlist: object,
) -> list[dict]:
    """Filter MCP clients to those that can relay permission prompts.

    Three conditions, ALL required:
    1. Connected
    2. In the session's --channels allowlist
    3. Declares BOTH claude/channel AND claude/channel/permission capabilities
    """
    result = []
    for c in clients:
        if c.get("type") != "connected":
            continue
        name = c.get("name", "")
        if not (callable(is_in_allowlist) and is_in_allowlist(name)):
            continue
        experimental = (c.get("capabilities") or {}).get("experimental") or {}
        has_channel = ChannelCapability.CHANNEL in experimental
        has_perm = ChannelCapability.CHANNEL_PERMISSION in experimental
        if has_channel and has_perm:
            result.append(c)
    return result


def health_check() -> bool:
    return True
