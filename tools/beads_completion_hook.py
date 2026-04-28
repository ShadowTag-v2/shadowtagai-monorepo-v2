#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
beads_completion_hook.py — Auto-append completed tasks to .beads/issues.jsonl

Per operator_invariants.json: ".beads/issues.jsonl" must be connected to the execution loop.

Usage:
    python3 tools/beads_completion_hook.py              # scan and append
    python3 tools/beads_completion_hook.py --dry-run     # preview only
    python3 tools/beads_completion_hook.py --status      # show current state

Can be wired into:
    - Git post-commit hook
    - CI/CD pipeline
    - Manual execution after task completion
"""

from __future__ import annotations

import argparse
import json
import re
import hashlib
from datetime import datetime, UTC
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BEADS_FILE = REPO_ROOT / ".beads" / "issues.jsonl"
TASK_MD = REPO_ROOT / "TASK.md"

# Also scan brain dirs for task.md artifacts
BRAIN_BASE = Path("/Users/pikeymickey/.gemini/antigravity/brain")

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def _load_beads() -> list[dict]:
    """Load all beads from the JSONL ledger."""
    if not BEADS_FILE.exists():
        return []
    rows = []
    with BEADS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _completed_bead_ids(beads: list[dict]) -> set[str]:
    """Get set of bead IDs that already have a completion event."""
    completed = set()
    for b in beads:
        if b.get("update_type") == "status_change" and b.get("new_status") == "closed":
            completed.add(b["id"])
        if b.get("tag") == "COMPLETION":
            # Dedup key: hash of title
            completed.add(b.get("_dedup_key", ""))
    return completed


def _dedup_key(title: str) -> str:
    """Create a deduplication key from a task title."""
    return hashlib.md5(title.strip().lower().encode()).hexdigest()[:12]


def _scan_task_md(path: Path) -> list[dict]:
    """Scan a task.md file for completed items ([x])."""
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    completed = []

    # Match lines like: - `[x]` Some task description
    pattern = re.compile(r"^[\s-]*`?\[x\]`?\s+(.+)$", re.MULTILINE | re.IGNORECASE)

    for match in pattern.finditer(content):
        title = match.group(1).strip()
        # Clean up markdown formatting
        title = re.sub(r"[*_`]", "", title)
        # Remove trailing status indicators like ✅, — ...
        title = re.sub(r"\s*[✅—].*$", "", title).strip()
        if title:
            completed.append(
                {
                    "title": title,
                    "source": str(path),
                    "_dedup_key": _dedup_key(title),
                }
            )

    return completed


def _append_bead(entry: dict) -> None:
    """Append a single entry to the beads ledger."""
    BEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with BEADS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_scan(dry_run: bool = False) -> int:
    """Scan for completed tasks and append to beads ledger."""
    print(f"{YELLOW}═══ BEADS COMPLETION HOOK ═══{NC}")

    beads = _load_beads()
    existing_keys = _completed_bead_ids(beads)

    # Collect completed tasks from all sources
    all_completed = []

    # 1. Repo-root TASK.md
    all_completed.extend(_scan_task_md(TASK_MD))

    # 2. Brain task.md files (recent conversations)
    if BRAIN_BASE.exists():
        for conv_dir in sorted(BRAIN_BASE.iterdir()):
            task_file = conv_dir / "task.md"
            if task_file.exists():
                all_completed.extend(_scan_task_md(task_file))

    # Filter out already-recorded completions
    new_completions = [c for c in all_completed if c["_dedup_key"] not in existing_keys]

    if not new_completions:
        print(f"  {GREEN}No new completions to record.{NC}")
        print(f"  📊 Existing beads: {len(beads)} | Completed tasks scanned: {len(all_completed)}")
        return 0

    print(f"  📊 Found {len(new_completions)} new completion(s) to record:")

    for comp in new_completions:
        print(f"    → {comp['title']}")

        if not dry_run:
            entry = {
                "id": comp["_dedup_key"],
                "tag": "COMPLETION",
                "title": comp["title"],
                "source": comp["source"],
                "status": "closed",
                "timestamp": datetime.now(UTC).isoformat(),
                "_dedup_key": comp["_dedup_key"],
            }
            _append_bead(entry)

    if dry_run:
        print(f"\n  {YELLOW}DRY RUN — nothing written.{NC}")
    else:
        print(f"\n  {GREEN}✅ {len(new_completions)} completion(s) appended to .beads/issues.jsonl{NC}")

    return 0


def cmd_status() -> int:
    """Show current beads state."""
    print(f"{YELLOW}═══ BEADS STATUS ═══{NC}")
    beads = _load_beads()

    open_count = sum(1 for b in beads if b.get("status") == "open")
    closed_count = sum(1 for b in beads if b.get("status") == "closed")
    decisions = sum(1 for b in beads if b.get("tag") == "DECISION")
    completions = sum(1 for b in beads if b.get("tag") == "COMPLETION")

    print(f"  Total entries: {len(beads)}")
    print(f"  Open tasks: {open_count}")
    print(f"  Closed tasks: {closed_count}")
    print(f"  Decisions: {decisions}")
    print(f"  Completions: {completions}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Beads Completion Hook — scan tasks, append completions")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--status", action="store_true", help="Show beads state")
    args = parser.parse_args()

    if args.status:
        return cmd_status()
    return cmd_scan(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
