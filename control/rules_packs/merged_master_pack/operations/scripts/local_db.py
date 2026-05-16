#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

DB_ROOT = Path("./data/localdb")


def cmd_init() -> int:
    DB_ROOT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"status": "ok", "action": "init", "path": str(DB_ROOT)}))
    return 0


def cmd_stats() -> int:
    exists = DB_ROOT.exists()
    files = []
    if exists:
        files = sorted(str(p.relative_to(DB_ROOT)) for p in DB_ROOT.rglob("*"))
    print(json.dumps({"status": "ok", "action": "stats", "path": str(DB_ROOT), "exists": exists, "file_count": len(files), "files": files[:100]}))
    return 0


def cmd_smoke_test() -> int:
    DB_ROOT.mkdir(parents=True, exist_ok=True)
    marker = DB_ROOT / "SMOKE_TEST_OK"
    marker.write_text("ok\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "action": "smoke-test", "path": str(DB_ROOT), "marker": str(marker)}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    if args.init:
        return cmd_init()
    if args.stats:
        return cmd_stats()
    if args.smoke_test:
        return cmd_smoke_test()
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
