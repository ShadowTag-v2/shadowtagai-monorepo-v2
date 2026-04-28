# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os
from pathlib import Path

TARGET_DIR = Path(os.path.expanduser("~/antigravity-flattened"))
INDEX_FILE = TARGET_DIR / "index.json"


def get_repo_stats(repo_path):
    file_count = 0
    total_bytes = 0
    extensions = set()

    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
        for file in files:
            file_path = Path(root) / file
            if file_path.is_symlink():
                continue
            try:
                stat = file_path.stat()
                file_count += 1
                total_bytes += stat.st_size
                extensions.add(file_path.suffix)
            except (OSError, ValueError):
                pass

    return {"files": file_count, "bytes": total_bytes, "extensions": sorted(list(extensions))}


def main():
    if not INDEX_FILE.exists():
        print(f"Index file not found at {INDEX_FILE}")
        return

    try:
        with open(INDEX_FILE) as f:
            index_data = json.load(f)
    except json.JSONDecodeError:
        print("Error reading index.json")
        return

    modified = False

    # Check for new directories in TARGET_DIR
    for item in TARGET_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            repo_name = item.name
            if repo_name not in index_data["repos"]:
                print(f"Adding {repo_name} to index...")
                stats = get_repo_stats(item)
                index_data["repos"][repo_name] = stats
                modified = True
            else:
                pass  # Already indexed

    if modified:
        with open(INDEX_FILE, "w") as f:
            json.dump(index_data, f, indent=2)
        print("Updated index.json successfully.")
    else:
        print("No new repositories to index.")


if __name__ == "__main__":
    main()
