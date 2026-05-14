#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections.abc import Iterable

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
BEADS_DIR = ROOT / ".beads"
ISSUES_FILE = BEADS_DIR / "issues.jsonl"
ARCHIVE_FILE = BEADS_DIR / "archive.jsonl"

ALLOWED_STATUSES = {
    "active",
    "historical",
    "reference_only",
    "superseded",
    "quarantined",
    "archived",
}

ALLOWED_TYPES = {
    "system_directive",
    "control_plane_operation",
    "code_artifact",
    "workflow_definition",
    "decision",
    "assumption",
    "risk",
    "supersession",
    "thread_recovery_finding",
    "product_constraint",
    "runtime_config",
    "file_manifest",
    "merge_status",
    "prompt_template",
}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_store() -> None:
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    if not ISSUES_FILE.exists():
        ISSUES_FILE.touch()


def load_beads(path: Path = ISSUES_FILE) -> list[dict[str, Any]]:
    ensure_store()
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_beads(rows: Iterable[dict[str, Any]], path: Path = ISSUES_FILE) -> None:
    ensure_store()
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_bead(bead: dict[str, Any]) -> None:
    validate_bead(bead)
    ensure_store()
    with ISSUES_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(bead, ensure_ascii=False) + "\n")


def validate_bead(bead: dict[str, Any]) -> None:
    required = [
        "id",
        "timestamp",
        "type",
        "title",
        "status",
        "source",
        "tags",
        "supersedes",
        "content",
        "description",
    ]
    missing = [k for k in required if k not in bead]
    if missing:
        raise ValueError(f"missing required fields: {missing}")

    if bead["status"] not in ALLOWED_STATUSES:
        raise ValueError(f"invalid status: {bead['status']}")

    if bead["type"] not in ALLOWED_TYPES:
        raise ValueError(f"invalid type: {bead['type']}")

    if not isinstance(bead["tags"], list):
        raise ValueError("tags must be a list")

    if not isinstance(bead["supersedes"], list):
        raise ValueError("supersedes must be a list")


def make_bead(
    bead_id: str,
    bead_type: str,
    title: str,
    content: Any,
    description: str,
    *,
    status: str = "active",
    source: str = "thread",
    tags: list[str] | None = None,
    supersedes: list[str] | None = None,
    fmt: str = "text",
    path_hint: str = "",
    family: str = "",
    priority: str = "medium",
) -> dict[str, Any]:
    bead = {
        "id": bead_id,
        "timestamp": now_iso(),
        "type": bead_type,
        "title": title,
        "status": status,
        "source": source,
        "format": fmt,
        "tags": tags or [],
        "supersedes": supersedes or [],
        "path_hint": path_hint,
        "family": family,
        "priority": priority,
        "content": content,
        "description": description,
    }
    validate_bead(bead)
    return bead


def mark_superseded(target_ids: list[str], replacement_id: str | None = None) -> int:
    rows = load_beads()
    changed = 0
    for row in rows:
        if row.get("id") in target_ids:
            row["status"] = "superseded"
            if replacement_id:
                row.setdefault("replaced_by", replacement_id)
            changed += 1
    write_beads(rows)
    return changed


def query_beads(
    *,
    status: str | None = None,
    bead_type: str | None = None,
    tag: str | None = None,
    family: str | None = None,
) -> list[dict[str, Any]]:
    rows = load_beads()
    out: list[dict[str, Any]] = []
    for row in rows:
        if status and row.get("status") != status:
            continue
        if bead_type and row.get("type") != bead_type:
            continue
        if tag and tag not in row.get("tags", []):
            continue
        if family and row.get("family") != family:
            continue
        out.append(row)
    return out


def latest_active_by_family(family: str) -> dict[str, Any] | None:
    rows = query_beads(status="active", family=family)
    if not rows:
        return None
    rows.sort(key=lambda r: r["timestamp"])
    return rows[-1]


def archive_superseded() -> int:
    rows = load_beads()
    keep: list[dict[str, Any]] = []
    move: list[dict[str, Any]] = []

    for row in rows:
        if row.get("status") == "superseded":
            row["status"] = "archived"
            move.append(row)
        else:
            keep.append(row)

    if move:
        with ARCHIVE_FILE.open("a", encoding="utf-8") as f:
            for row in move:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        write_beads(keep)

    return len(move)


def print_rows(rows: list[dict[str, Any]]) -> None:
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cli() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--type", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--content", required=True)
    p_add.add_argument("--description", required=True)
    p_add.add_argument("--status", default="active")
    p_add.add_argument("--source", default="thread")
    p_add.add_argument("--format", default="text")
    p_add.add_argument("--path-hint", default="")
    p_add.add_argument("--family", default="")
    p_add.add_argument("--priority", default="medium")
    p_add.add_argument("--tags", default="")
    p_add.add_argument("--supersedes", default="")

    p_query = sub.add_parser("query")
    p_query.add_argument("--status", default=None)
    p_query.add_argument("--type", default=None)
    p_query.add_argument("--tag", default=None)
    p_query.add_argument("--family", default=None)

    p_sup = sub.add_parser("supersede")
    p_sup.add_argument("--ids", required=True)
    p_sup.add_argument("--replacement-id", default=None)

    p_latest = sub.add_parser("latest")
    p_latest.add_argument("--family", required=True)

    sub.add_parser("archive-superseded")

    args = parser.parse_args()

    if args.cmd == "add":
        bead = make_bead(
            bead_id=args.id,
            bead_type=args.type,
            title=args.title,
            content=args.content,
            description=args.description,
            status=args.status,
            source=args.source,
            tags=[x for x in args.tags.split(",") if x],
            supersedes=[x for x in args.supersedes.split(",") if x],
            fmt=args.format,
            path_hint=args.path_hint,
            family=args.family,
            priority=args.priority,
        )
        append_bead(bead)
        print(json.dumps({"status": "ok", "added": bead["id"]}))
        return 0

    if args.cmd == "query":
        rows = query_beads(
            status=args.status,
            bead_type=args.type,
            tag=args.tag,
            family=args.family,
        )
        print_rows(rows)
        return 0

    if args.cmd == "supersede":
        changed = mark_superseded(
            target_ids=[x for x in args.ids.split(",") if x],
            replacement_id=args.replacement_id,
        )
        print(json.dumps({"status": "ok", "changed": changed}))
        return 0

    if args.cmd == "latest":
        row = latest_active_by_family(args.family)
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "archive-superseded":
        moved = archive_superseded()
        print(json.dumps({"status": "ok", "archived": moved}))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(cli())
