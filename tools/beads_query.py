#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
BEADS_FILE = ROOT / ".beads" / "issues.jsonl"
ARCHIVE_FILE = ROOT / ".beads" / "archive.jsonl"

DEFAULT_VISIBLE_STATUSES = ["active", "historical", "reference_only"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_all(include_archive: bool = False) -> list[dict[str, Any]]:
    rows = load_jsonl(BEADS_FILE)
    if include_archive:
        rows.extend(load_jsonl(ARCHIVE_FILE))
    return rows


def visible_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("status") in DEFAULT_VISIBLE_STATUSES]


def filter_rows(
    rows: list[dict[str, Any]],
    *,
    status: str | None = None,
    bead_type: str | None = None,
    tag: str | None = None,
    family: str | None = None,
    text: str | None = None,
) -> list[dict[str, Any]]:
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
        if text:
            hay = json.dumps(row, ensure_ascii=False).lower()
            if text.lower() not in hay:
                continue
        out.append(row)
    return out


def sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (r.get("timestamp", ""), r.get("id", "")))


def latest_by_family(rows: list[dict[str, Any]], family: str) -> dict[str, Any] | None:
    family_rows = [r for r in rows if r.get("family") == family]
    if not family_rows:
        return None
    return sort_rows(family_rows)[-1]


def resolve_supersession(rows: list[dict[str, Any]], bead_id: str) -> list[dict[str, Any]]:
    chain: list[dict[str, Any]] = []
    index = {r.get("id"): r for r in rows}
    current = index.get(bead_id)
    if not current:
        return chain

    chain.append(current)
    while True:
        replacement_id = current.get("replaced_by")
        if replacement_id and replacement_id in index:
            current = index[replacement_id]
            chain.append(current)
            continue

        next_rows = [r for r in rows if bead_id in r.get("supersedes", [])]
        if not next_rows:
            break
        next_rows = sort_rows(next_rows)
        current = next_rows[-1]
        chain.append(current)
        bead_id = current.get("id", "")
    return chain


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_family: dict[str, int] = {}

    for row in rows:
        by_status[row.get("status", "")] = by_status.get(row.get("status", ""), 0) + 1
        by_type[row.get("type", "")] = by_type.get(row.get("type", ""), 0) + 1
        fam = row.get("family", "")
        if fam:
            by_family[fam] = by_family.get(fam, 0) + 1

    return {
        "count": len(rows),
        "by_status": by_status,
        "by_type": by_type,
        "by_family": by_family,
    }


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cli() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--all-statuses", action="store_true")
    p_list.add_argument("--include-archive", action="store_true")
    p_list.add_argument("--status", default=None)
    p_list.add_argument("--type", default=None)
    p_list.add_argument("--tag", default=None)
    p_list.add_argument("--family", default=None)
    p_list.add_argument("--text", default=None)

    p_latest = sub.add_parser("latest")
    p_latest.add_argument("--family", required=True)
    p_latest.add_argument("--include-archive", action="store_true")

    p_chain = sub.add_parser("chain")
    p_chain.add_argument("--id", required=True)
    p_chain.add_argument("--include-archive", action="store_true")

    p_summary = sub.add_parser("summary")
    p_summary.add_argument("--all-statuses", action="store_true")
    p_summary.add_argument("--include-archive", action="store_true")

    args = parser.parse_args()

    rows = load_all(include_archive=getattr(args, "include_archive", False))
    if not getattr(args, "all_statuses", False):
        rows = visible_rows(rows)

    if args.cmd == "list":
        rows = filter_rows(
            rows,
            status=args.status,
            bead_type=args.type,
            tag=args.tag,
            family=args.family,
            text=args.text,
        )
        print_json(sort_rows(rows))
        return 0

    if args.cmd == "latest":
        row = latest_by_family(rows, args.family)
        print_json(row)
        return 0

    if args.cmd == "chain":
        chain = resolve_supersession(rows, args.id)
        print_json(chain)
        return 0

    if args.cmd == "summary":
        print_json(summarize(rows))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(cli())
