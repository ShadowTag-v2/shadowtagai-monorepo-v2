"""
Fork Status Utility for n-autoresearch/Kosmos/BioAgents
Reports on the status (sync, existence) of repositories in external_repos.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

# Adjust path to import from scripts if needed, or define the list here if simpler.
# Attempting to load dynamic config from scripts/fork_repos.py
try:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    scripts_dir = project_root / "scripts"
    sys.path.append(str(scripts_dir))
    # pyright: reportMissingImports=false
    from fork_repos import REPOS_TO_FORK, get_repo_name  # type: ignore
except ImportError:
    # Fallback list if import fails
    REPOS_TO_FORK = [
        "https://github.com/deepseek-ai/LPLB",
        "https://github.com/opentimestamps/opentimestamps-client",
        # ... (truncated for brevity, logic handles dynamic scanning too)
    ]

    def get_repo_name(url: str) -> str:
        return url.split("/")[-1].replace(".git", "")


def get_git_status(repo_path: Path) -> dict[str, Any]:
    """Get git status for a repo."""
    if not (repo_path / ".git").exists():
        return {"status": "missing_git", "is_git": False}

    status: dict[str, Any] = {"is_git": True}

    try:
        # Get remote info
        remote = subprocess.check_output(
            ["git", "remote", "-v"], cwd=repo_path, text=True, stderr=subprocess.DEVNULL
        )
        status["remotes"] = remote.strip().split("\n")
    except subprocess.CalledProcessError:
        status["remotes_error"] = True

    try:
        # Get ahead/behind counts if upstream exists
        # Assuming upstream is named 'upstream' or 'origin' - let's check HEAD vs origin/main
        # First check current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, text=True
        ).strip()
        status["branch"] = branch

        # Check status (clean/dirty)
        git_status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_path, text=True
        ).strip()
        status["dirty"] = bool(git_status)

    except subprocess.CalledProcessError:
        status["git_check_error"] = True

    return status


def get_all_fork_statuses(root_path: Path | None = None) -> list[dict[str, Any]]:
    """Scan repositories and return their status."""
    if root_path is None:
        # Default to project_root/external_repos
        # We need to find project root relative to this file: src/fork_status.py
        # src/fork_status.py -> src -> shadowtag_v4-fastapi-services
        root_path = Path(__file__).parent.parent / "external_repos"

    results: list[dict[str, Any]] = []

    # 1. Check strict list (REPOS_TO_FORK)
    for url in REPOS_TO_FORK:
        name = get_repo_name(url)
        repo_path = root_path / name
        exists = repo_path.exists()

        repo_data: dict[str, Any] = {
            "name": name,
            "url": url,
            "exists": exists,
            "path": str(repo_path),
        }

        if exists:
            repo_data.update(get_git_status(repo_path))

        results.append(repo_data)

    # 2. Check for extra folders in root_path not in REPOS_TO_FORK
    if root_path.exists():
        known_names = {r["name"] for r in results}
        for item in root_path.iterdir():
            if item.is_dir() and item.name not in known_names:
                # Add existing directory that wasn't in list
                repo_data = {
                    "name": item.name,
                    "url": "unknown",
                    "exists": True,
                    "path": str(item),
                    "extra": True,
                }
                repo_data.update(get_git_status(item))
                results.append(repo_data)

    return results
