#!/usr/bin/env python3
"""Mass subtree merge for ehanc69 fold-in.

Merges all repos from third_party/ehanc69-fold-staging/ into the monorepo
using git subtree add --squash. Respects DRY_RUN environment variable.

Staging prefix: third_party/ehanc69-fold-staging/<repo>/
Target prefix:  third_party/ehanc69/<repo>/

Usage:
  DRY_RUN=true  python3 scripts/mass_subtree_merge.py   # list only
  DRY_RUN=false python3 scripts/mass_subtree_merge.py   # merge + commit
"""

import os
import subprocess
import sys
from pathlib import Path

STAGING_DIR = Path("third_party/ehanc69-fold-staging")
TARGET_PREFIX = "third_party/ehanc69"
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() in ("true", "1", "yes")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return result."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_staged_repos() -> list[str]:
    """Return sorted list of repo dirs in staging."""
    if not STAGING_DIR.exists():
        print(f"ERROR: Staging dir {STAGING_DIR} does not exist.")
        sys.exit(1)
    repos = sorted(
        d.name
        for d in STAGING_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    return repos


def merge_repo(repo_name: str) -> bool:
    """Merge a single repo via subtree read-tree + commit (squash-equivalent).

    We avoid `git subtree add` because it requires a remote ref. Instead we:
    1. Read the staging tree into the target prefix
    2. Commit with a squash-style message
    """
    staging_path = STAGING_DIR / repo_name
    target_path = Path(TARGET_PREFIX) / repo_name

    if target_path.exists():
        print(f"  SKIP (already merged): {target_path}")
        return True

    if DRY_RUN:
        print(f"  DRY_RUN: would merge {staging_path} → {target_path}")
        return True

    # Remove .git from the staging clone so we can add it as plain files
    staging_git = staging_path / ".git"
    if staging_git.exists():
        import shutil
        shutil.rmtree(staging_git)

    # Create target dir and copy files
    target_path.mkdir(parents=True, exist_ok=True)
    import shutil
    for item in staging_path.iterdir():
        dest = target_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # Stage the new files
    result = run(["git", "add", str(target_path)], check=False)
    if result.returncode != 0:
        print(f"  ERROR staging {repo_name}: {result.stderr}")
        return False

    # Commit with squash-style message
    result = run(
        [
            "git", "commit", "-m",
            f"fold-in: squash-merge ehanc69/{repo_name} → {target_path}\n\n"
            f"Source: https://github.com/ehanc69/{repo_name}\n"
            f"Method: copy + squash (single commit, no history)",
        ],
        check=False,
    )
    if result.returncode != 0:
        # Might be empty (no new files)
        if "nothing to commit" in result.stdout + result.stderr:
            print(f"  SKIP (no new files): {repo_name}")
            return True
        print(f"  ERROR committing {repo_name}: {result.stderr}")
        return False

    return True


def main() -> None:
    print("=== ehanc69 Mass Subtree Merge ===")
    print(f"  Staging: {STAGING_DIR}")
    print(f"  Target:  {TARGET_PREFIX}/")
    print(f"  DRY_RUN: {DRY_RUN}")
    print()

    repos = get_staged_repos()
    print(f"Found {len(repos)} repos in staging:")
    for r in repos:
        print(f"  - {r}")
    print()

    success = 0
    fail = 0
    skip = 0

    for repo in repos:
        print(f"[{repos.index(repo) + 1}/{len(repos)}] {repo}")
        result = merge_repo(repo)
        if result:
            success += 1
        else:
            fail += 1

    print()
    print(f"=== Complete: {success} merged, {fail} failed, {skip} skipped ===")

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
