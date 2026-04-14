"""ANTIGRAVITY :: GOD MODE :: ARSENAL INVENTORY
Classification: TIER 30 SOVEREIGN
Context: 1M+
"""

import os
import shutil
from collections import defaultdict

TARGET_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".go", ".rs"}
IGNORE_DIRS = {"node_modules", ".git", ".venv", "__pycache__", "dist", "libs/arsenal_recovered"}
ROOT_DIR = "."
DEST_DIR = "libs/arsenal_recovered"
KEYWORDS = ["deploy", "migrate", "setup", "fix", "restore", "pipeline", "judge"]


def scan_and_harvest():
    print(">>> 🛰️  INITIATING DEEP SCAN & HARVEST...")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    stats = defaultdict(int)
    total = 0
    harvested = 0

    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
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
                    except Exception:
                        pass

    print(f"\n>>> 📊 TOTAL SCRIPTS: {total}")
    print(f">>> ✅ HARVESTED: {harvested} Weapons to {DEST_DIR}")


if __name__ == "__main__":
    scan_and_harvest()
