# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import contextlib
import shutil
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:8600"
SOURCE_DIR = Path("external_repos")
TARGET_DIR = Path("src/vendor")


def check_governance(operation: str):
    print(f"⚖️  Asking Judge 6 for permission to: {operation}...")
    try:
        resp = requests.post(
            f"{BASE_URL}/risk",
            json={"query": operation, "mission_id": "MIGRATE-001"},
        )
        resp.raise_for_status()
        decision = resp.json()
        if decision.get("approved"):
            print(
                f"   ✅ APPROVED by {decision.get('authority')} (Risk: {decision.get('risk_tier')})",
            )
            return True
        print(f"   ⛔ DENIED by {decision.get('authority')}")
        return False
    except Exception as e:
        print(f"   ⚠️  Governance Offline or Error: {e}")
        # Fail safe or proceed? Let's fail safe for "God Mode" strictness.
        return False


def migrate_repos():
    if not check_governance("Migrate external repositories to Monorepo Vendor"):
        sys.exit(1)

    if not SOURCE_DIR.exists():
        print("❌ Source directory 'external_repos' not found.")
        sys.exit(1)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"📦 Migrating repos from {SOURCE_DIR} to {TARGET_DIR}...")

    count = 0
    for user_dir in SOURCE_DIR.iterdir():
        if user_dir.is_dir():
            print(f"   📂 Processing user: {user_dir.name}")
            for repo_dir in user_dir.iterdir():
                if repo_dir.is_dir():
                    # Check for incomplete downloads (e.g. tensorflow)
                    # We can use a simple heuristic or just move it.
                    # If it has a .git folder, it's likely initialized.
                    if (repo_dir / ".git").exists():
                        target_path = TARGET_DIR / repo_dir.name
                        if target_path.exists():
                            print(f"      ⚠️  Skipping {repo_dir.name} (Already exists)")
                        else:
                            # Move the directory
                            shutil.move(str(repo_dir), str(target_path))
                            print(f"      ✅ Moved {repo_dir.name}")
                            count += 1
                    else:
                        print(f"      ⚠️  Skipping {repo_dir.name} (No .git found / Incomplete)")

    print(f"\n🎉 Migration Complete. Moved {count} repositories.")

    # Generate Report via UI
    with contextlib.suppress(BaseException):
        requests.post(f"{BASE_URL}/ui", json={"intent": f"Migration Report: {count} repos moved"})


if __name__ == "__main__":
    migrate_repos()
