#!/usr/bin/env python3
"""
Beads Auto-Hydrate Hook — Gemini CLI SessionStart

Reads the latest entries from .beads/issues.jsonl and injects them
as system context at session start. Closes the beads auto-append loop.
"""

import json
import sys
import os
from pathlib import Path

BEADS_PATH = Path(os.environ.get("GEMINI_PROJECT_DIR", ".")) / ".beads" / "issues.jsonl"
MAX_ENTRIES = 10  # inject the last 10 beads


def main():
  """Read stdin (hook input), hydrate beads, write to stdout."""
  # Read hook input from stdin (Gemini CLI sends JSON)
  try:
    _hook_input = json.load(sys.stdin)
  except Exception:
    _hook_input = {}

  beads_summary = []

  if BEADS_PATH.exists():
    try:
      lines = BEADS_PATH.read_text().strip().split("\n")
      recent = lines[-MAX_ENTRIES:] if len(lines) > MAX_ENTRIES else lines
      for line in recent:
        if line.strip():
          try:
            entry = json.loads(line)
            # Extract key fields
            title = entry.get("title", entry.get("id", "?"))
            status = entry.get("status", "?")
            ts = entry.get("timestamp", entry.get("created", "?"))
            beads_summary.append(f"  [{status}] {title} ({ts})")
          except json.JSONDecodeError:
            continue
    except Exception as e:
      beads_summary.append(f"  ⚠️ Error reading beads: {e}")
  else:
    beads_summary.append("  (no .beads/issues.jsonl found)")

  context_block = "BEADS CONTEXT (last {}):\n{}".format(
    len(beads_summary), "\n".join(beads_summary)
  )

  # Write hook response
  response = {
    "decision": "allow",
    "systemMessage": f"*** BEADS AUTO-HYDRATE ***\n{context_block}",
  }
  json.dump(response, sys.stdout)
  sys.stderr.write(f"[beads-hydrate] Injected {len(beads_summary)} entries\n")


if __name__ == "__main__":
  main()
