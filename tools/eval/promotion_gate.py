# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Promotion gate — blocks PR merge if offline eval results are below threshold.

Reads tools/eval/eval_results.json and exits non-zero if the eval failed.

Usage:
    python tools/eval/promotion_gate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    """Check promotion gate from eval results."""
    results_path = Path("tools/eval/eval_results.json")

    if not results_path.exists():
        print("No eval results found — run offline_eval.py first")
        print("Promotion gate: SKIPPED (no results)")
        sys.exit(0)

    with open(results_path) as f:
        results = json.load(f)

    passed = results.get("passed", False)
    violations = results.get("ruff_violations", "unknown")
    threshold = results.get("max_allowed_violations", "unknown")

    if passed:
        print(f"Promotion gate: PASSED ({violations} violations, threshold {threshold})")
        sys.exit(0)
    else:
        print(f"Promotion gate: BLOCKED ({violations} violations exceed threshold {threshold})")
        sys.exit(1)


if __name__ == "__main__":
    main()
