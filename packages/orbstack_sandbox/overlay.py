# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Overlay Manager — Copy-on-Write filesystem overlay for sandbox isolation.

Ported from Claude Code speculation.ts: getOverlayPath, copyOverlayToMain,
safeRemoveOverlay.  Python equivalent using host filesystem overlays.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_OVERLAY_ROOT = Path(".beads/sandbox_overlays")
MAX_OVERLAY_BYTES = 256 * 1024 * 1024


@dataclass
class OverlayDiff:
  """Changes made within the overlay."""

  created: list[str] = field(default_factory=list)
  modified: list[str] = field(default_factory=list)
  deleted: list[str] = field(default_factory=list)
  total_bytes: int = 0

  @property
  def has_changes(self) -> bool:
    return bool(self.created or self.modified or self.deleted)

  @property
  def file_count(self) -> int:
    return len(self.created) + len(self.modified) + len(self.deleted)

  def to_dict(self) -> dict[str, Any]:
    return {
      "created": self.created,
      "modified": self.modified,
      "deleted": self.deleted,
      "total_bytes": self.total_bytes,
      "file_count": self.file_count,
    }


def _safe_dirname(session_id: str) -> str:
  h = hashlib.sha256(session_id.encode()).hexdigest()[:8]
  safe = session_id.replace("/", "_").replace("\\", "_")[:32]
  return f"{safe}_{h}"


def _file_hash(path: Path) -> str:
  h = hashlib.sha256()
  try:
    with path.open("rb") as fh:
      for chunk in iter(lambda: fh.read(8192), b""):
        h.update(chunk)
    return h.hexdigest()
  except OSError:
    return ""


class OverlayManager:
  """Copy-on-Write overlay for sandbox execution.

  Host workspace is read-only; writes go to overlay dir.
  After verification, validated changes merge back.
  Mirrors Claude Code speculation overlay pattern.
  """

  def __init__(
    self,
    workspace_root: Path | None = None,
    overlay_root: Path | None = None,
  ) -> None:
    self._workspace = workspace_root or Path.cwd()
    self._overlay_root = overlay_root or (self._workspace / _DEFAULT_OVERLAY_ROOT)
    self._active_overlays: dict[str, Path] = {}

  @property
  def workspace_root(self) -> Path:
    return self._workspace

  def create(self, session_id: str) -> Path:
    if session_id in self._active_overlays:
      raise ValueError(f"Overlay already exists for session {session_id}")
    overlay_dir = self._overlay_root / _safe_dirname(session_id)
    overlay_dir.mkdir(parents=True, exist_ok=True)
    self._active_overlays[session_id] = overlay_dir
    logger.info("[Overlay] Created: %s → %s", session_id, overlay_dir)
    return overlay_dir

  def get_path(self, session_id: str) -> Path | None:
    return self._active_overlays.get(session_id)

  def compute_diff(self, session_id: str) -> OverlayDiff:
    overlay_dir = self._active_overlays.get(session_id)
    if overlay_dir is None or not overlay_dir.exists():
      return OverlayDiff()
    diff = OverlayDiff()
    total_bytes = 0
    for overlay_file in overlay_dir.rglob("*"):
      if overlay_file.is_dir():
        continue
      rel_path = str(overlay_file.relative_to(overlay_dir))
      if overlay_file.name.endswith(".deleted"):
        diff.deleted.append(rel_path.removesuffix(".deleted"))
        continue
      workspace_file = self._workspace / rel_path
      total_bytes += overlay_file.stat().st_size
      if not workspace_file.exists():
        diff.created.append(rel_path)
      elif _file_hash(overlay_file) != _file_hash(workspace_file):
        diff.modified.append(rel_path)
    diff.total_bytes = total_bytes
    return diff

  def merge_to_workspace(
    self,
    session_id: str,
    allowed_paths: list[str] | None = None,
  ) -> int:
    overlay_dir = self._active_overlays.get(session_id)
    if overlay_dir is None or not overlay_dir.exists():
      return 0
    merged = 0
    for overlay_file in overlay_dir.rglob("*"):
      if overlay_file.is_dir() or overlay_file.name.endswith(".deleted"):
        continue
      rel_path = str(overlay_file.relative_to(overlay_dir))
      if allowed_paths is not None and rel_path not in allowed_paths:
        continue
      dest = self._workspace / rel_path
      try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(overlay_file, dest)
        merged += 1
      except OSError as exc:
        logger.warning("[Overlay] Merge failed %s: %s", rel_path, exc)
    logger.info("[Overlay] Merged %d files from %s", merged, session_id)
    return merged

  def destroy(self, session_id: str) -> bool:
    overlay_dir = self._active_overlays.pop(session_id, None)
    if overlay_dir is None:
      return False
    shutil.rmtree(overlay_dir, ignore_errors=True)
    logger.info("[Overlay] Destroyed: %s", session_id)
    return True

  def check_disk_pressure(self, session_id: str) -> bool:
    overlay_dir = self._active_overlays.get(session_id)
    if overlay_dir is None or not overlay_dir.exists():
      return True
    total = sum(f.stat().st_size for f in overlay_dir.rglob("*") if f.is_file())
    return total < MAX_OVERLAY_BYTES

  def list_active(self) -> list[str]:
    return list(self._active_overlays.keys())
