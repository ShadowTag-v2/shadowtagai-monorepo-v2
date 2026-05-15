"""Repo classification — internal vs external repository detection.

Determines whether the current working directory is an "internal" (private,
allowlisted) repository or an "external" (public/open-source) one. This
classification drives :func:`undercover.is_undercover` to decide whether
model codenames and internal attribution should be stripped.

Ported from: Claude Code utils/commitAttribution.ts (repo classification only)
"""

from __future__ import annotations

import functools
import subprocess
from pathlib import Path
from typing import Literal

__all__ = [
  "RepoClass",
  "get_repo_class",
  "is_internal_repo",
  "classify_remote_url",
  "INTERNAL_REPO_PATTERNS",
]

# Type alias for the three classification states.
RepoClass = Literal["internal", "external", "none"]

# ---------------------------------------------------------------------------
# Allowlist of private repo remote URL fragments.
# NOTE: This is intentionally a repo allowlist, NOT an org-wide check.
# Some orgs host public repos — only confirmed PRIVATE repos belong here.
#
# For the AGNT framework, "internal" means repos belonging to the
# ShadowTag-v2 organisation (the canonical monorepo host).
# ---------------------------------------------------------------------------
INTERNAL_REPO_PATTERNS: list[str] = [
  # ShadowTag-v2 monorepo (SSH + HTTPS variants)
  "github.com:ShadowTag-v2/Monorepo-Uphillsnowball",
  "github.com/ShadowTag-v2/Monorepo-Uphillsnowball",
  # Add additional private repos here as needed.
]


def _find_git_root(cwd: str | Path | None = None) -> Path | None:
  """Resolve the nearest git root from *cwd* (or the process CWD)."""
  try:
    result = subprocess.run(
      ["git", "rev-parse", "--show-toplevel"],
      capture_output=True,
      text=True,
      cwd=str(cwd) if cwd else None,
      timeout=5,
    )
    if result.returncode == 0 and result.stdout.strip():
      return Path(result.stdout.strip())
  except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
    pass
  return None


def _get_remote_url(cwd: str | Path | None = None) -> str | None:
  """Return the ``origin`` remote URL for the repo at *cwd*."""
  try:
    result = subprocess.run(
      ["git", "remote", "get-url", "origin"],
      capture_output=True,
      text=True,
      cwd=str(cwd) if cwd else None,
      timeout=5,
    )
    if result.returncode == 0 and result.stdout.strip():
      return result.stdout.strip()
  except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
    pass
  return None


def classify_remote_url(
  remote_url: str | None,
  *,
  patterns: list[str] | None = None,
) -> RepoClass:
  """Classify a remote URL against the internal allowlist.

  Args:
      remote_url: The ``origin`` remote URL string (SSH or HTTPS).
      patterns: Override the default allowlist for testing.

  Returns:
      ``'internal'`` if the remote matches an allowlisted pattern,
      ``'external'`` if a remote exists but does not match,
      ``'none'`` if no remote URL was provided.
  """
  if not remote_url:
    return "none"
  allowlist = patterns if patterns is not None else INTERNAL_REPO_PATTERNS
  for pattern in allowlist:
    if pattern in remote_url:
      return "internal"
  return "external"


@functools.lru_cache(maxsize=1)
def get_repo_class(cwd: str | None = None) -> RepoClass:
  """Determine the repo classification for the current working tree.

  The result is cached per-process (``lru_cache(1)``). Priming happens
  once — subsequent calls return the cached value. The safe default is
  ``'none'`` (treated as non-internal → undercover stays ON).

  Args:
      cwd: Optional explicit working directory. Defaults to ``os.getcwd()``.

  Returns:
      The :data:`RepoClass` for the resolved git root.
  """
  git_root = _find_git_root(cwd)
  if git_root is None:
    return "none"
  remote_url = _get_remote_url(git_root)
  return classify_remote_url(remote_url)


def is_internal_repo(cwd: str | None = None) -> bool:
  """Return ``True`` iff the current repo is on the internal allowlist.

  Safe default is ``False`` — if the check hasn't run or fails, we assume
  external (don't leak).
  """
  return get_repo_class(cwd) == "internal"
