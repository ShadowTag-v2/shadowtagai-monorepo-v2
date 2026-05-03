# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Extract Memories — Durable memory extraction from session transcripts.

Ported from src/services/extractMemories/extractMemories.ts (557 lines).

Core pattern:
  - Extracts durable memories at end of each query loop
  - Cursor-based: only processes messages since last extraction
  - Overlap guard: stashes context for trailing run if called during extraction
  - Tool permissions: restricted to read-only + auto-memory-dir writes
  - Integrates with AutoDream for complementary memory consolidation
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)

# Allowed tool names for memory extraction (mirrors TS createAutoMemCanUseTool)
READ_ONLY_TOOLS = frozenset({"file_read", "grep", "glob"})
WRITE_TOOLS = frozenset({"file_edit", "file_write"})
BASH_TOOL = "bash"

# Type for the system message append callback
AppendSystemMessage = Callable[[dict[str, Any]], None]


@dataclass
class ExtractionResult:
    """Result from a single extraction run."""

    files_written: list[str] = field(default_factory=list)
    memories_saved: int = 0
    skipped: bool = False
    skip_reason: str | None = None
    duration_ms: float = 0.0
    error: str | None = None


def is_model_visible(message: dict[str, Any]) -> bool:
    """True if message is sent in API calls (user or assistant)."""
    return message.get("type") in ("user", "assistant")


def count_model_visible_since(messages: list[dict[str, Any]], since_uuid: str | None) -> int:
    """Count model-visible messages after the cursor UUID."""
    if since_uuid is None:
        return sum(1 for m in messages if is_model_visible(m))

    found = False
    n = 0
    for msg in messages:
        if not found:
            if msg.get("uuid") == since_uuid:
                found = True
            continue
        if is_model_visible(msg):
            n += 1

    # Fallback if cursor was removed (e.g. by context compaction)
    if not found:
        return sum(1 for m in messages if is_model_visible(m))
    return n


def has_memory_writes_since(
    messages: list[dict[str, Any]],
    since_uuid: str | None,
    is_auto_mem_path: Callable[[str], bool],
) -> bool:
    """Check if main agent already wrote to auto-memory paths."""
    found = since_uuid is None
    for msg in messages:
        if not found:
            if msg.get("uuid") == since_uuid:
                found = True
            continue
        if msg.get("type") != "assistant":
            continue
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            fp = _get_written_file_path(block)
            if fp is not None and is_auto_mem_path(fp):
                return True
    return False


def _get_written_file_path(block: dict[str, Any]) -> str | None:
    """Extract file_path from a tool_use block's input."""
    if block.get("type") != "tool_use":
        return None
    name = block.get("name", "")
    if name not in WRITE_TOOLS:
        return None
    inp = block.get("input")
    if isinstance(inp, dict):
        fp = inp.get("file_path")
        if isinstance(fp, str):
            return fp
    return None


def is_tool_allowed_for_extraction(
    tool_name: str,
    tool_input: dict[str, Any],
    memory_dir: str,
) -> bool:
    """Check if a tool call is permitted during extraction.

    Mirrors createAutoMemCanUseTool from the TS source:
    - Read/Grep/Glob: always allowed
    - Bash: only if read-only (no mutation)
    - Edit/Write: only within memory_dir
    """
    if tool_name in READ_ONLY_TOOLS:
        return True

    if tool_name == BASH_TOOL:
        # In the full implementation this would check BashTool.isReadOnly()
        # For the stub, conservatively deny
        return False

    if tool_name in WRITE_TOOLS:
        fp = tool_input.get("file_path", "")
        return isinstance(fp, str) and fp.startswith(memory_dir)

    return False


class MemoryExtractor:
    """Manages durable memory extraction from session transcripts.

    Closure-scoped state is encapsulated in this class (matching the TS
    initExtractMemories() closure pattern).

    Usage:
        extractor = MemoryExtractor(memory_dir=Path("~/.claude/memory"))
        await extractor.run(messages, append_system_message=callback)
        await extractor.drain()  # Wait for in-flight extractions
    """

    def __init__(
        self,
        *,
        memory_dir: Path | None = None,
        is_auto_mem_path: Callable[[str], bool] | None = None,
        min_turns_between: int = 1,
    ) -> None:
        self._memory_dir = memory_dir or Path.home() / ".claude" / "memory"
        self._is_auto_mem_path = is_auto_mem_path or (lambda p: p.startswith(str(self._memory_dir)))
        self._min_turns = min_turns_between

        # Closure-scoped mutable state
        self._last_cursor_uuid: str | None = None
        self._in_progress = False
        self._turns_since_last = 0
        self._pending_context: tuple[list[dict[str, Any]], AppendSystemMessage | None] | None = None
        self._in_flight: set[asyncio.Task[None]] = set()

    @property
    def is_extracting(self) -> bool:
        return self._in_progress

    async def run(
        self,
        messages: list[dict[str, Any]],
        *,
        append_system_message: AppendSystemMessage | None = None,
        is_subagent: bool = False,
    ) -> ExtractionResult:
        """Run memory extraction (fire-and-forget safe).

        Mirrors executeExtractMemoriesImpl from TS:
        - Skips for subagents
        - Checks feature gate (stubbed as enabled)
        - Handles overlap by stashing for trailing run
        """
        if is_subagent:
            return ExtractionResult(skipped=True, skip_reason="subagent")

        if self._in_progress:
            logger.debug("Extraction in progress — stashing for trailing run")
            self._pending_context = (messages, append_system_message)
            return ExtractionResult(skipped=True, skip_reason="coalesced")

        return await self._run_extraction(messages, append_system_message, is_trailing=False)

    async def _run_extraction(
        self,
        messages: list[dict[str, Any]],
        append_system_message: AppendSystemMessage | None,
        *,
        is_trailing: bool,
    ) -> ExtractionResult:
        """Core extraction logic with trailing-run support."""
        import time

        start = time.monotonic()
        new_count = count_model_visible_since(messages, self._last_cursor_uuid)

        # Mutual exclusion: skip if main agent already wrote memories
        if has_memory_writes_since(messages, self._last_cursor_uuid, self._is_auto_mem_path):
            last = messages[-1] if messages else None
            if last and last.get("uuid"):
                self._last_cursor_uuid = last["uuid"]
            return ExtractionResult(skipped=True, skip_reason="direct_write")

        # Turn throttle (skip for trailing runs)
        if not is_trailing:
            self._turns_since_last += 1
            if self._turns_since_last < self._min_turns:
                return ExtractionResult(skipped=True, skip_reason="throttled")
        self._turns_since_last = 0

        self._in_progress = True
        result = ExtractionResult()
        try:
            logger.debug(
                "Starting extraction: %d new messages, dir=%s",
                new_count,
                self._memory_dir,
            )

            # In the full implementation, this would:
            # 1. Scan existing memories (formatMemoryManifest)
            # 2. Build extraction prompt
            # 3. Run forked agent with restricted tool permissions
            # 4. Extract written paths from result
            # For the stub, we just advance the cursor.

            last = messages[-1] if messages else None
            if last and last.get("uuid"):
                self._last_cursor_uuid = last["uuid"]

            elapsed_ms = (time.monotonic() - start) * 1000
            result.duration_ms = elapsed_ms
            logger.debug("Extraction complete: %.0fms", elapsed_ms)

        except Exception as exc:
            result.error = str(exc)
            logger.debug("Extraction error: %s", exc, exc_info=True)
        finally:
            self._in_progress = False

            # Trailing run: process stashed context
            trailing = self._pending_context
            self._pending_context = None
            if trailing:
                logger.debug("Running trailing extraction")
                await self._run_extraction(trailing[0], trailing[1], is_trailing=True)

        return result

    async def drain(self, timeout: float = 60.0) -> None:
        """Wait for all in-flight extractions to complete."""
        if not self._in_flight:
            return
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._in_flight, return_exceptions=True),
                timeout=timeout,
            )
        except TimeoutError:
            logger.debug("Drain timed out after %.0fs", timeout)

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._last_cursor_uuid = None
        self._in_progress = False
        self._turns_since_last = 0
        self._pending_context = None
        self._in_flight.clear()
