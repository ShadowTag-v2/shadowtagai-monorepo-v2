# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Collapse read/search — Optimized file read/search tool coalescing.

Ported from src/services/collapseReadSearch.ts (Claude Code v2.1.91).

Modules:
    git_ops:           Git operation detection for read/search caching
    memory_detection:  Memory-aware detection for auto-managed files
    types:             Shared type definitions for collapse operations
"""

from packages.collapse_read_search.git_ops import (
  BranchInfo,
  CommitInfo,
  GitOperationResult,
  PrInfo,
  PushInfo,
  detect_git_operation,
)
from packages.collapse_read_search.memory_detection import (
  is_auto_managed_memory_file,
  is_auto_managed_memory_pattern,
  is_memory_directory,
  is_shell_command_targeting_memory,
)
from packages.collapse_read_search.types import (
  CollapsedReadSearchGroup,
  ContentBlock,
  NormalizedMessage,
  SearchOrReadResult,
  StopHookInfo,
)

__all__ = [
  "BranchInfo",
  "CollapsedReadSearchGroup",
  "CommitInfo",
  "ContentBlock",
  "GitOperationResult",
  "NormalizedMessage",
  "PrInfo",
  "PushInfo",
  "SearchOrReadResult",
  "StopHookInfo",
  "detect_git_operation",
  "is_auto_managed_memory_file",
  "is_auto_managed_memory_pattern",
  "is_memory_directory",
  "is_shell_command_targeting_memory",
]
