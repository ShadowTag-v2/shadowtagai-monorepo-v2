#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
LOCK="$ROOT/memory_lock.json"

if [[ ! -f "$LOCK" ]]; then
  echo "MEMORY STATUS: DRIFTED"
  echo "Reason: missing memory_lock.json"
  echo "Action: Stopping immediately. Requesting re-lock."
  exit 1
fi

python3 - <<'PY'
import json
import os
import sys
from pathlib import Path

root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball").resolve()
lock = json.loads((root / "memory_lock.json").read_text())

expected_root = lock["workspace_root"]
expected_brain = lock["brain_dir"]
forbidden_strings = lock.get("forbidden_strings", [])

errors = []

if str(root) != expected_root:
    errors.append(f"workspace root mismatch: {root} != {expected_root}")

brain_env = os.environ.get("BRAIN_DIR", "")
if brain_env and brain_env != expected_brain:
    errors.append(f"BRAIN_DIR mismatch: {brain_env} != {expected_brain}")

for path in root.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".sqlite", ".db", ".pyc"}:
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for bad in forbidden_strings:
        if bad in text:
            errors.append(f"forbidden string present in {path}")

if errors:
    print("MEMORY STATUS: DRIFTED")
    for err in errors:
        print("Reason:", err)
    print("Action: Stopping immediately. Requesting re-lock.")
    sys.exit(1)

print("MEMORY STATUS: LOCKED")
print("NEXT ACTION: Ready for Stage 3 canonicalization and repo-drift audit.")
PY
