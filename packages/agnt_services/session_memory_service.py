# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Memory Service — Background memory extraction from conversations.

Ported from Claude Code v2.1.91 src/services/SessionMemory/:
  - sessionMemory.ts (495L) → Threshold-based extraction scheduling
  - sessionMemoryUtils.ts (207L) → Config, state tracking
  - prompts.ts (324L) → Extraction prompt templates

Key patterns:
  - Forked subagent for memory extraction (shares parent prompt cache)
  - Dual threshold: token count AND tool call count
  - tengu_session_memory feature flag gate
  - tengu_sm_config remote config for thresholds
  - Sequential lock prevents concurrent extractions
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ── Configuration ───────────────────────────────────────────────────


@dataclass
class SessionMemoryConfig:
    """Configuration for session memory extraction thresholds.

    Mirrors CC's SessionMemoryConfig interface from sessionMemoryUtils.ts.
    """

    # Minimum context window tokens before first extraction
    initialization_threshold: int = 10_000
    # Minimum tokens growth between extractions
    minimum_tokens_between_update: int = 5_000
    # Minimum tool calls between extractions
    tool_calls_between_updates: int = 5
    # Maximum token budget for extraction subagent
    max_extraction_tokens: int = 4_096
    # Whether to use the forked agent pattern
    use_forked_agent: bool = True


DEFAULT_CONFIG = SessionMemoryConfig()


# ── State tracking ──────────────────────────────────────────────────


@dataclass
class SessionMemoryState:
    """Mutable state for session memory service.

    Instance-scoped (not module-level) for test isolation.
    """

    initialized: bool = False
    last_extraction_token_count: int = 0
    last_summarized_message_id: str | None = None
    extraction_in_progress: bool = False
    extraction_count: int = 0
    total_extraction_tokens: int = 0
    config: SessionMemoryConfig = field(default_factory=SessionMemoryConfig)


# ── Message types ───────────────────────────────────────────────────


@dataclass
class Message:
    """Simplified message representation for memory extraction."""

    uuid: str
    type: str  # "user" | "assistant" | "system"
    content: Any = None
    tool_calls: list[dict] = field(default_factory=list)


# ── Core logic ──────────────────────────────────────────────────────


def count_tool_calls_since(messages: list[Message], since_uuid: str | None) -> int:
    """Count assistant tool calls since a given message UUID."""
    tool_count = 0
    found_start = since_uuid is None

    for msg in messages:
        if not found_start:
            if msg.uuid == since_uuid:
                found_start = True
            continue
        if msg.type == "assistant":
            tool_count += len(msg.tool_calls)

    return tool_count


def should_extract_memory(
    messages: list[Message],
    current_token_count: int,
    state: SessionMemoryState,
) -> bool:
    """Determine whether to trigger memory extraction.

    Extraction triggers when:
    1. Both thresholds met (tokens AND tool calls), OR
    2. No tool calls in last turn AND token threshold met

    The token threshold is ALWAYS required — prevents excessive extractions
    even when tool call threshold is met.
    """
    config = state.config

    # Check initialization threshold
    if not state.initialized:
        if current_token_count < config.initialization_threshold:
            return False
        state.initialized = True
        state.last_extraction_token_count = current_token_count

    # Token growth threshold
    token_growth = current_token_count - state.last_extraction_token_count
    has_met_token_threshold = token_growth >= config.minimum_tokens_between_update

    # Tool call threshold
    tool_calls_since = count_tool_calls_since(messages, state.last_summarized_message_id)
    has_met_tool_threshold = tool_calls_since >= config.tool_calls_between_updates

    # Check if last assistant turn has no tool calls
    last_has_tools = False
    for msg in reversed(messages):
        if msg.type == "assistant":
            last_has_tools = len(msg.tool_calls) > 0
            break

    should = (has_met_token_threshold and has_met_tool_threshold) or (has_met_token_threshold and not last_has_tools)

    if should and messages:
        last_msg = messages[-1]
        state.last_summarized_message_id = last_msg.uuid
        state.last_extraction_token_count = current_token_count

    return should


# ── Memory file management ──────────────────────────────────────────


def get_session_memory_path(project_dir: str | Path) -> Path:
    """Get the path to the session memory markdown file."""
    return Path(project_dir) / ".claude" / "session_memory.md"


def load_session_memory(path: Path) -> str | None:
    """Load existing session memory content, if any."""
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("Failed to load session memory: %s", e)
    return None


def save_session_memory(path: Path, content: str) -> bool:
    """Save session memory content to disk."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        logger.error("Failed to save session memory: %s", e)
        return False


# ── Extraction prompts ──────────────────────────────────────────────

SESSION_MEMORY_TEMPLATE = """# Session Memory

## Key Decisions
- (extracted from conversation)

## Current State
- (what the user is working on)

## Important Context
- (relevant technical details, preferences, constraints)
"""


def build_session_memory_update_prompt(
    existing_memory: str | None,
    conversation_summary: str,
) -> str:
    """Build the prompt for the extraction subagent."""
    base = existing_memory or SESSION_MEMORY_TEMPLATE
    return (
        f"Update the following session memory based on the recent conversation.\n\n"
        f"## Current Memory\n{base}\n\n"
        f"## Recent Conversation Summary\n{conversation_summary}\n\n"
        f"Write the updated session memory in markdown format. "
        f"Preserve important context, update state, and add new decisions."
    )


# ── Service class ───────────────────────────────────────────────────


class SessionMemoryService:
    """Manages automatic session memory extraction.

    Uses threshold-based triggering and sequential locking
    to prevent concurrent extractions.
    """

    def __init__(
        self,
        project_dir: str | Path,
        config: SessionMemoryConfig | None = None,
    ) -> None:
        self.project_dir = Path(project_dir)
        self.state = SessionMemoryState(config=config or SessionMemoryConfig())
        self._memory_path = get_session_memory_path(self.project_dir)

    def check_and_extract(
        self,
        messages: list[Message],
        current_token_count: int,
    ) -> bool:
        """Check thresholds and trigger extraction if needed.

        Returns True if extraction was triggered.
        """
        if self.state.extraction_in_progress:
            return False

        if not should_extract_memory(messages, current_token_count, self.state):
            return False

        self.state.extraction_in_progress = True
        try:
            load_session_memory(self._memory_path)
            # In production, this would run via a forked subagent.
            # Here we just mark that extraction would occur.
            self.state.extraction_count += 1
            logger.info(
                "Session memory extraction #%d triggered at %d tokens",
                self.state.extraction_count,
                current_token_count,
            )
            return True
        finally:
            self.state.extraction_in_progress = False

    def reset(self) -> None:
        """Reset state for testing."""
        self.state = SessionMemoryState(config=self.state.config)


def health_check() -> bool:
    return True
