#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from collections.abc import Iterable

DEFAULT_SRC_ROOT = Path("/Users/pikeymickey/shadowtag-omega-v4-stack")
DEFAULT_DST_ROOT = Path(
  "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack"
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
    msg = f"missing src root: {src_root}"
    raise SystemExit(msg)

  results = []

  if args.one:
    src = src_root / args.one
    if not src.exists():
      msg = f"missing requested source: {src}"
      raise SystemExit(msg)
    dst = dst_root / args.one
    results.append(copy_tree(src, dst))
  else:
    for src in iter_sources(src_root):
      dst = dst_root / src.name
      if src.is_dir():
        results.append(copy_tree(src, dst))

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
