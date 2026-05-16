# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Settings Sync Service — Batch 6 port from Claude Code v2.1.91.

Syncs user settings and memory files across environments.
Adapted from OAuth-based remote sync to Firestore-backed sync.

Ported from: external_repos/claude_code_services/settingsSync/index.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500KB per file (matches CC backend limit)


class SyncKey(StrEnum):
  """Known sync keys for settings synchronization."""

  USER_SETTINGS = "user_settings"
  USER_MEMORY = "user_memory"

  @staticmethod
  def project_settings(project_id: str) -> str:
    """Generate a project-specific settings key."""
    return f"project_settings:{project_id}"

  @staticmethod
  def project_memory(project_id: str) -> str:
    """Generate a project-specific memory key."""
    return f"project_memory:{project_id}"


@dataclass(frozen=True, slots=True)
class SyncResult:
  """Result of a sync operation."""

  success: bool
  error: str | None = None
  entries_synced: int = 0


@dataclass
class SettingsSyncService:
  """Manages settings synchronization between local and remote storage.

  This is the Python equivalent of Claude Code's settingsSync module.
  The CC version uses OAuth + Anthropic API; this version uses Firestore
  or local file-based sync as the backend.
  """

  _local_entries: dict[str, str] = field(default_factory=dict)
  _remote_entries: dict[str, str] = field(default_factory=dict)
  _sync_enabled: bool = True

  def build_entries_from_local(
    self,
    user_settings_path: Path | None = None,
    user_memory_path: Path | None = None,
    project_id: str | None = None,
    local_settings_path: Path | None = None,
    local_memory_path: Path | None = None,
  ) -> dict[str, str]:
    """Build sync entries from local files.

    Args:
        user_settings_path: Path to global user settings.
        user_memory_path: Path to global user memory.
        project_id: Git remote hash for project-scoped entries.
        local_settings_path: Path to project-local settings.
        local_memory_path: Path to project-local memory.

    Returns:
        Dict of sync_key → file_content for all readable files.
    """
    entries: dict[str, str] = {}

    for key, path in [
      (SyncKey.USER_SETTINGS, user_settings_path),
      (SyncKey.USER_MEMORY, user_memory_path),
    ]:
      content = self._try_read_file(path)
      if content:
        entries[key] = content

    if project_id:
      for key_fn, path in [
        (SyncKey.project_settings, local_settings_path),
        (SyncKey.project_memory, local_memory_path),
      ]:
        content = self._try_read_file(path)
        if content:
          entries[key_fn(project_id)] = content

    self._local_entries = entries
    return entries

  def compute_diff(
    self,
    local: dict[str, str],
    remote: dict[str, str],
  ) -> dict[str, str]:
    """Compute entries that differ between local and remote.

    Args:
        local: Local sync entries.
        remote: Remote sync entries.

    Returns:
        Dict of entries that exist in local but differ from remote.
    """
    return {k: v for k, v in local.items() if remote.get(k) != v}

  def apply_remote_entries(
    self,
    entries: dict[str, str],
    target_paths: dict[str, Path],
  ) -> SyncResult:
    """Apply remote entries to local files.

    Args:
        entries: Remote entries to apply (sync_key → content).
        target_paths: Mapping of sync_key → local file path.

    Returns:
        SyncResult with success status and count.
    """
    applied = 0
    for key, content in entries.items():
      target = target_paths.get(key)
      if not target:
        continue
      if len(content.encode("utf-8")) > MAX_FILE_SIZE_BYTES:
        logger.warning(
          "Skipping oversized entry %s (%d bytes)",
          key,
          len(content.encode("utf-8")),
        )
        continue
      try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        applied += 1
      except OSError as e:
        logger.warning("Failed to write %s: %s", target, e)

    return SyncResult(success=True, entries_synced=applied)

  @staticmethod
  def _try_read_file(path: Path | None) -> str | None:
    """Try to read a file for sync, with size limit and error handling."""
    if not path or not path.exists():
      return None
    try:
      if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        logger.info("File too large for sync: %s", path)
        return None
      content = path.read_text(encoding="utf-8")
      if not content or content.isspace():
        return None
      return content
    except OSError:
      return None
