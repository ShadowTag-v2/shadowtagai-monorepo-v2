#!/usr/bin/env python3
"""
cognitive_boot.py — Initializes the cognitive architecture and synchronizes
epistemic targets via the omni_epistemic_sync.ts 14-point multiplexer.

Usage:
    python3 scripts/cognitive_boot.py <atom_type> <new_knowledge> [old_text_to_supersede]

Example:
    python3 scripts/cognitive_boot.py constraint "AlloyDB replaces PostgreSQL" "PostgreSQL"

If called with no args, prints status and exits cleanly.
"""

import subprocess
import sys
from pathlib import Path

MONOREPO = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = MONOREPO / "scripts" / "omni_epistemic_sync.ts"


def main() -> int:
  """Initializes the environment and synchronizes epistemic targets."""
  print("Initializing Cognitive Architecture...")

  if not SYNC_SCRIPT.exists():
    print(f"ERROR: Sync script not found at {SYNC_SCRIPT}", file=sys.stderr)
    return 1

  # Parse optional CLI arguments — the TS script requires atom_type + new_knowledge
  args = sys.argv[1:]
  if len(args) < 2:
    print("No sync arguments provided. Running status check only.")
    print(f"  Monorepo: {MONOREPO}")
    print(
      f"  Sync script: {SYNC_SCRIPT} ({'exists' if SYNC_SCRIPT.exists() else 'MISSING'})"
    )
    print("State A active. Pass <atom_type> <new_knowledge> to broadcast.")
    return 0

  cmd = ["bun", "run", str(SYNC_SCRIPT), *args]
  try:
    subprocess.run(
      cmd,
      cwd=str(MONOREPO),
      check=True,
      capture_output=False,
    )
  except FileNotFoundError:
    print("ERROR: 'bun' is not installed or not in PATH.", file=sys.stderr)
    return 1
  except subprocess.CalledProcessError as exc:
    print(
      f"ERROR: Epistemic sync failed with exit code {exc.returncode}", file=sys.stderr
    )
    return exc.returncode

  print("Epistemic sync complete. State A active.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
