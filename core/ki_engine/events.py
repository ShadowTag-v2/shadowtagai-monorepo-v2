# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Event Sourcing — Item 13: Append-only event log for KI mutations.

Every KI create/update/archive/promote/conflict emits a structured event
to ki_events.ndjson. Enables:
  - Audit trail of all knowledge changes
  - Deterministic replay
  - Conflict resolution history
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class EventAction(StrEnum):
    """KI mutation event types."""

    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    EXPIRE = "expire"
    PROMOTE = "promote"  # belief → fact
    CONFLICT = "conflict"
    MERGE = "merge"
    SHARE = "share"
    UNSHARE = "unshare"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"


@dataclass
class KIEvent:
    """A single KI mutation event."""

    event_id: str
    timestamp: str
    action: EventAction
    ki_name: str
    agent_id: str | None = None
    details: dict = field(default_factory=dict)
    snapshot: dict | None = None  # Full KI metadata at time of event

    def to_json(self) -> str:
        """Serialize to JSON string for NDJSON line."""
        d = {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "action": self.action.value if isinstance(self.action, EventAction) else self.action,
            "ki_name": self.ki_name,
        }
        if self.agent_id:
            d["agent_id"] = self.agent_id
        if self.details:
            d["details"] = self.details
        if self.snapshot:
            d["snapshot"] = self.snapshot
        return json.dumps(d, separators=(",", ":"))

    @classmethod
    def from_json(cls, line: str) -> KIEvent:
        """Deserialize from JSON string."""
        d = json.loads(line)
        return cls(
            event_id=d["event_id"],
            timestamp=d["timestamp"],
            action=EventAction(d["action"]),
            ki_name=d["ki_name"],
            agent_id=d.get("agent_id"),
            details=d.get("details", {}),
            snapshot=d.get("snapshot"),
        )


def _event_log_path(ki_dir: Path) -> Path:
    """Get the event log path for a KI directory."""
    return ki_dir / "ki_events.ndjson"


def generate_event_id() -> str:
    """Generate a unique event ID."""
    return f"evt-{uuid.uuid4().hex[:12]}"


def append_event(
    ki_dir: Path,
    action: EventAction,
    ki_name: str,
    agent_id: str | None = None,
    details: dict | None = None,
    snapshot: dict | None = None,
) -> KIEvent:
    """Append an event to the KI event log.

    Args:
        ki_dir: Path to KI directory.
        action: The mutation type.
        ki_name: Name of the KI being mutated.
        agent_id: Optional agent identifier.
        details: Optional additional context.
        snapshot: Optional full KI metadata snapshot.

    Returns:
        The created KIEvent.
    """
    event = KIEvent(
        event_id=generate_event_id(),
        timestamp=datetime.now(UTC).isoformat(),
        action=action,
        ki_name=ki_name,
        agent_id=agent_id,
        details=details or {},
        snapshot=snapshot,
    )

    log_path = _event_log_path(ki_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(event.to_json() + "\n")

    return event


def read_events(
    ki_dir: Path,
    action_filter: EventAction | None = None,
    ki_filter: str | None = None,
    limit: int | None = None,
) -> list[KIEvent]:
    """Read events from the log, optionally filtered.

    Args:
        ki_dir: Path to KI directory.
        action_filter: Only return events of this action type.
        ki_filter: Only return events for this KI name.
        limit: Maximum number of events to return (most recent first).

    Returns:
        List of KIEvent objects.
    """
    log_path = _event_log_path(ki_dir)
    if not log_path.exists():
        return []

    events = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = KIEvent.from_json(line)
                if action_filter and event.action != action_filter:
                    continue
                if ki_filter and event.ki_name != ki_filter:
                    continue
                events.append(event)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    # Most recent first for limit
    events.reverse()
    if limit:
        events = events[:limit]

    return events


def count_events(ki_dir: Path) -> int:
    """Count total events in the log."""
    log_path = _event_log_path(ki_dir)
    if not log_path.exists():
        return 0
    with open(log_path) as f:
        return sum(1 for line in f if line.strip())


def compact_log(
    ki_dir: Path,
    keep_latest_per_ki: int = 10,
) -> int:
    """Compact the event log, keeping only recent events per KI.

    Returns:
        Number of events removed.
    """
    events = read_events(ki_dir)
    events.reverse()  # Back to chronological order

    # Group by KI
    per_ki: dict[str, list[KIEvent]] = {}
    for event in events:
        per_ki.setdefault(event.ki_name, []).append(event)

    # Keep only latest N per KI
    kept: list[KIEvent] = []
    removed = 0
    for ki_name, ki_events in per_ki.items():
        if len(ki_events) > keep_latest_per_ki:
            removed += len(ki_events) - keep_latest_per_ki
            ki_events = ki_events[-keep_latest_per_ki:]
        kept.extend(ki_events)

    # Sort chronologically
    kept.sort(key=lambda e: e.timestamp)

    # Rewrite log
    log_path = _event_log_path(ki_dir)
    backup = log_path.with_suffix(".ndjson.bak")
    if log_path.exists():
        log_path.rename(backup)

    with open(log_path, "w") as f:
        for event in kept:
            f.write(event.to_json() + "\n")

    return removed
