# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Team Memory Sync — Batch 6 port from Claude Code v2.1.91.

Synchronizes shared team memory (CLAUDE.md) across team members
via a backend registry. Includes secret scanning guard.

Ported from: external_repos/claude_code_services/teamMemorySync/
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Secret scanner patterns ──────────────────────────────────────────

_SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Key", re.compile(r"AKIA[0-9A-Z]{16}", re.ASCII)),
    ("GitHub Token", re.compile(r"gh[ps]_[A-Za-z0-9_]{36,}", re.ASCII)),
    ("Slack Token", re.compile(r"xox[bpors]-[0-9a-zA-Z-]+", re.ASCII)),
    (
        "Private Key",
        re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----", re.ASCII),
    ),
    ("Generic API Key", re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9]{20,}", re.ASCII)),
    ("Bearer Token", re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{20,}", re.ASCII)),
]


@dataclass(frozen=True, slots=True)
class SecretFinding:
    """A detected secret in team memory content."""

    pattern_name: str
    line_number: int
    redacted_match: str


def scan_for_secrets(content: str) -> list[SecretFinding]:
    """Scan content for potential secrets.

    Args:
        content: Text content to scan.

    Returns:
        List of SecretFinding objects for any matches.
    """
    findings: list[SecretFinding] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        for name, pattern in _SECRET_PATTERNS:
            for match in pattern.finditer(line):
                matched = match.group(0)
                # Redact: show first 4 and last 4 chars
                if len(matched) > 12:
                    redacted = matched[:4] + "..." + matched[-4:]
                else:
                    redacted = matched[:4] + "..."
                findings.append(
                    SecretFinding(
                        pattern_name=name,
                        line_number=line_num,
                        redacted_match=redacted,
                    )
                )
    return findings


@dataclass(frozen=True, slots=True)
class TeamMemoryEntry:
    """A single team memory entry with metadata."""

    key: str
    content: str
    content_hash: str
    author: str | None = None
    updated_at: str | None = None

    @staticmethod
    def from_content(key: str, content: str, author: str | None = None) -> TeamMemoryEntry:
        """Create a TeamMemoryEntry from raw content."""
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        return TeamMemoryEntry(
            key=key,
            content=content,
            content_hash=content_hash,
            author=author,
        )


@dataclass
class TeamMemorySyncService:
    """Manages team memory synchronization with secret guard.

    Mirrors the CC teamMemorySync module:
    - Reads local CLAUDE.md / team memory files
    - Scans for secrets before upload
    - Computes content hashes for diff detection
    - Applies remote entries with conflict detection
    """

    _entries: dict[str, TeamMemoryEntry] = field(default_factory=dict)
    _block_on_secrets: bool = True

    def add_entry(self, key: str, content: str, author: str | None = None) -> SecretFinding | None:
        """Add or update a team memory entry.

        Scans for secrets before accepting the entry.

        Args:
            key: Entry key (e.g., "project:CLAUDE.md").
            content: File content.
            author: Optional author identifier.

        Returns:
            First SecretFinding if secrets detected and blocking is enabled,
            None if the entry was accepted.
        """
        if self._block_on_secrets:
            findings = scan_for_secrets(content)
            if findings:
                logger.warning(
                    "Secret detected in team memory entry %s: %s at line %d",
                    key,
                    findings[0].pattern_name,
                    findings[0].line_number,
                )
                return findings[0]

        entry = TeamMemoryEntry.from_content(key, content, author)
        self._entries[key] = entry
        return None

    def get_changed_entries(
        self,
        remote_hashes: dict[str, str],
    ) -> dict[str, TeamMemoryEntry]:
        """Get entries that differ from remote.

        Args:
            remote_hashes: Dict of key → content_hash from remote.

        Returns:
            Dict of entries whose local hash differs from remote.
        """
        return {
            k: v
            for k, v in self._entries.items()
            if remote_hashes.get(k) != v.content_hash
        }

    def all_entries(self) -> dict[str, TeamMemoryEntry]:
        """Get all registered entries."""
        return dict(self._entries)
