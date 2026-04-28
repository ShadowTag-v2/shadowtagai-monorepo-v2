#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import subprocess
import sys


def run_linter(path="."):
    print(f"Running Ruff on {path}...")
    # Check
    result = subprocess.run(["ruff", "check", path], capture_output=True, text=True)

    error_count = len(result.stdout.splitlines())
    print(f"Found {error_count} potential issues.")

    if error_count == 0:
        print("✅ Clean.")
        return

    if error_count < 5:
        print("🛠️  Auto-fixing...")
        subprocess.run(["ruff", "check", "--fix", path])
        print("✅ Fixed.")
    else:
        print("⚠️  High error count. Manual review recommended.")
        # In a real agent loop, this would trigger Judge 6
        sys.exit(1)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_linter(target)
