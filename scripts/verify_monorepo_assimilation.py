#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
verify_monorepo_assimilation.py
Verifies that all migrated codebases have been properly assimilated into the
canonical monorepo structure, ensuring no nested .git states exist and core
manifests are present.
"""

import sys
from pathlib import Path


def verify_assimilation():
    root_dir = Path(__file__).resolve().parent.parent
    print("=== Monorepo Assimilation Verification ===")
    print(f"Target Root: {root_dir}")
    print("-" * 40)

    issues = 0

    # 1. Check Core Directories
    core_dirs = ["apps", "libs", "scripts", "tools", "docs"]
    missing_dirs = []
    for d in core_dirs:
        if not (root_dir / d).is_dir():
            missing_dirs.append(d)

    if missing_dirs:
        print(f"❌ FAILED: Missing core directories: {', '.join(missing_dirs)}")
        issues += 1
    else:
        print("✅ Core directories present: ", ", ".join(core_dirs))

    # 2. Check for nested .git directories (which would indicate broken assimilation)
    nested_gits = []
    for d in ["apps", "libs"]:
        search_path = root_dir / d
        if search_path.exists():
            for sub in search_path.iterdir():
                if sub.is_dir() and (sub / ".git").exists():
                    nested_gits.append(str(sub.relative_to(root_dir)))

    if nested_gits:
        print(f"❌ FAILED: Found nested .git repositories (unassimilated modules): {', '.join(nested_gits)}")
        issues += 1
    else:
        print("✅ No nested .git repositories found in apps/ or libs/. Assimilation clean.")

    # 3. Check for Pyright isolation (performance)
    if not (root_dir / "pyrightconfig.json").exists():
        print("⚠️ WARNING: pyrightconfig.json missing. Type checking may scan external/vendor folders.")
    else:
        print("✅ Pyright isolation config (`pyrightconfig.json`) is present.")

    # 4. Check for Makefile hook
    if not (root_dir / "Makefile").exists():
        print("⚠️ WARNING: Root Makefile missing.")
    else:
        print("✅ Root Makefile is present.")

    print("-" * 40)
    if issues > 0:
        print(f"🧨 Verification FAILED with {issues} critical structural errors.")
        sys.exit(1)
    else:
        print("🚀 Monorepo Assimilation Verification: PASSED 10/10")
        sys.exit(0)


if __name__ == "__main__":
    verify_assimilation()
