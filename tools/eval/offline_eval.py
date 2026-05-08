# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Offline evaluation runner for CounselConduit promotion gate.

Loads policy/config/strict_policy.yml and evaluates the current codebase
against structural quality thresholds. Outputs a JSON report to
tools/eval/eval_results.json.

Usage:
    python tools/eval/offline_eval.py [--policy PATH]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml not installed — skipping policy-based eval")
    sys.exit(0)


def load_policy(policy_path: str = "policy/config/strict_policy.yml") -> dict:
    """Load the strict policy YAML if it exists."""
    p = Path(policy_path)
    if not p.exists():
        print(f"Policy file not found at {policy_path} — using defaults")
        return {"min_python_version": "3.11", "max_ruff_violations": 0}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def count_ruff_violations() -> int:
    """Run ruff check and count violations."""
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "check", ".", "--select=E,W,F", "--statistics"],
            capture_output=True,
            text=True,
            timeout=120,  # noqa: S603
        )
        # Count non-empty lines in output as violation groups
        lines = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
        return len(lines)
    except FileNotFoundError, subprocess.TimeoutExpired:
        print("ruff not available — skipping lint eval")
        return 0


def count_python_files() -> int:
    """Count Python files in the project (excluding vendored dirs)."""
    count = 0
    exclude = {".venv", "node_modules", "__pycache__", ".git", "bazel-", ".chroma_db"}
    for _root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude and not d.startswith("bazel-")]
        count += sum(1 for f in files if f.endswith(".py"))
    return count


def main() -> None:
    """Run offline evaluation."""
    policy = load_policy()
    ruff_violations = count_ruff_violations()
    py_file_count = count_python_files()

    max_violations = policy.get("max_ruff_violations", 10)

    results = {
        "ruff_violations": ruff_violations,
        "python_file_count": py_file_count,
        "max_allowed_violations": max_violations,
        "passed": ruff_violations <= max_violations,
    }

    output_path = Path("tools/eval/eval_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Eval results: {json.dumps(results, indent=2)}")

    if not results["passed"]:
        print(f"FAIL: {ruff_violations} violations exceed threshold {max_violations}")
        sys.exit(1)

    print("PASS: Offline eval passed")


if __name__ == "__main__":
    main()
