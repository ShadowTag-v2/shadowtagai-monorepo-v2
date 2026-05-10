# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Git Worktree Isolation — P1 #7 from Kairos Ultraplan.

Ported from: Claude Code src/services/worktreeIsolation.ts (inferred)

STATE B (Clutch mode) operations that modify architecture (>3 packages)
now execute in an isolated git worktree to prevent contamination of the
main working tree. This provides transactional semantics — the worktree
is either merged cleanly or discarded entirely.

Usage:
    from packages.agnt_tools.worktree_isolation import WorktreeIsolation
    iso = WorktreeIsolation()
    with iso.isolated("feat/big-refactor") as wt:
        # All work happens in wt.path
        # On success, wt.merge() brings changes back
        pass
"""

from __future__ import annotations

import logging
import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("agnt.worktree_isolation")

REPO_ROOT = Path(
    os.environ.get(
        "REPO_ROOT",
        os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball"),
    )
)
WORKTREE_DIR = REPO_ROOT / ".worktrees"


@dataclass
class WorktreeContext:
    """Context for an active worktree."""

    branch: str
    path: Path
    base_branch: str = "main"
    _merged: bool = False

    def merge(self) -> bool:
        """Merge worktree changes back to base branch."""
        try:
            # Switch to base branch
            subprocess.run(
                ["git", "checkout", self.base_branch],
                cwd=str(REPO_ROOT),
                capture_output=True,
                check=True,
            )
            # Merge
            result = subprocess.run(
                ["git", "merge", self.branch, "--no-ff", "-m", f"merge: {self.branch} (STATE B worktree)"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self._merged = result.returncode == 0
            if self._merged:
                logger.info("WorktreeIsolation: merged %s → %s", self.branch, self.base_branch)
            else:
                logger.warning("WorktreeIsolation: merge failed: %s", result.stderr[:200])
            return self._merged
        except subprocess.CalledProcessError as e:
            logger.error("WorktreeIsolation: merge error: %s", e)
            return False


class WorktreeIsolation:
    """Provide transactional git worktree isolation for STATE B operations.

    STATE B (Clutch mode) triggers when:
      - git history rewrites
      - force-pushes
      - database migrations
      - auth/payment changes
      - architecture shifts >3 packages

    This class creates an isolated worktree where dangerous changes
    execute without contaminating the main working tree.
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or REPO_ROOT

    @contextmanager
    def isolated(self, branch: str, base: str = "main"):
        """Create an isolated worktree context.

        Args:
            branch: Feature branch name for the worktree.
            base: Base branch to fork from.

        Yields:
            WorktreeContext with the worktree path.

        On context exit, the worktree is cleaned up regardless of success.
        """
        wt_path = WORKTREE_DIR / branch.replace("/", "_")
        WORKTREE_DIR.mkdir(parents=True, exist_ok=True)

        try:
            # Create branch and worktree
            subprocess.run(
                ["git", "branch", branch, base],
                cwd=str(self.repo_root),
                capture_output=True,
            )
            subprocess.run(
                ["git", "worktree", "add", str(wt_path), branch],
                cwd=str(self.repo_root),
                capture_output=True,
                check=True,
            )
            logger.info("WorktreeIsolation: created worktree at %s", wt_path)

            ctx = WorktreeContext(branch=branch, path=wt_path, base_branch=base)
            yield ctx

        finally:
            # Cleanup worktree
            subprocess.run(
                ["git", "worktree", "remove", str(wt_path), "--force"],
                cwd=str(self.repo_root),
                capture_output=True,
            )
            logger.info("WorktreeIsolation: removed worktree %s", wt_path)

    def list_worktrees(self) -> list[str]:
        """List active worktrees."""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        worktrees = []
        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                worktrees.append(line.split(" ", 1)[1])
        return worktrees
