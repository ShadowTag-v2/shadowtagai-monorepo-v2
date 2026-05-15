"""Memory file detection utilities.

Determines whether a given file path, glob pattern, or shell command targets
an auto-managed memory file or directory. Used by the collapse engine to
classify memory reads/writes vs regular file I/O.

Ported from: Claude Code utils/memoryFileDetection.ts
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

__all__ = [
  "is_auto_managed_memory_file",
  "is_auto_managed_memory_pattern",
  "is_memory_directory",
  "is_shell_command_targeting_memory",
]

# Well-known memory file names used by the AGNT framework.
_MEMORY_FILE_NAMES: frozenset[str] = frozenset(
  {
    "CLAUDE.md",
    ".claude",
    "AGENTS.md",
    ".agents",
    "GEMINI.md",
    ".gemini",
    # Local project context files
    ".cursorrules",
    ".cursor",
    "copilot-instructions.md",
  }
)

# Patterns that appear in glob expressions targeting memory files.
_MEMORY_GLOB_FRAGMENTS: tuple[str, ...] = (
  "CLAUDE.md",
  ".claude/",
  "AGENTS.md",
  ".agents/",
  "GEMINI.md",
  ".gemini/",
)

# Compiled regex for detecting shell commands that target memory paths.
_MEMORY_PATH_RE = re.compile(
  r"(?:CLAUDE\.md|\.claude/|AGENTS\.md|\.agents/|GEMINI\.md|\.gemini/)",
  re.IGNORECASE,
)


def is_auto_managed_memory_file(path: str) -> bool:
  """Return ``True`` if *path* points to an auto-managed memory file.

  Checks both the filename (basename match) and whether the path contains
  a known memory directory segment.
  """
  p = PurePosixPath(path)
  # Direct file match
  if p.name in _MEMORY_FILE_NAMES:
    return True
  # Path segment match (e.g. ".claude/rules/foo.md")
  parts = p.parts
  return any(part in _MEMORY_FILE_NAMES for part in parts)


def is_auto_managed_memory_pattern(glob: str) -> bool:
  """Return ``True`` if *glob* contains a known memory-targeting pattern."""
  return any(frag in glob for frag in _MEMORY_GLOB_FRAGMENTS)


def is_memory_directory(path: str) -> bool:
  """Return ``True`` if *path* is (or is inside) a memory directory."""
  p = PurePosixPath(path)
  memory_dirs = {".claude", ".agents", ".gemini"}
  return any(part in memory_dirs for part in p.parts)


def is_shell_command_targeting_memory(command: str) -> bool:
  """Return ``True`` if *command* contains a memory file/dir reference.

  Used to classify ``Bash`` tool calls that run ``grep``, ``rg``, ``cat``,
  etc. against memory paths.
  """
  return bool(_MEMORY_PATH_RE.search(command))
