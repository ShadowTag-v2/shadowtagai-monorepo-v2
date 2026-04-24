#!/usr/bin/env python3
"""Wire lint results into the .beads/issues.jsonl audit trail.

Reads .lint-results/latest.json and appends a structured entry to .beads/issues.jsonl.
Designed to be called after an autolint daemon run.

Usage:
    python3 scripts/wire_lint_to_beads.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT_RESULTS = REPO_ROOT / ".lint-results" / "latest.json"
BEADS_DIR = REPO_ROOT / ".beads"
ISSUES_FILE = BEADS_DIR / "issues.jsonl"


def main() -> None:
    if not LINT_RESULTS.exists():
        print("[*] No lint results found at", LINT_RESULTS)
        sys.exit(0)

    results = json.loads(LINT_RESULTS.read_text())
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

    # Count total findings
    total_warnings = 0
    total_fatals = 0
    for _tool_name, data in results.get("findings", {}).items():
        if data["severity"] == "WARNING":
            total_warnings += 1
        elif data["severity"] == "FATAL":
            total_fatals += 1

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "omni-autolint-daemon",
        "type": "lint_sweep",
        "severity": "FATAL" if total_fatals > 0 else ("WARNING" if total_warnings > 0 else "CLEAN"),
        "summary": f"{total_fatals} fatal, {total_warnings} warnings across {len(results.get('findings', {}))} tools",
        "lint_timestamp": results.get("timestamp"),
        "findings": results.get("findings", {}),
        "git_diff_stats": results.get("git_diff_stats", ""),
    }

    with ISSUES_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[*] Appended lint entry to {ISSUES_FILE}")
    print(f"    Severity: {entry['severity']}")
    print(f"    Summary: {entry['summary']}")


if __name__ == "__main__":
    main()
