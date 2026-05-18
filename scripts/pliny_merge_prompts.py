#!/usr/bin/env python3
# Copyright 2026 ShadowTag AI — All Rights Reserved.
# pliny_merge_prompts.py — Block-merger for incoming prompt leaks.
# Diffs and compiles YAML prompt blocks into atomic chunks.

"""
Pliny Merge Prompts — Diff & Compile Incoming Prompt Leaks

Reads YAML prompt files from .agent/prompts/, extracts block-level
changes, and produces a merged master prompt with conflict resolution.

Usage:
    python scripts/pliny_merge_prompts.py [--dry-run]
"""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
  import yaml
except ImportError:
  print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
  sys.exit(1)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / ".agent" / "prompts"
OUTPUT_FILE = PROMPTS_DIR / "merged_master.yaml"


def load_yaml(path: Path) -> dict:
  """Load a YAML file, return empty dict on failure."""
  try:
    with open(path) as f:
      return yaml.safe_load(f) or {}
  except (yaml.YAMLError, OSError) as e:
    print(f"WARN: Failed to load {path.name}: {e}", file=sys.stderr)
    return {}


def block_hash(content: str) -> str:
  """SHA-256 fingerprint of a block's rules text."""
  return hashlib.sha256(content.encode()).hexdigest()[:12]


def merge_blocks(sources: list[dict]) -> dict:
  """Merge blocks from multiple YAML sources. Last-write-wins on conflict."""
  merged = {}
  provenance = {}

  for source in sources:
    blocks = source.get("blocks", {})
    source_version = source.get("version", "unknown")

    for block_name, block_data in blocks.items():
      rules_text = (
        block_data.get("rules", "") if isinstance(block_data, dict) else str(block_data)
      )
      fingerprint = block_hash(rules_text)

      if block_name in merged:
        existing_fp = block_hash(
          merged[block_name].get("rules", "")
          if isinstance(merged[block_name], dict)
          else str(merged[block_name])
        )
        if existing_fp != fingerprint:
          print(
            f"  CONFLICT: {block_name} "
            f"({provenance[block_name]} -> {source_version}). "
            f"Last-write-wins."
          )

      merged[block_name] = block_data
      provenance[block_name] = source_version

  return merged


def main() -> int:
  parser = argparse.ArgumentParser(description="Merge prompt YAML blocks")
  parser.add_argument(
    "--dry-run", action="store_true", help="Print merge without writing"
  )
  args = parser.parse_args()

  if not PROMPTS_DIR.exists():
    print(f"ERROR: Prompts directory not found: {PROMPTS_DIR}", file=sys.stderr)
    return 1

  yaml_files = sorted(PROMPTS_DIR.glob("*.yaml"))
  if not yaml_files:
    print("No YAML files found in prompts directory.", file=sys.stderr)
    return 1

  print(f"[pliny_merge] Scanning {len(yaml_files)} YAML files in {PROMPTS_DIR}")

  sources = []
  for yf in yaml_files:
    data = load_yaml(yf)
    if data:
      sources.append(data)
      version = data.get("version", "?")
      block_count = len(data.get("blocks", {}))
      print(f"  ✅ {yf.name} (v{version}, {block_count} blocks)")

  merged_blocks = merge_blocks(sources)

  output = {
    "version": "merged-auto",
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "description": f"Auto-merged from {len(sources)} sources by pliny_merge_prompts.py",
    "blocks": merged_blocks,
    "activation": {
      "instruction": "Apply EVERY block above on every single response. Merged master policy."
    },
  }

  if args.dry_run:
    print("\n--- DRY RUN: Merged output ---")
    print(yaml.dump(output, default_flow_style=False, sort_keys=False))
    return 0

  with open(OUTPUT_FILE, "w") as f:
    yaml.dump(output, f, default_flow_style=False, sort_keys=False)

  print(f"\n✅ Merged {len(merged_blocks)} blocks -> {OUTPUT_FILE}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
