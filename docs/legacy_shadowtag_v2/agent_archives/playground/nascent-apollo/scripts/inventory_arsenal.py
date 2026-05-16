# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import shutil
from collections import defaultdict

"""
Antigravity Arsenal Inventory
Scans the codebase for high-value scripts and centralizes them.
Mode: LIVE FIRE
"""

TARGET_EXTENSIONS: set[str] = {".py", ".sh", ".js", ".ts", ".go", ".rs"}
IGNORE_DIRS: set[str] = {"node_modules", ".git", ".venv", "__pycache__", "dist", "libs/arsenal_recovered"}
ROOT_DIR: str = "."
DEST_DIR: str = "libs/arsenal_recovered"
KEYWORDS: list[str] = ["deploy", "migrate", "setup", "fix", "restore", "pipeline", "judge"]


def scan_and_harvest() -> None:
    """Scans root directory for high-value operational scripts."""
    print(">>> 🛰️  INITIATING DEEP SCAN & HARVEST...")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    stats = defaultdict(int)
    total = 0
    harvested = 0

    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        # In-place filtering of directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in TARGET_EXTENSIONS:
                stats[ext] += 1
                total += 1

                # HARVEST HIGH VALUE TARGETS
                if any(k in file.lower() for k in KEYWORDS):
                    src_path = os.path.join(root, file)
                    clean_name = f"{os.path.basename(root)}_{file}"
                    dst_path = os.path.join(DEST_DIR, clean_name)
                    try:
                        shutil.copy2(src_path, dst_path)
                        harvested += 1
                        print(f"    🔹 Recovered: {clean_name}")
                    except Exception as e:
                        print(f"    ⚠️ Failed to copy {file}: {e}")

    print(f"\n>>> 📊 TOTAL SCRIPTS: {total}")
    print(f">>> ✅ HARVESTED: {harvested} Weapons to {DEST_DIR}")


if __name__ == "__main__":
    scan_and_harvest()
