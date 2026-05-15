# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Plugin Installation Manager — core implementation.

Ported from Claude Code v2.1.91 services/plugins/PluginInstallationManager.ts.
Adapted for AGNT's skill fleet architecture.
"""

from __future__ import annotations

import logging
import pathlib
import subprocess
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from collections.abc import Callable

logger = logging.getLogger("plugin_manager")


class InstallationStatus(StrEnum):
  """Per-marketplace installation status."""

  PENDING = "pending"
  INSTALLING = "installing"
  INSTALLED = "installed"
  FAILED = "failed"
  UP_TO_DATE = "up_to_date"


@dataclass(slots=True)
class MarketplaceStatus:
  """Status for a single marketplace/skill source.

  Attributes:
      name: Marketplace or skill source identifier.
      status: Current installation status.
      error: Error message if status is FAILED.
      source: Source URL or path.
      updated_at: Unix timestamp of last status change.
  """

  name: str
  status: InstallationStatus = InstallationStatus.PENDING
  error: str = ""
  source: str = ""
  updated_at: float = 0.0

  def __post_init__(self) -> None:
    if self.updated_at == 0.0:
      self.updated_at = time.time()


@dataclass(slots=True)
class ReconciliationResult:
  """Result of a marketplace reconciliation run.

  Attributes:
      installed: Names of newly installed marketplaces.
      updated: Names of updated marketplaces.
      failed: Names of marketplaces that failed.
      up_to_date: Names of marketplaces already up to date.
      duration_ms: Total reconciliation duration in milliseconds.
  """

  installed: list[str] = field(default_factory=list)
  updated: list[str] = field(default_factory=list)
  failed: list[str] = field(default_factory=list)
  up_to_date: list[str] = field(default_factory=list)
  duration_ms: float = 0.0


# Type for progress callbacks
ProgressCallback = Callable[[str, str, str | None], None]


class PluginInstallationManager:
  """Background plugin/marketplace installation manager.

  Handles automatic installation and reconciliation of skill sources
  (external repos, marketplaces) without blocking daemon startup.

  Args:
      skills_dir: Root directory for installed skills.
      external_repos_dir: Directory for cloned external repos.
  """

  def __init__(
    self,
    skills_dir: str | pathlib.Path,
    external_repos_dir: str | pathlib.Path,
  ) -> None:
    self.skills_dir = pathlib.Path(skills_dir)
    self.external_repos_dir = pathlib.Path(external_repos_dir)
    self._statuses: dict[str, MarketplaceStatus] = {}
    self._on_progress: ProgressCallback | None = None

  def set_progress_callback(self, callback: ProgressCallback) -> None:
    """Set callback for installation progress updates.

    Callback signature: (name, status, error_msg) -> None
    """
    self._on_progress = callback

  def _emit_progress(self, name: str, status: str, error: str | None = None) -> None:
    """Emit a progress event."""
    if name in self._statuses:
      self._statuses[name].status = InstallationStatus(status)
      self._statuses[name].error = error or ""
      self._statuses[name].updated_at = time.time()

    if self._on_progress:
      self._on_progress(name, status, error)

  def get_declared_marketplaces(self) -> list[dict[str, Any]]:
    """Get declared marketplace sources from config.

    In Claude Code, this reads from user settings and repo config.
    In AGNT, this reads from the monorepo manifest and skill fleet.
    """
    declared: list[dict[str, Any]] = []

    # Google skills
    google_skills = self.external_repos_dir / "google-skills"
    if google_skills.exists():
      declared.append(
        {
          "name": "google-skills",
          "source": "https://github.com/google/skills",
          "path": str(google_skills),
        }
      )

    # Vercel skills
    vercel_skills = self.external_repos_dir / "vercel-skills"
    if vercel_skills.exists():
      declared.append(
        {
          "name": "vercel-skills",
          "source": "https://github.com/vercel-labs/skills",
          "path": str(vercel_skills),
        }
      )

    return declared

  def diff_marketplaces(
    self,
    declared: list[dict[str, Any]],
  ) -> tuple[list[str], list[str], list[str]]:
    """Compute diff between declared and installed marketplaces.

    Returns:
        (missing, changed, up_to_date) marketplace names.
    """
    missing: list[str] = []
    changed: list[str] = []
    up_to_date: list[str] = []

    for mp in declared:
      path = pathlib.Path(mp.get("path", ""))
      if not path.exists():
        missing.append(mp["name"])
      elif not (path / ".git").exists():
        changed.append(mp["name"])
      else:
        up_to_date.append(mp["name"])

    return missing, changed, up_to_date

  def _clone_marketplace(self, name: str, source: str) -> bool:
    """Clone a marketplace repository.

    Args:
        name: Marketplace name.
        source: Git clone URL.

    Returns:
        True if successful.
    """
    target = self.external_repos_dir / name
    self.external_repos_dir.mkdir(parents=True, exist_ok=True)

    try:
      self._emit_progress(name, "installing")
      result = subprocess.run(
        ["git", "clone", "--depth=1", source, str(target)],
        capture_output=True,
        text=True,
        timeout=120,
      )
      if result.returncode == 0:
        self._emit_progress(name, "installed")
        return True
      self._emit_progress(name, "failed", result.stderr[:500])
      return False
    except subprocess.TimeoutExpired:
      self._emit_progress(name, "failed", "Clone timed out (120s)")
      return False
    except FileNotFoundError:
      self._emit_progress(name, "failed", "git not found")
      return False

  def _update_marketplace(self, name: str, path: str) -> bool:
    """Pull latest changes for an existing marketplace.

    Args:
        name: Marketplace name.
        path: Local filesystem path.

    Returns:
        True if successful.
    """
    try:
      self._emit_progress(name, "installing")
      result = subprocess.run(
        ["git", "pull", "--ff-only"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=path,
      )
      if result.returncode == 0:
        self._emit_progress(name, "installed")
        return True
      self._emit_progress(name, "failed", result.stderr[:500])
      return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
      self._emit_progress(name, "failed", str(e))
      return False

  def reconcile(
    self,
    on_progress: ProgressCallback | None = None,
  ) -> ReconciliationResult:
    """Reconcile all declared marketplaces.

    Installs missing marketplaces, updates changed ones, and reports
    overall status.

    Args:
        on_progress: Optional progress callback override.

    Returns:
        ReconciliationResult with counts and timing.
    """
    if on_progress:
      self._on_progress = on_progress

    start = time.monotonic()
    declared = self.get_declared_marketplaces()

    # Initialize statuses
    for mp in declared:
      self._statuses[mp["name"]] = MarketplaceStatus(
        name=mp["name"],
        source=mp.get("source", ""),
      )

    missing, changed, up_to_date = self.diff_marketplaces(declared)
    result = ReconciliationResult(up_to_date=up_to_date)

    # Install missing
    for name in missing:
      mp = next((m for m in declared if m["name"] == name), None)
      if mp and mp.get("source"):
        if self._clone_marketplace(name, mp["source"]):
          result.installed.append(name)
        else:
          result.failed.append(name)
      else:
        result.failed.append(name)

    # Update changed
    for name in changed:
      mp = next((m for m in declared if m["name"] == name), None)
      if mp and mp.get("path"):
        if self._update_marketplace(name, mp["path"]):
          result.updated.append(name)
        else:
          result.failed.append(name)

    result.duration_ms = (time.monotonic() - start) * 1000
    logger.info(
      "Reconciliation complete: %d installed, %d updated, %d failed, %d up-to-date (%.0fms)",
      len(result.installed),
      len(result.updated),
      len(result.failed),
      len(result.up_to_date),
      result.duration_ms,
    )
    return result

  def get_statuses(self) -> list[MarketplaceStatus]:
    """Get current installation statuses for all tracked marketplaces."""
    return list(self._statuses.values())

  def clear_caches(self) -> None:
    """Clear marketplace and plugin caches.

    In Claude Code, this calls clearMarketplacesCache() and clearPluginCache().
    In AGNT, this clears the skill cache in preparation for reload.
    """
    self._statuses.clear()
    logger.info("Plugin/marketplace caches cleared")
