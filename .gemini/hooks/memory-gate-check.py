#!/usr/bin/env python3
"""
Memory Gate Check — Gemini CLI SessionStart

Reads memory_state from operator_invariants.json and injects it
as a system message at session start.
"""

import json
import sys
import os
from pathlib import Path

INVARIANTS_PATH = Path(os.environ.get("GEMINI_PROJECT_DIR", ".")) / "operator_invariants.json"


def main():
    try:
        _hook_input = json.load(sys.stdin)
    except Exception:
        _hook_input = {}

    state = "UNKNOWN"
    try:
        if INVARIANTS_PATH.exists():
            data = json.loads(INVARIANTS_PATH.read_text())
            state = data.get("memory_state", "LOCKED")
    except Exception as e:
        sys.stderr.write(f"[memory-gate] Error: {e}\n")

    response = {
        "decision": "allow",
        "systemMessage": f"*** PRE-ACTION MEMORY GATE: State={state} ***",
    }
    json.dump(response, sys.stdout)
    sys.stderr.write(f"[memory-gate] State: {state}\n")


if __name__ == "__main__":
    main()
