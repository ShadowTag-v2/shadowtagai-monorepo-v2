#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import re
import sys
from pathlib import Path

# The Philosophy Check (The Gentle Stop Hook)
# Scans for "Risky Patterns" - technically correct but strategically stupid.

DEFAULT_PATTERNS = [
    (r"cursor\.execute\(", "WARNING: Raw SQL detected. Use the ORM."),
    (r"except Exception:", "WARNING: Too broad exception clause. Catch specific errors."),
    (r"print\(", "WARNING: Use a logger instead of print()."),
    (r"pdb\.set_trace", "WARNING: Debugger breakpoint left in code."),
]


def check_file(file_path):
    issues = []
    try:
        path = Path(file_path)
        if not path.is_file():
            return []

        content = path.read_text(encoding="utf-8", errors="ignore")

        for pattern, msg in DEFAULT_PATTERNS:
            if re.search(pattern, content):
                issues.append(msg)
    except Exception:
        # Ignore read errors for now (binary files, etc)
        pass
    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: philosophy_check.py <file1> <file2> ...")
        sys.exit(0)

    found_issues = False
    for f in sys.argv[1:]:
        issues = check_file(f)
        if issues:
            found_issues = True
            print(f"[Philosophy Check] {f}:")
            for i in issues:
                print(f"  - {i}")
            print("-" * 40)

    if found_issues:
        sys.exit(1)  # Signal failure to hooks if needed
