#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import json
import os
import shutil
from collections.abc import Iterable
from pathlib import Path

DEFAULT_SRC_ROOT = Path("/Users/pikeymickey/aiyou-stack")
DEFAULT_DST_ROOT = Path(
  "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack"
)
EXCLUDE_DIRS = {
  ".git",
  "__pycache__",
  ".pytest_cache",
  ".mypy_cache",
  ".ruff_cache",
  "node_modules",
  ".DS_Store",
}


def iter_sources(root: Path) -> Iterable[Path]:
  for child in sorted(root.iterdir()):
    if child.name in EXCLUDE_DIRS:
      continue
    yield child


def copy_tree(src: Path, dst: Path) -> dict:
  copied = 0
  skipped = 0
  dst.mkdir(parents=True, exist_ok=True)

  for current_root, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    rel_root = Path(current_root).relative_to(src)
    target_root = dst / rel_root
    target_root.mkdir(parents=True, exist_ok=True)

    for name in files:
      if name in EXCLUDE_DIRS:
        skipped += 1
        continue
      s = Path(current_root) / name
      t = target_root / name
      shutil.copy2(s, t)
      copied += 1

  return {
    "source": str(src),
    "destination": str(dst),
    "copied_files": copied,
    "skipped_files": skipped,
  }


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Merge external trees into monorepo subtree"
  )
  parser.add_argument("--src-root", default=str(DEFAULT_SRC_ROOT))
  parser.add_argument("--dst-root", default=str(DEFAULT_DST_ROOT))
  parser.add_argument(
    "--one", help="Merge only one named child repo/folder from src-root"
  )
  args = parser.parse_args()

  src_root = Path(args.src_root).expanduser().resolve()
  dst_root = Path(args.dst_root).expanduser().resolve()

  if not src_root.exists():
    raise SystemExit(f"missing src root: {src_root}")

  results = []

  if args.one:
    src = src_root / args.one
    if not src.exists():
      raise SystemExit(f"missing requested source: {src}")
    dst = dst_root / args.one
    results.append(copy_tree(src, dst))
  else:
    for src in iter_sources(src_root):
      dst = dst_root / src.name
      if src.is_dir():
        results.append(copy_tree(src, dst))

  print(
    json.dumps(
      {
        "status": "ok",
        "src_root": str(src_root),
        "dst_root": str(dst_root),
        "merged_count": len(results),
        "results": results,
      },
      indent=2,
    )
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
