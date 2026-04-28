#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
FINISH CHANGES (The "Janitor")
====================================
Role: Lints, formats, stages, and commits all changes in the workspace.
Trigger: User Alias `f1 gca` or `/omega-loop`
Monorepo Matrix: TypeScript + Python (Bazel)
"""

import argparse
import subprocess
import sys


def run_cmd(cmd: list, check: bool = True):
    print(f"\n[Janitor] Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=check, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[Janitor] ERROR: Command failed with exit code {e.returncode}")
        print(f"[Janitor] Command: {' '.join(cmd)}")
        if check:
            sys.exit(1)


def check_git_status() -> bool:
    """Returns True if there are changes to commit."""
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return bool(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="The Janitor: Lints, formats, stages, and commits all changes.")
    parser.add_argument("-m", "--message", help="Commit message.")
    args = parser.parse_args()

    print("====================================")
    print(" 🧹 THE JANITOR / OMEGA-LOOP INIT")
    print("====================================\n")

    if not check_git_status():
        print("[Janitor] Workspace is clean. No changes to sweep.")
        sys.exit(0)

    # 1. Formatting Phase (The Boy Scout Rule)
    print("--- Phase 1: Formatting ---")
    # For a Bazel monorepo, buildifier is standard for BUILD files.
    # We use our local bazelisk binary wrapper to ensure we hit the correct compiler version.
    run_cmd(["./tools/bazel", "run", "//:buildifier"], check=False)

    # We will add generic fallbacks if Bazel tools aren't available yet.
    # Note: These are 'best effort' formats if the tools are in the path.
    # In a fully fleshed matrix, we'd invoke bazel run //:format directly.
    run_cmd(["npx", "prettier", "--write", "."], check=False)  # TS/JS/JSON/MD
    run_cmd(["black", "."], check=False)  # Python

    # 2. Linting Phase
    print("\n--- Phase 2: Linting ---")
    print("[Janitor] Executing: npx eslint --fix .")
    run_cmd(["npx", "eslint", "--fix", "."], check=False)

    # 3. Git Staging
    print("\n--- Phase 3: Staging ---")
    run_cmd(["git", "add", "."])

    # 4. Git Committing
    print("\n--- Phase 4: Committing ---")
    commit_msg = args.message if args.message else "chore: atomic agent commit"
    run_cmd(["git", "commit", "-m", commit_msg])

    print("\n====================================")
    print(" 🎉 OMEGA-LOOP COMPLETE. Clean slate.")
    print("====================================")


if __name__ == "__main__":
    main()
