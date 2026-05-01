"""Git operation detection from bash command + output text.

Parses commit SHAs, push refs, branch actions, and PR URLs from the combined
stdout/stderr of git CLI invocations. Used by the collapse engine to surface
"committed abc123, created PR #42" in the collapsed summary.

Ported from: Claude Code tools/shared/gitOperationTracking.ts
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .types import BranchAction, CommitKind, PrAction

__all__ = [
    "detect_git_operation",
    "GitOperationResult",
]

# --- Regex patterns ---

# `git commit` output: "[main abc1234] Fix bug"
_COMMIT_RE = re.compile(r"\[(?:\S+)\s+([0-9a-f]{7,40})\]")
# `git commit --amend` output: "[main abc1234] Fix bug" (same pattern)
_AMEND_RE = re.compile(r"--amend")

# `git push` output: "To github.com:org/repo.git\n   abc1234..def5678  main -> main"
_PUSH_REF_RE = re.compile(r"([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\s+(\S+)\s+->\s+(\S+)")

# `git branch` / `git checkout -b`
_BRANCH_CREATE_RE = re.compile(r"Switched to a new branch '([^']+)'")
_BRANCH_DELETE_RE = re.compile(r"Deleted branch (\S+)")
_BRANCH_CHECKOUT_RE = re.compile(r"Switched to branch '([^']+)'")

# PR creation (GitHub CLI / hub)
_PR_URL_RE = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+/pull/(\d+)")


@dataclass
class CommitInfo:
    """Information about a detected commit."""

    sha: str
    kind: CommitKind


@dataclass
class PushInfo:
    """Information about a detected push."""

    branch: str


@dataclass
class BranchInfo:
    """Information about a branch action."""

    ref: str
    action: BranchAction


@dataclass
class PrInfo:
    """Information about a PR action."""

    number: int
    url: str | None = None
    action: PrAction = PrAction.CREATE


@dataclass
class GitOperationResult:
    """Aggregated result from scanning a command + its output."""

    commit: CommitInfo | None = None
    push: PushInfo | None = None
    branch: BranchInfo | None = None
    pr: PrInfo | None = None


def detect_git_operation(command: str, output: str) -> GitOperationResult:
    """Scan a bash command string + its combined output for git operations.

    Args:
        command: The original shell command string.
        output: Combined stdout + stderr from the command.

    Returns:
        A :class:`GitOperationResult` with populated fields for any
        detected operations.
    """
    result = GitOperationResult()

    # --- Commit detection ---
    commit_match = _COMMIT_RE.search(output)
    if commit_match:
        sha = commit_match.group(1)
        kind = CommitKind.AMEND if _AMEND_RE.search(command) else CommitKind.REGULAR
        # Detect merge commits
        if "merge" in command.lower():
            kind = CommitKind.MERGE
        result.commit = CommitInfo(sha=sha, kind=kind)

    # --- Push detection ---
    push_match = _PUSH_REF_RE.search(output)
    if push_match:
        branch = push_match.group(4)  # remote branch name
        result.push = PushInfo(branch=branch)

    # --- Branch detection ---
    create_match = _BRANCH_CREATE_RE.search(output)
    if create_match:
        result.branch = BranchInfo(ref=create_match.group(1), action=BranchAction.CREATE)
    else:
        delete_match = _BRANCH_DELETE_RE.search(output)
        if delete_match:
            result.branch = BranchInfo(
                ref=delete_match.group(1), action=BranchAction.DELETE
            )
        else:
            checkout_match = _BRANCH_CHECKOUT_RE.search(output)
            if checkout_match:
                result.branch = BranchInfo(
                    ref=checkout_match.group(1), action=BranchAction.CHECKOUT
                )

    # --- PR detection ---
    pr_match = _PR_URL_RE.search(output)
    if pr_match:
        result.pr = PrInfo(
            number=int(pr_match.group(1)),
            url=pr_match.group(0),
            action=PrAction.CREATE,
        )

    return result
