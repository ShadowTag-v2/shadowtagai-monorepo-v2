# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR Cassette — Serializable API interaction recordings.

A cassette is a JSONL file containing timestamped request/response pairs.
Cassettes are stored in brain/{conv}/vcr_cassettes/ and can be replayed
for deterministic testing.

Design:
    - Each entry is independently serializable (JSONL, one per line)
    - Entries include fingerprints for fuzzy matching during replay
    - Cassettes support append-only recording (concurrent-safe)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CassetteEntry:
    """Single recorded API interaction.

    Attributes:
        request_hash: SHA-256 fingerprint of the canonical request body.
        request_body: Full serialized request payload.
        response_body: Full serialized response payload.
        model: Model ID used for the request.
        timestamp: Unix epoch when recorded.
        latency_ms: Original API latency.
        token_usage: Token counts (prompt, completion, total).
        tags: Optional metadata tags for filtering.
    """

    request_hash: str
    request_body: dict[str, Any]
    response_body: dict[str, Any]
    model: str = ""
    timestamp: float = 0.0
    latency_ms: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSONL storage."""
        return {
            "request_hash": self.request_hash,
            "request_body": self.request_body,
            "response_body": self.response_body,
            "model": self.model,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
            "token_usage": self.token_usage,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CassetteEntry:
        """Deserialize from dictionary."""
        return cls(
            request_hash=data.get("request_hash", ""),
            request_body=data.get("request_body", {}),
            response_body=data.get("response_body", {}),
            model=data.get("model", ""),
            timestamp=data.get("timestamp", 0.0),
            latency_ms=data.get("latency_ms", 0.0),
            token_usage=data.get("token_usage", {}),
            tags=data.get("tags", []),
        )


def compute_request_hash(request_body: dict[str, Any]) -> str:
    """Compute a deterministic hash for a request body.

    Normalizes the request by:
    1. Sorting keys
    2. Stripping timestamps and session IDs
    3. SHA-256 hashing the canonical JSON

    Args:
        request_body: The API request payload.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    # Strip non-deterministic fields before hashing
    normalized = {k: v for k, v in request_body.items() if k not in ("timestamp", "session_id", "request_id")}
    canonical = json.dumps(normalized, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class Cassette:
    """A collection of recorded API interactions.

    Cassettes are stored as JSONL files with one entry per line.
    They support both sequential recording and hash-based lookup for replay.

    Args:
        path: File path for the cassette JSONL file.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._entries: list[CassetteEntry] = []
        self._index: dict[str, int] = {}  # request_hash → entry index
        self._replay_cursor: int = 0

    @property
    def path(self) -> Path:
        """The cassette file path."""
        return self._path

    @property
    def entries(self) -> list[CassetteEntry]:
        """All recorded entries."""
        return self._entries

    def load(self) -> None:
        """Load entries from disk."""
        self._entries.clear()
        self._index.clear()

        if not self._path.exists():
            return

        with open(self._path) as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = CassetteEntry.from_dict(data)
                    self._entries.append(entry)
                    self._index[entry.request_hash] = line_num
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip malformed entries
                    import logging

                    logging.getLogger(__name__).warning(
                        "Skipping malformed cassette entry at line %d: %s",
                        line_num,
                        e,
                    )

    def save(self) -> None:
        """Write all entries to disk (full overwrite)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(entry.to_dict()) + "\n")

    def append(self, entry: CassetteEntry) -> None:
        """Append a single entry (concurrent-safe append)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._entries.append(entry)
        self._index[entry.request_hash] = len(self._entries) - 1
        with open(self._path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def lookup(self, request_hash: str) -> CassetteEntry | None:
        """Find an entry by request hash (for replay)."""
        idx = self._index.get(request_hash)
        if idx is not None and idx < len(self._entries):
            return self._entries[idx]
        return None

    def next_sequential(self) -> CassetteEntry | None:
        """Get next entry in sequential order (for ordered replay)."""
        if self._replay_cursor >= len(self._entries):
            return None
        entry = self._entries[self._replay_cursor]
        self._replay_cursor += 1
        return entry

    def reset_cursor(self) -> None:
        """Reset sequential replay cursor to beginning."""
        self._replay_cursor = 0

    def record(
        self,
        request_body: dict[str, Any],
        response_body: dict[str, Any],
        model: str = "",
        latency_ms: float = 0.0,
        token_usage: dict[str, int] | None = None,
        tags: list[str] | None = None,
    ) -> CassetteEntry:
        """Record a new API interaction.

        Convenience method that creates a CassetteEntry and appends it.

        Returns:
            The newly created entry.
        """
        entry = CassetteEntry(
            request_hash=compute_request_hash(request_body),
            request_body=request_body,
            response_body=response_body,
            model=model,
            timestamp=time.time(),
            latency_ms=latency_ms,
            token_usage=token_usage or {},
            tags=tags or [],
        )
        self.append(entry)
        return entry

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"Cassette(path={self._path}, entries={len(self._entries)})"
