# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Diagnostic tracking service — baseline/diff tracking for IDE diagnostics.

Ported from src/services/diagnosticTracking.ts (Claude Code v2.1.91).

This module tracks diagnostic state (lint errors, type errors, warnings)
across file edits to detect *newly introduced* issues. The core algorithm:

  1. Before editing a file → capture baseline diagnostics
  2. After editing → fetch current diagnostics
  3. Diff against baseline → surface only *new* diagnostics

The IDE/MCP integration is abstracted behind a ``DiagnosticProvider`` protocol,
allowing tests and non-IDE environments to inject their own providers.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

logger = logging.getLogger(__name__)

MAX_DIAGNOSTICS_SUMMARY_CHARS = 4000

# Unicode symbols for severity display
_SEVERITY_SYMBOLS: dict[str, str] = {
  "Error": "✖",
  "Warning": "⚠",
  "Info": "ℹ",
  "Hint": "★",
}
_DEFAULT_SYMBOL = "•"


class DiagnosticSeverity(StrEnum):
  """Diagnostic severity levels matching LSP specification."""

  ERROR = "Error"
  WARNING = "Warning"
  INFO = "Info"
  HINT = "Hint"


@dataclass(frozen=True, slots=True)
class DiagnosticRange:
  """Source location range for a diagnostic."""

  start_line: int
  start_character: int
  end_line: int
  end_character: int


@dataclass(frozen=True, slots=True)
class Diagnostic:
  """A single diagnostic (lint error, type error, warning, etc.)."""

  message: str
  severity: DiagnosticSeverity
  range: DiagnosticRange
  source: str | None = None
  code: str | None = None

  def matches(self, other: Diagnostic) -> bool:
    """Check if two diagnostics are semantically equal."""
    return (
      self.message == other.message
      and self.severity == other.severity
      and self.source == other.source
      and self.code == other.code
      and self.range.start_line == other.range.start_line
      and self.range.start_character == other.range.start_character
      and self.range.end_line == other.range.end_line
      and self.range.end_character == other.range.end_character
    )


@dataclass(frozen=True, slots=True)
class DiagnosticFile:
  """Diagnostics associated with a specific file URI."""

  uri: str
  diagnostics: list[Diagnostic]


class DiagnosticProvider(Protocol):
  """Protocol for fetching diagnostics from an IDE or analysis tool."""

  async def get_diagnostics(self, file_uri: str | None = None) -> list[DiagnosticFile]:
    """Fetch diagnostics.  If ``file_uri`` is provided, scope to that file."""
    ...  # pragma: no cover

  async def open_file(self, file_uri: str) -> None:
    """Ensure a file is open/loaded in the IDE for diagnostics to work."""
    ...  # pragma: no cover


# Normalize file URIs so protocol prefixes and OS path conventions
# don't break baseline lookups.

_PROTOCOL_PREFIXES = frozenset(("file://", "_claude_fs_right:", "_claude_fs_left:"))


def _normalize_uri(uri: str) -> str:
  """Strip known protocol prefixes and normalize for comparison."""
  for prefix in _PROTOCOL_PREFIXES:
    if uri.startswith(prefix):
      uri = uri[len(prefix) :]
      break
  # Case-insensitive on Windows
  if os.name == "nt":
    uri = uri.lower().replace("\\", "/")
  return uri


class DiagnosticTrackingService:
  """Tracks diagnostic baselines across file edits.

  Thread-safe singleton.  Call ``initialize()`` with a provider before use.
  """

  _instance: DiagnosticTrackingService | None = None
  _lock = threading.Lock()

  def __init__(self) -> None:
    self._baseline: dict[str, list[Diagnostic]] = {}
    self._right_file_state: dict[str, list[Diagnostic]] = {}
    self._timestamps: dict[str, float] = {}
    self._provider: DiagnosticProvider | None = None
    self._initialized = False

  @classmethod
  def get_instance(cls) -> DiagnosticTrackingService:
    """Return the module-level singleton (thread-safe)."""
    if cls._instance is None:
      with cls._lock:
        if cls._instance is None:
          cls._instance = cls()
    return cls._instance

  @classmethod
  def reset_instance(cls) -> None:
    """Reset singleton for testing."""
    with cls._lock:
      cls._instance = None

  # -- lifecycle --------------------------------------------------------

  def initialize(self, provider: DiagnosticProvider) -> None:
    """Attach a diagnostic provider.  Idempotent."""
    if self._initialized:
      return
    self._provider = provider
    self._initialized = True

  def shutdown(self) -> None:
    """Release all state."""
    self._initialized = False
    self._baseline.clear()
    self._right_file_state.clear()
    self._timestamps.clear()

  def reset(self) -> None:
    """Clear tracking state while keeping the service initialized."""
    self._baseline.clear()
    self._right_file_state.clear()
    self._timestamps.clear()

  @property
  def is_initialized(self) -> bool:
    return self._initialized

  # -- pre-edit capture -------------------------------------------------

  async def before_file_edited(self, file_path: str) -> None:
    """Capture baseline diagnostics for *file_path* before editing."""
    if not self._initialized or self._provider is None:
      return

    import time

    timestamp = time.time()
    normalized = _normalize_uri(file_path)

    try:
      results = await self._provider.get_diagnostics(f"file://{file_path}")
      if results:
        diag_file = results[0]
        result_norm = _normalize_uri(diag_file.uri)
        if result_norm != normalized:
          logger.warning(
            "Diagnostics path mismatch: expected %s, got %s",
            file_path,
            diag_file.uri,
          )
          return
        self._baseline[normalized] = list(diag_file.diagnostics)
      else:
        self._baseline[normalized] = []
      self._timestamps[normalized] = timestamp
    except Exception:
      logger.debug("Failed to capture baseline diagnostics for %s", file_path)

  # -- post-edit diff ---------------------------------------------------

  async def get_new_diagnostics(self) -> list[DiagnosticFile]:
    """Return diagnostics introduced *after* baselines were captured."""
    if not self._initialized or self._provider is None:
      return []

    try:
      all_files = await self._provider.get_diagnostics()
    except Exception:
      return []

    # Split by protocol
    file_proto = [
      f
      for f in all_files
      if self._baseline.get(_normalize_uri(f.uri)) is not None
      and f.uri.startswith("file://")
    ]
    right_map: dict[str, DiagnosticFile] = {}
    for f in all_files:
      norm = _normalize_uri(f.uri)
      if norm in self._baseline and f.uri.startswith("_claude_fs_right:"):
        right_map[norm] = f

    new_files: list[DiagnosticFile] = []
    for f in file_proto:
      normalized = _normalize_uri(f.uri)
      baseline = self._baseline.get(normalized, [])

      # Prefer right-file diagnostics if changed
      file_to_use = f
      right_file = right_map.get(normalized)
      if right_file is not None:
        prev = self._right_file_state.get(normalized)
        if prev is None or not _arrays_equal(prev, right_file.diagnostics):
          file_to_use = right_file
        self._right_file_state[normalized] = list(right_file.diagnostics)

      # Diff
      new_diags = [
        d for d in file_to_use.diagnostics if not any(d.matches(b) for b in baseline)
      ]
      if new_diags:
        new_files.append(DiagnosticFile(uri=f.uri, diagnostics=new_diags))

      # Roll baseline forward
      self._baseline[normalized] = list(file_to_use.diagnostics)

    return new_files

  # -- formatting -------------------------------------------------------

  @staticmethod
  def format_summary(files: list[DiagnosticFile]) -> str:
    """Human-readable summary of diagnostic files.

    Truncated to ``MAX_DIAGNOSTICS_SUMMARY_CHARS``.
    """
    parts: list[str] = []
    for f in files:
      filename = f.uri.rsplit("/", 1)[-1] or f.uri
      diag_lines = []
      for d in f.diagnostics:
        sym = _SEVERITY_SYMBOLS.get(d.severity.value, _DEFAULT_SYMBOL)
        loc = f"[Line {d.range.start_line + 1}:{d.range.start_character + 1}]"
        code_part = f" [{d.code}]" if d.code else ""
        source_part = f" ({d.source})" if d.source else ""
        diag_lines.append(f"  {sym} {loc} {d.message}{code_part}{source_part}")
      parts.append(f"{filename}:\n" + "\n".join(diag_lines))

    result = "\n\n".join(parts)
    if len(result) > MAX_DIAGNOSTICS_SUMMARY_CHARS:
      trunc = "…[truncated]"
      return result[: MAX_DIAGNOSTICS_SUMMARY_CHARS - len(trunc)] + trunc
    return result

  @staticmethod
  def severity_symbol(severity: DiagnosticSeverity) -> str:
    """Get the display symbol for a severity level."""
    return _SEVERITY_SYMBOLS.get(severity.value, _DEFAULT_SYMBOL)


def _arrays_equal(a: list[Diagnostic], b: list[Diagnostic]) -> bool:
  """Check if two diagnostic lists contain the same diagnostics (set equality)."""
  if len(a) != len(b):
    return False
  return all(any(da.matches(db) for db in b) for da in a) and all(
    any(db.matches(da) for da in a) for db in b
  )


# Module-level convenience
diagnostic_tracker = DiagnosticTrackingService.get_instance()
