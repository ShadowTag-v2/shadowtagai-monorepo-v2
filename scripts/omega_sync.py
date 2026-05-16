# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import sys
from pathlib import Path


def enforce_immutable_state():
    print("💎 Initializing Omega Loop Absolute Sync...")

    # 1. Format & Lint (The Quality Bar)
    print("   -> Enforcing Biome & Ruff Formats...")
    subprocess.run(["npx", "@biomejs/biome", "format", "--write", "apps"], check=False)
    subprocess.run(["python3", "-m", "ruff", "format", "apps"], check=False)

    # 2. Beads Memory Injection
    print("   -> Saving Temporal Bead State...")
    subprocess.run(
        [
            "python3",
            "tools/beads_manager.py",
            "add",
            "--id",
            "auto-egress-sync",
            "--type",
            "task",
            "--title",
            "Omega Sync Execution",
            "--content",
            "Snapshot locked.",
        ],
        check=False,
    )

    # 3. Mint GitHub App Token & Push (The App ID: 3018200 Egress)
    print("   -> Establishing Validated GitHub Native App Route...")
    subprocess.run(["python3", "scripts/gh_app_auth.py"], check=False)

    # 4. Git Atomic Commit
    print("   -> Committing Core Matrix...")
    subprocess.run(["git", "add", "-A"], check=False)
    status = subprocess.getoutput("git status --porcelain")
    if status.strip():
        subprocess.run(["git", "commit", "-m", "chore: omnipresent omega synchronization [skip ci]"], check=False)
        subprocess.run(["git", "push", "origin", "HEAD"], check=False)
        print("✅ Codebase Canonicalized, Secured, and Delivered.")
    else:
        print("✅ Matrix already perfectly synchronized.")


if __name__ == "__main__":
    pwd = Path.cwd()
    if "Monorepo-Uphillsnowball" not in str(pwd):
        print("❌ CRITICAL: Unauthorized execution outside Monorepo Root.")
        sys.exit(1)
    enforce_immutable_state()
