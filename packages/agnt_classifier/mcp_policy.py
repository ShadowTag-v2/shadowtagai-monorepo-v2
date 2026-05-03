# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""MCP Server Policy Enforcement — Ported from Claude Code v2.1.91 config.ts.

Implements the enterprise-grade MCP server allowlist/denylist pattern from
Claude Code's `isMcpServerAllowedByPolicy()` (config.ts L417-508).

Architecture:
    - Denylist ALWAYS takes absolute precedence over allowlist.
    - Empty allowlist = block all servers.
    - No allowlist defined (None) = allow all (no restrictions).
    - Policy entries can match by server name, command array, or URL pattern.
    - Reserved server names are always blocked.

Reference: Claude Code v2.1.91 src/services/mcp/config.ts
Reference: AGNT STATE B Spec P2.3
"""

from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# ── Reserved Server Names (always blocked) ──

RESERVED_SERVER_NAMES: frozenset[str] = frozenset(
    {
        # Claude Code internal servers
        "claude-in-chrome",
        "computer-use",
        "computer-use-internal",
        # SDK transport placeholders
        "sdk-transport",
        # AGNT internal servers
        "agnt-internal",
        "agnt-classifier",
    }
)


class PolicyEntryType(StrEnum):
    """Type discriminator for policy entries."""

    NAME = "name"
    COMMAND = "command"
    URL = "url"


@dataclass(frozen=True)
class PolicyEntry:
    """A single entry in the allow/deny list.

    Supports three matching modes:
        - Name: exact match on server name
        - Command: match on the command array (executable + args)
        - URL: glob match on the server URL
    """

    entry_type: PolicyEntryType
    server_name: str = ""
    server_command: tuple[str, ...] = ()
    server_url: str = ""

    @classmethod
    def from_name(cls, name: str) -> PolicyEntry:
        """Create a name-based policy entry."""
        return cls(entry_type=PolicyEntryType.NAME, server_name=name)

    @classmethod
    def from_command(cls, command: list[str] | tuple[str, ...]) -> PolicyEntry:
        """Create a command-based policy entry."""
        return cls(
            entry_type=PolicyEntryType.COMMAND,
            server_command=tuple(command),
        )

    @classmethod
    def from_url(cls, url: str) -> PolicyEntry:
        """Create a URL-based policy entry."""
        return cls(entry_type=PolicyEntryType.URL, server_url=url)


@dataclass
class MCPPolicyConfig:
    """Enterprise MCP policy configuration.

    Mirrors Claude Code's managed settings for MCP server gating.
    """

    allowed_servers: list[PolicyEntry] | None = None
    denied_servers: list[PolicyEntry] = field(default_factory=list)

    @property
    def has_allowlist(self) -> bool:
        """True if an allowlist is defined (even if empty)."""
        return self.allowed_servers is not None

    @property
    def has_denylist(self) -> bool:
        """True if a denylist has entries."""
        return len(self.denied_servers) > 0


@dataclass(frozen=True)
class MCPServerInfo:
    """Minimal info about an MCP server for policy evaluation."""

    name: str
    command: list[str] | None = None
    url: str | None = None
    server_type: str = "stdio"  # stdio | sse | http | ws


@dataclass(frozen=True)
class PolicyResult:
    """Result of a policy evaluation."""

    allowed: bool
    reason: str
    matched_entry: PolicyEntry | None = None


# ── Policy Evaluation Functions ──


def _command_arrays_match(pattern: tuple[str, ...], actual: list[str] | tuple[str, ...]) -> bool:
    """Check if command arrays match.

    Claude Code uses exact match on the command array.
    We add glob support for the executable path.
    """
    if not pattern or not actual:
        return False
    if len(pattern) > len(actual):
        return False

    # First element (executable): glob match
    if not fnmatch.fnmatch(actual[0], pattern[0]):
        return False

    # Remaining elements: exact match (order matters)
    return all(pattern[i] == actual[i] for i in range(1, len(pattern)))


def _url_matches_pattern(server_url: str, pattern_url: str) -> bool:
    """Check if a server URL matches a pattern URL.

    Supports glob patterns in the path component.
    Ported from Claude Code's urlMatchesPattern().
    """
    try:
        server_parsed = urlparse(server_url)
        pattern_parsed = urlparse(pattern_url)
    except Exception:
        return False

    # Scheme must match exactly
    if server_parsed.scheme != pattern_parsed.scheme:
        return False

    # Host must match exactly
    if server_parsed.hostname != pattern_parsed.hostname:
        return False

    # Port must match (or both absent)
    if server_parsed.port != pattern_parsed.port:
        return False

    # Path: glob match
    return fnmatch.fnmatch(server_parsed.path, pattern_parsed.path or "/*")


def is_mcp_server_denied(
    server_name: str,
    server_info: MCPServerInfo | None,
    policy: MCPPolicyConfig,
) -> tuple[bool, PolicyEntry | None]:
    """Check if an MCP server is on the denylist.

    Denylist ALWAYS takes absolute precedence.
    Ported from Claude Code config.ts isMcpServerDenied().
    """
    # Reserved names are always denied
    if server_name.lower() in RESERVED_SERVER_NAMES:
        return True, PolicyEntry.from_name(server_name)

    for entry in policy.denied_servers:
        if entry.entry_type == PolicyEntryType.NAME:
            if entry.server_name == server_name:
                return True, entry

        elif entry.entry_type == PolicyEntryType.COMMAND and server_info:
            if server_info.command and _command_arrays_match(entry.server_command, server_info.command):
                return True, entry

        elif entry.entry_type == PolicyEntryType.URL and server_info:
            if server_info.url and _url_matches_pattern(server_info.url, entry.server_url):
                return True, entry

    return False, None


def is_mcp_server_allowed_by_policy(
    server_name: str,
    server_info: MCPServerInfo | None,
    policy: MCPPolicyConfig,
) -> PolicyResult:
    """Evaluate whether an MCP server is allowed by enterprise policy.

    Ported from Claude Code config.ts isMcpServerAllowedByPolicy() L417-508.

    Priority:
        1. Denylist → absolute block
        2. No allowlist → allow all
        3. Empty allowlist → block all
        4. Allowlist match → allow
        5. No match → block
    """
    # Step 1: Denylist takes absolute precedence
    denied, deny_entry = is_mcp_server_denied(server_name, server_info, policy)
    if denied:
        return PolicyResult(
            allowed=False,
            reason=f"Server '{server_name}' is on the denylist.",
            matched_entry=deny_entry,
        )

    # Step 2: No allowlist = no restrictions
    if not policy.has_allowlist:
        return PolicyResult(
            allowed=True,
            reason="No allowlist configured — all servers permitted.",
        )

    assert policy.allowed_servers is not None

    # Step 3: Empty allowlist = block all
    if len(policy.allowed_servers) == 0:
        return PolicyResult(
            allowed=False,
            reason="Empty allowlist — all servers blocked.",
        )

    # Step 4: Check allowlist entries
    has_command_entries = any(e.entry_type == PolicyEntryType.COMMAND for e in policy.allowed_servers)
    has_url_entries = any(e.entry_type == PolicyEntryType.URL for e in policy.allowed_servers)

    if server_info:
        # stdio server with command
        if server_info.command:
            if has_command_entries:
                for entry in policy.allowed_servers:
                    if entry.entry_type == PolicyEntryType.COMMAND:
                        if _command_arrays_match(entry.server_command, server_info.command):
                            return PolicyResult(
                                allowed=True,
                                reason="Server command matches allowlist entry.",
                                matched_entry=entry,
                            )
                return PolicyResult(
                    allowed=False,
                    reason=f"Server '{server_name}' command does not match any allowlist entry.",
                )
            # No command entries → fall through to name check

        # Remote server with URL
        elif server_info.url:
            if has_url_entries:
                for entry in policy.allowed_servers:
                    if entry.entry_type == PolicyEntryType.URL:
                        if _url_matches_pattern(server_info.url, entry.server_url):
                            return PolicyResult(
                                allowed=True,
                                reason="Server URL matches allowlist pattern.",
                                matched_entry=entry,
                            )
                return PolicyResult(
                    allowed=False,
                    reason=f"Server '{server_name}' URL does not match any allowlist entry.",
                )
            # No URL entries → fall through to name check

    # Name-based check (fallback for all server types)
    for entry in policy.allowed_servers:
        if entry.entry_type == PolicyEntryType.NAME:
            if entry.server_name == server_name:
                return PolicyResult(
                    allowed=True,
                    reason=f"Server name '{server_name}' is on the allowlist.",
                    matched_entry=entry,
                )

    return PolicyResult(
        allowed=False,
        reason=f"Server '{server_name}' is not on the allowlist.",
    )


def filter_servers_by_policy(
    servers: dict[str, MCPServerInfo],
    policy: MCPPolicyConfig,
) -> tuple[dict[str, MCPServerInfo], list[str]]:
    """Filter a dict of MCP servers by policy. Returns (allowed, blocked_names).

    Ported from Claude Code's filterServersByManagedPolicy().
    """
    allowed: dict[str, MCPServerInfo] = {}
    blocked_names: list[str] = []

    for name, info in servers.items():
        result = is_mcp_server_allowed_by_policy(name, info, policy)
        if result.allowed:
            allowed[name] = info
        else:
            blocked_names.append(name)
            logger.info("MCP server '%s' blocked by policy: %s", name, result.reason)

    return allowed, blocked_names


def get_default_agnt_policy() -> MCPPolicyConfig:
    """Return the default AGNT MCP policy.

    Allows the 5 fleet servers and blocks dangerous/reserved names.
    """
    return MCPPolicyConfig(
        allowed_servers=[
            PolicyEntry.from_name("StitchMCP"),
            PolicyEntry.from_name("chrome-devtools-mcp"),
            PolicyEntry.from_name("firebase-mcp-server"),
            PolicyEntry.from_name("google-developer-knowledge"),
            PolicyEntry.from_name("sequential-thinking"),
        ],
        denied_servers=[
            PolicyEntry.from_name("claude-in-chrome"),
            PolicyEntry.from_name("computer-use"),
            PolicyEntry.from_name("computer-use-internal"),
        ],
    )
