# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess
import concurrent.futures

SOURCE_LIST_FILE = "/Users/pikeymickey/.gemini/antigravity/brain/8239360b-eff1-4b3e-821e-33f09db476b3/REPOS.md"
TARGET_BASE_DIR = "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/vendor"
MAX_WORKERS = 10
LOG_FILE = "migration_parallel.log"

SKIP_LIST = {"xla", "rumdl"}


def migrate_repo(repo_path):
    repo_path = repo_path.strip()
    if not repo_path:
        return

    dirname = os.path.basename(repo_path)

    if dirname in SKIP_LIST:
        return f"SKIPPED {dirname} (Heavy)"

    target_dir = os.path.join(TARGET_BASE_DIR, dirname)

    # Check if already done (simple check)
    if os.path.exists(target_dir):
        # We assume if dir exists, it's started/done. To be safe we could re-run but skipping for speed
        return f"SKIPPED {dirname} (Exists)"

    os.makedirs(target_dir, exist_ok=True)

    cmd = [
        "rsync",
        "-a",
        "--exclude=.git",
        "--exclude=node_modules",
        "--exclude=__pycache__",
        "--exclude=.DS_Store",
        "--exclude=.next",
        f"{repo_path}/",
        f"{target_dir}/",
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"MIGRATED {dirname}"
    except subprocess.CalledProcessError:
        return f"FAILED {dirname}"


def main():
    if not os.path.exists(SOURCE_LIST_FILE):
        print(f"File not found: {SOURCE_LIST_FILE}")
        return

    with open(SOURCE_LIST_FILE) as f:
        repos = [line.strip() for line in f if line.strip()]

    total = len(repos)
    print(f"Starting parallel migration of {total} repos with {MAX_WORKERS} workers...")

    with open(LOG_FILE, "a") as log:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all
            future_to_repo = {executor.submit(migrate_repo, repo): repo for repo in repos}

            completed = 0
            for future in concurrent.futures.as_completed(future_to_repo):
                result = future.result()
                completed += 1
                if result:
                    msg = f"[{completed}/{total}] {result}"
                    print(msg)
                    log.write(msg + "\n")
                    log.flush()  # Force write


if __name__ == "__main__":
    main()
