# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import os
import subprocess
import tarfile

# CONFIGURATION
ROOT_DIR = "."
ARCHIVE_DIR = "Legacy_Archives/Recovery_Snapshots"
IGNORE_DIRS = {".git", ".venv", "__pycache__", "node_modules"}


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def scroll_tree():
    print(">>> 📜 SCROLLING THE TREE (Deep Audit)...")

    # 1. Get Git Status
    git_status = run_command("git status --porcelain")
    if not git_status:
        print("    ✅ Git Tree is Clean. No ghosts found.")
        return

    print("    ⚠️  DIRTY STATE DETECTED (The '2-3 Day Old' Changes):")
    lines = git_status.split("\n")
    for line in lines:
        print(f"       {line}")

    # 2. The Safety Net (Archive the Ghosts)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"ghost_state_{timestamp}.tar.gz"
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    print(f"\n>>> 📦 ARCHIVING DIRTY STATE to {ARCHIVE_DIR}/{archive_name}...")

    with tarfile.open(os.path.join(ARCHIVE_DIR, archive_name), "w:gz") as tar:
        for line in lines:
            # line format: " M src/file.py" or "?? new_file.py"
            file_path = line[3:]
            if os.path.exists(file_path):
                tar.add(file_path)

    print("    ✅ Archive Complete. We are safe to overwrite.")


if __name__ == "__main__":
    scroll_tree()
