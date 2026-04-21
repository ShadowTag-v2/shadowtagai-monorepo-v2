#!/usr/bin/env python3
"""Session Manifest Builder.
========================
Parses raw_sessions.txt → deduplicates → emits structured TELEPORT_MANIFEST.json.

Usage:
  python scripts/session_manifest_builder.py Docs/raw_sessions.txt
  python scripts/session_manifest_builder.py Docs/raw_sessions.txt --merge   # merge with existing manifest
  python scripts/session_manifest_builder.py Docs/raw_sessions.txt --dry-run # print only

Output: Docs/TELEPORT_MANIFEST.json (updated in place)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "apps" / "ShadowTag-v2_stack" / "nascent-apollo" / "Docs" / "TELEPORT_MANIFEST.json"

# Priority order for groups
GROUP_PRIORITY = {
    "JUDGE_LEVEL": 1,
    "JUDGE_EXTENDED": 1,
    "INGESTION_PIPELINE": 2,
    "JUICY": 2,
    "MERGE_BRANCHES": 2,
    "011CUv_CLUSTER": 3,
    "011CUu_CLUSTER": 3,
    "UNGROUPED": 4,
}

SESSION_RE = re.compile(r"(session_[A-Za-z0-9]+)")


def parse_raw_file(path: Path) -> tuple[dict[str, str], int, int]:
    """Returns:
    session_map: {session_id: group}
    total_lines: raw non-comment, non-empty lines scanned
    duplicate_count: how many duplicate IDs were encountered.

    """
    session_map: dict[str, str] = {}
    seen: set[str] = set()
    duplicates = 0
    total_lines = 0

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        total_lines += 1

        m = SESSION_RE.search(stripped)
        if not m:
            continue
        sid = m.group(1)

        # Extract group label (second token if present)
        parts = stripped.split()
        group = "UNGROUPED"
        for part in parts[1:]:
            if part in GROUP_PRIORITY:
                group = part
                break

        if sid in seen:
            duplicates += 1
            continue
        seen.add(sid)
        session_map[sid] = group

    return session_map, total_lines, duplicates


def build_manifest(session_map: dict[str, str], raw_lines: int, duplicates: int) -> dict:
    groups: dict[str, dict] = {}
    for gname in GROUP_PRIORITY:
        sessions = [sid for sid, g in session_map.items() if g == gname]
        if sessions:
            groups[gname] = {
                "priority": GROUP_PRIORITY[gname],
                "count": len(sessions),
                "sessions": sorted(sessions),
            }

    return {
        "meta": {
            "source": "session_manifest_builder.py",
            "date": str(date.today()),
            "total_unique_sessions": len(session_map),
            "total_raw_lines": raw_lines,
            "duplicates_removed": duplicates,
            "resume_command": "claude --resume <session_id>",
            "note": "--teleport is not a native Claude Code flag; use --resume",
        },
        "groups": groups,
        "ingest_status": {},
    }


def merge_with_existing(new_manifest: dict, existing_path: Path) -> dict:
    """Preserve existing ingest_status and add any new sessions."""
    if not existing_path.exists():
        return new_manifest

    existing = json.loads(existing_path.read_text())
    # Carry over ingest_status
    new_manifest["ingest_status"] = existing.get("ingest_status", {})
    # Carry over any sessions from old JUDGE_LEVEL that might not be in raw file
    old_judge = existing.get("priorities", {}).get("JUDGE_LEVEL", [])
    if old_judge:
        current_judge = new_manifest["groups"].get("JUDGE_LEVEL", {}).get("sessions", [])
        merged = sorted(set(current_judge) | set(old_judge))
        if "JUDGE_LEVEL" not in new_manifest["groups"]:
            new_manifest["groups"]["JUDGE_LEVEL"] = {"priority": 1, "count": 0, "sessions": []}
        new_manifest["groups"]["JUDGE_LEVEL"]["sessions"] = merged
        new_manifest["groups"]["JUDGE_LEVEL"]["count"] = len(merged)
        # Re-count total
        all_ids: set[str] = set()
        for g in new_manifest["groups"].values():
            all_ids.update(g.get("sessions", []))
        new_manifest["meta"]["total_unique_sessions"] = len(all_ids)
    return new_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build TELEPORT_MANIFEST.json from raw session list")
    parser.add_argument("raw_file", type=Path, help="Path to raw_sessions.txt")
    parser.add_argument("--merge", action="store_true", help="Merge with existing manifest")
    parser.add_argument("--dry-run", action="store_true", help="Print manifest without writing")
    parser.add_argument("--out", type=Path, default=MANIFEST_PATH, help="Output manifest path")
    args = parser.parse_args()

    if not args.raw_file.exists():
        sys.exit(1)

    session_map, raw_lines, duplicates = parse_raw_file(args.raw_file)
    manifest = build_manifest(session_map, raw_lines, duplicates)

    if args.merge or args.out.exists():
        manifest = merge_with_existing(manifest, args.out)

    output = json.dumps(manifest, indent=2)

    if args.dry_run:
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n")
    for _gname, _gdata in manifest["groups"].items():
        pass


if __name__ == "__main__":
    main()
