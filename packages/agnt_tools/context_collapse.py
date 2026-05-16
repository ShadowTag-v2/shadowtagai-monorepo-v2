# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context Collapse — P0 #5 from Kairos Ultraplan.

Ported from: Claude Code src/services/contextCollapse.ts (inferred)
Reference: Kairos Ultraplan lines 1441-1443

Collapses consecutive read/search tool results into synthesized summaries
to prevent context window bloat from back-to-back grep_search, view_file,
or read_url_content calls.

Pattern:
  1. Detect consecutive tool results of the same type (grep, read, search)
  2. Extract key findings from each result
  3. Synthesize into a compact summary
  4. Replace the N individual results with a single collapsed block

This is Layer 0 of the 4-layer microcompact pipeline.

Usage:
    from packages.agnt_tools.context_collapse import ContextCollapser
    collapser = ContextCollapser()
    collapsed = collapser.collapse(tool_results)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("agnt.context_collapse")

# --- Constants ---------------------------------------------------------------

# Tool types that are candidates for collapse
COLLAPSIBLE_TOOLS = frozenset(
  {
    "grep_search",
    "view_file",
    "read_url_content",
    "list_dir",
    "semantic_search",
  }
)

# Minimum consecutive same-type calls before collapsing
MIN_CONSECUTIVE_FOR_COLLAPSE = 3

# Maximum lines to keep per collapsed result
MAX_LINES_PER_RESULT = 10

# Maximum total lines in collapsed output
MAX_COLLAPSED_LINES = 50


# --- Data Models -------------------------------------------------------------


@dataclass
class ToolResult:
  """Represents a single tool call result."""

  tool_name: str
  arguments: dict = field(default_factory=dict)
  output: str = ""
  chars: int = 0


@dataclass
class CollapseResult:
  """Result of the context collapse operation."""

  original_count: int
  collapsed_count: int
  original_chars: int
  collapsed_chars: int
  savings_pct: float
  output: str


# --- Core Implementation ----------------------------------------------------


class ContextCollapser:
  """Collapse consecutive read/search tool results into summaries.

  This is the Layer 0 filter in the 4-layer microcompact pipeline.
  It runs before the model sees the tool results, reducing context
  window consumption from back-to-back exploratory tool calls.

  Collapse strategy:
    - grep_search: Merge file lists, deduplicate, show top N matches
    - view_file: Summarize viewed ranges, extract key identifiers
    - read_url_content: Extract titles and key sections
    - list_dir: Merge directory listings
  """

  def __init__(
    self,
    min_consecutive: int = MIN_CONSECUTIVE_FOR_COLLAPSE,
    max_lines_per: int = MAX_LINES_PER_RESULT,
    max_total_lines: int = MAX_COLLAPSED_LINES,
  ) -> None:
    self.min_consecutive = min_consecutive
    self.max_lines_per = max_lines_per
    self.max_total_lines = max_total_lines

  def collapse(self, results: list[ToolResult]) -> CollapseResult:
    """Collapse consecutive same-type tool results.

    Args:
        results: Ordered list of tool results from a turn.

    Returns:
        CollapseResult with the synthesized output.
    """
    if not results:
      return CollapseResult(
        original_count=0,
        collapsed_count=0,
        original_chars=0,
        collapsed_chars=0,
        savings_pct=0,
        output="",
      )

    original_chars = sum(r.chars or len(r.output) for r in results)

    # Find runs of consecutive same-type collapsible tools
    runs = self._find_collapsible_runs(results)

    if not runs:
      # Nothing to collapse
      combined = "\n".join(r.output for r in results)
      return CollapseResult(
        original_count=len(results),
        collapsed_count=len(results),
        original_chars=original_chars,
        collapsed_chars=len(combined),
        savings_pct=0,
        output=combined,
      )

    # Build collapsed output
    output_parts: list[str] = []
    collapsed_count = 0
    processed_indices: set[int] = set()

    for start, end, tool_name in runs:
      run_results = results[start:end]
      collapsed_text = self._collapse_run(tool_name, run_results)
      output_parts.append(collapsed_text)
      collapsed_count += 1
      processed_indices.update(range(start, end))

    # Include non-collapsed results as-is
    for i, result in enumerate(results):
      if i not in processed_indices:
        output_parts.append(result.output)
        collapsed_count += 1

    combined = "\n\n".join(output_parts)
    collapsed_chars = len(combined)

    savings = (1 - collapsed_chars / original_chars) * 100 if original_chars > 0 else 0

    if savings > 5:
      logger.info(
        "ContextCollapse: %d results → %d blocks (%.0f%% savings, %d → %d chars)",
        len(results),
        collapsed_count,
        savings,
        original_chars,
        collapsed_chars,
      )

    return CollapseResult(
      original_count=len(results),
      collapsed_count=collapsed_count,
      original_chars=original_chars,
      collapsed_chars=collapsed_chars,
      savings_pct=round(savings, 1),
      output=combined,
    )

  def _find_collapsible_runs(
    self, results: list[ToolResult]
  ) -> list[tuple[int, int, str]]:
    """Find runs of consecutive same-type collapsible tools.

    Returns list of (start_index, end_index, tool_name) tuples.
    """
    runs: list[tuple[int, int, str]] = []
    i = 0
    while i < len(results):
      tool = results[i].tool_name
      if tool not in COLLAPSIBLE_TOOLS:
        i += 1
        continue

      # Find end of run
      j = i + 1
      while j < len(results) and results[j].tool_name == tool:
        j += 1

      run_length = j - i
      if run_length >= self.min_consecutive:
        runs.append((i, j, tool))

      i = j

    return runs

  def _collapse_run(self, tool_name: str, results: list[ToolResult]) -> str:
    """Collapse a run of same-type tool results into a summary."""
    if tool_name == "grep_search":
      return self._collapse_grep(results)
    elif tool_name == "view_file":
      return self._collapse_view_file(results)
    elif tool_name == "read_url_content":
      return self._collapse_urls(results)
    elif tool_name == "list_dir":
      return self._collapse_list_dir(results)
    else:
      return self._collapse_generic(results)

  def _collapse_grep(self, results: list[ToolResult]) -> str:
    """Collapse consecutive grep_search results."""
    queries = []
    all_files: set[str] = set()
    match_lines: list[str] = []

    for r in results:
      query = r.arguments.get("Query", "?")
      queries.append(query)

      # Extract file paths from output
      for line in r.output.splitlines():
        line = line.strip()
        if line and not line.startswith("(") and ":" in line:
          file_part = line.split(":")[0]
          all_files.add(file_part)
          if len(match_lines) < self.max_total_lines:
            match_lines.append(line)

    header = f"[COLLAPSED: {len(results)} grep_search calls]\nQueries: {', '.join(repr(q) for q in queries)}\nFiles matched: {len(all_files)}\n"

    if all_files:
      file_list = "\n".join(f"  - {f}" for f in sorted(all_files)[:20])
      header += f"Matched files:\n{file_list}\n"

    if match_lines:
      sample = "\n".join(match_lines[: self.max_lines_per])
      header += f"\nTop matches:\n{sample}"

    return header

  def _collapse_view_file(self, results: list[ToolResult]) -> str:
    """Collapse consecutive view_file results."""
    files_viewed: list[str] = []
    key_identifiers: list[str] = []

    for r in results:
      path = r.arguments.get("AbsolutePath", "?")
      start = r.arguments.get("StartLine", "")
      end = r.arguments.get("EndLine", "")
      range_str = f" L{start}-{end}" if start else ""
      files_viewed.append(f"{path}{range_str}")

      # Extract function/class definitions from output
      for line in r.output.splitlines():
        stripped = line.strip()
        if re.match(r"^(def |class |function |export |const |interface )", stripped):
          key_identifiers.append(stripped[:100])

    header = f"[COLLAPSED: {len(results)} view_file calls]\nFiles viewed:\n"
    for f in files_viewed:
      header += f"  - {f}\n"

    if key_identifiers:
      header += "\nKey identifiers found:\n"
      for ident in key_identifiers[: self.max_lines_per]:
        header += f"  - {ident}\n"

    return header

  def _collapse_urls(self, results: list[ToolResult]) -> str:
    """Collapse consecutive read_url_content results."""
    urls: list[str] = []
    titles: list[str] = []

    for r in results:
      url = r.arguments.get("Url", "?")
      urls.append(url)

      # Extract title (first heading or first non-empty line)
      for line in r.output.splitlines()[:10]:
        stripped = line.strip()
        if stripped.startswith("#"):
          titles.append(stripped.lstrip("# "))
          break

    header = f"[COLLAPSED: {len(results)} read_url_content calls]\nURLs fetched:\n"
    for i, url in enumerate(urls):
      title = titles[i] if i < len(titles) else ""
      header += f"  - {url}"
      if title:
        header += f" → {title}"
      header += "\n"

    return header

  def _collapse_list_dir(self, results: list[ToolResult]) -> str:
    """Collapse consecutive list_dir results."""
    dirs: list[str] = []
    total_entries = 0

    for r in results:
      path = r.arguments.get("DirectoryPath", "?")
      dirs.append(path)
      total_entries += len(r.output.splitlines())

    header = f"[COLLAPSED: {len(results)} list_dir calls]\nDirectories listed: {len(dirs)}\nTotal entries: {total_entries}\nPaths:\n"
    for d in dirs:
      header += f"  - {d}\n"

    return header

  def _collapse_generic(self, results: list[ToolResult]) -> str:
    """Generic collapse for unknown tool types."""
    tool_name = results[0].tool_name if results else "unknown"
    total_chars = sum(len(r.output) for r in results)
    header = (
      f"[COLLAPSED: {len(results)} {tool_name} calls, {total_chars:,} chars total]\n"
    )
    # Include first few lines of each
    for i, r in enumerate(results[:5]):
      first_lines = "\n".join(r.output.splitlines()[:3])
      header += f"\n--- Result {i + 1} ---\n{first_lines}\n"

    if len(results) > 5:
      header += f"\n... and {len(results) - 5} more results\n"

    return header
