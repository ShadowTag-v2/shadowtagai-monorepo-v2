# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Forking Swarm — session_forking.py

Dense multi-file operations (>5 files) are chunked horizontally
into independent work units that can be executed in parallel
by sub-agents or sequential passes.

Key principle: each fork is self-contained with its own
file manifest, rollback plan, and verification step.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


FORK_LOG_PATH = Path(".beads/session_forks.jsonl")
MAX_FILES_PER_FORK = 5


@dataclass
class WorkUnit:
    """A single fork of work — self-contained file edit batch."""

    fork_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    files: list[str] = field(default_factory=list)
    description: str = ""
    status: str = "pending"  # pending, in_progress, complete, failed, rolled_back
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    verification: str | None = None
    rollback_commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL logging."""
        return {
            "fork_id": self.fork_id,
            "files": self.files,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "verification": self.verification,
            "rollback_commands": self.rollback_commands,
        }


def plan_forks(
    file_list: list[str],
    descriptions: list[str] | None = None,
    max_per_fork: int = MAX_FILES_PER_FORK,
) -> list[WorkUnit]:
    """Chunk a large file list into independent work units.

    Args:
        file_list: All files that need editing.
        descriptions: Optional per-fork descriptions.
        max_per_fork: Max files per work unit (default 5).

    Returns:
        List of WorkUnit objects ready for execution.
    """
    forks: list[WorkUnit] = []

    for i in range(0, len(file_list), max_per_fork):
        chunk = file_list[i : i + max_per_fork]
        desc = ""
        if descriptions and i // max_per_fork < len(descriptions):
            desc = descriptions[i // max_per_fork]
        else:
            desc = f"Fork {len(forks) + 1}: {', '.join(Path(f).name for f in chunk)}"

        fork = WorkUnit(
            files=chunk,
            description=desc,
            rollback_commands=[f"git checkout HEAD -- {f}" for f in chunk],
        )
        forks.append(fork)

    _log_forks(forks, "planned")
    return forks


def start_fork(fork: WorkUnit) -> WorkUnit:
    """Mark a fork as in-progress."""
    fork.status = "in_progress"
    _log_fork(fork, "started")
    return fork


def complete_fork(fork: WorkUnit, verification_result: str | None = None) -> WorkUnit:
    """Mark a fork as complete with optional verification."""
    fork.status = "complete"
    fork.completed_at = datetime.now(UTC).isoformat()
    fork.verification = verification_result
    _log_fork(fork, "completed")
    return fork


def fail_fork(fork: WorkUnit, error: str) -> WorkUnit:
    """Mark a fork as failed."""
    fork.status = "failed"
    fork.completed_at = datetime.now(UTC).isoformat()
    fork.verification = f"FAILED: {error}"
    _log_fork(fork, "failed")
    return fork


def get_rollback_plan(forks: list[WorkUnit]) -> list[str]:
    """Get combined rollback commands for all failed forks."""
    commands: list[str] = []
    for fork in forks:
        if fork.status == "failed":
            commands.extend(fork.rollback_commands)
    return commands


def summarize_forks(forks: list[WorkUnit]) -> dict[str, Any]:
    """Summary statistics for a set of forks."""
    total = len(forks)
    by_status: dict[str, int] = {}
    for fork in forks:
        by_status[fork.status] = by_status.get(fork.status, 0) + 1

    return {
        "total_forks": total,
        "total_files": sum(len(f.files) for f in forks),
        "by_status": by_status,
        "all_complete": by_status.get("complete", 0) == total,
    }


def _log_fork(fork: WorkUnit, event: str) -> None:
    """Append fork event to JSONL log."""
    FORK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FORK_LOG_PATH.open("a") as f:
        f.write(
            json.dumps(
                {"event": event, "timestamp": datetime.now(UTC).isoformat(), **fork.to_dict()},
                default=str,
            )
            + "\n"
        )


def _log_forks(forks: list[WorkUnit], event: str) -> None:
    """Log multiple forks at once."""
    for fork in forks:
        _log_fork(fork, event)


if __name__ == "__main__":
    # Self-test
    files = [
        "apps/counselconduit/src/main.py",
        "apps/counselconduit/src/auth.py",
        "apps/counselconduit/src/billing.py",
        "apps/counselconduit/src/models.py",
        "apps/counselconduit/src/routes.py",
        "apps/counselconduit/src/middleware.py",
        "apps/counselconduit/src/Claude_Code_6.py",
        "apps/counselconduit/src/oracle.py",
    ]
    forks = plan_forks(files)
    print(f"Planned {len(forks)} forks:")
    for fork in forks:
        print(f"  {fork.fork_id}: {fork.files}")
    print(f"Summary: {summarize_forks(forks)}")
