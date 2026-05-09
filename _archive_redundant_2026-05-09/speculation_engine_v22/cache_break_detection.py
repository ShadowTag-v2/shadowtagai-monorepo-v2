# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Prompt Cache Break Detection — Two-phase cache invalidation monitor.

Ported from Claude Code v2.1.91 promptCacheBreakDetection.ts.

Architecture:
  Phase 1 (pre-call): Snapshot prompt/tool state, detect what changed.
  Phase 2 (post-call): Compare cache tokens to detect actual breaks,
  correlate with pending changes to explain causality.

  TTL-aware: Distinguishes genuine cache invalidations from expected
  5-min and 1-hour server-side TTL expirations. Tracks cache_control
  scope/TTL flips independently of content hashes.

  Per-tool schema hashing: When aggregate tool hash changes but tool
  count is stable, identifies exactly which tool's description mutated
  (common with dynamic MCP/Agent tools — 77% of tool breaks per BQ).
"""

from __future__ import annotations

import difflib
import json
import logging
import random
import string
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from speculation_engine.telemetry import _write_event

logger = logging.getLogger(__name__)

# --- Constants ---

CACHE_TTL_5MIN_S = 5 * 60
CACHE_TTL_1HOUR_S = 60 * 60
MIN_CACHE_MISS_TOKENS = 2_000
MAX_TRACKED_SOURCES = 10

TRACKED_SOURCE_PREFIXES = (
    "repl_main_thread",
    "sdk",
    "agent:custom",
    "agent:default",
    "agent:builtin",
)

EXCLUDED_MODEL_FRAGMENTS = ("haiku",)


# --- Hashing ---


def _djb2_hash(data: str) -> int:
    """DJB2 string hash (matches Claude Code's djb2Hash fallback)."""
    h = 5381
    for ch in data:
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    return h


def _compute_hash(data: Any) -> int:
    """Hash arbitrary JSON-serializable data via DJB2."""
    return _djb2_hash(json.dumps(data, sort_keys=True, default=str))


# --- Utility functions ---


def _is_excluded_model(model: str) -> bool:
    return any(frag in model for frag in EXCLUDED_MODEL_FRAGMENTS)


def _get_tracking_key(
    query_source: str,
    agent_id: str | None = None,
) -> str | None:
    """Return tracking key for a query source, or None if untracked."""
    if query_source == "compact":
        return "repl_main_thread"
    for prefix in TRACKED_SOURCE_PREFIXES:
        if query_source.startswith(prefix):
            return agent_id or query_source
    return None


def _strip_cache_control(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip cache_control from items for content-only hashing."""
    result = []
    for item in items:
        if "cache_control" not in item:
            result.append(item)
        else:
            copy = {k: v for k, v in item.items() if k != "cache_control"}
            result.append(copy)
    return result


def _sanitize_tool_name(name: str) -> str:
    """Collapse MCP tool names to 'mcp'; built-in names pass through."""
    return "mcp" if name.startswith("mcp__") else name


def _get_system_char_count(system: list[dict[str, Any]]) -> int:
    return sum(len(block.get("text", "")) for block in system)


def _compute_per_tool_hashes(
    stripped_tools: list[dict[str, Any]],
    names: list[str],
) -> dict[str, int]:
    hashes: dict[str, int] = {}
    for i, tool in enumerate(stripped_tools):
        key = names[i] if i < len(names) else f"__idx_{i}"
        hashes[key] = _compute_hash(tool)
    return hashes


def _build_diffable_content(
    system: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    model: str,
) -> str:
    system_text = "\n\n".join(block.get("text", "") for block in system)
    tool_details = sorted(
        f"{t.get('name', 'unknown')}\n"
        f"  description: {t.get('description', '')}\n"
        f"  input_schema: {json.dumps(t.get('input_schema', {}), sort_keys=True)}"
        for t in tools
    )
    return f"Model: {model}\n\n=== System Prompt ===\n\n{system_text}\n\n=== Tools ({len(tools)}) ===\n\n" + "\n\n".join(tool_details) + "\n"


# --- Data structures ---


@dataclass
class PendingChanges:
    """Detected changes between consecutive prompt states."""

    system_prompt_changed: bool = False
    tool_schemas_changed: bool = False
    model_changed: bool = False
    fast_mode_changed: bool = False
    cache_control_changed: bool = False
    global_cache_strategy_changed: bool = False
    betas_changed: bool = False
    auto_mode_changed: bool = False
    overage_changed: bool = False
    cached_mc_changed: bool = False
    effort_changed: bool = False
    extra_body_changed: bool = False
    added_tool_count: int = 0
    removed_tool_count: int = 0
    system_char_delta: int = 0
    added_tools: list[str] = field(default_factory=list)
    removed_tools: list[str] = field(default_factory=list)
    changed_tool_schemas: list[str] = field(default_factory=list)
    previous_model: str = ""
    new_model: str = ""
    prev_global_cache_strategy: str = ""
    new_global_cache_strategy: str = ""
    added_betas: list[str] = field(default_factory=list)
    removed_betas: list[str] = field(default_factory=list)
    prev_effort_value: str = ""
    new_effort_value: str = ""
    _build_prev_diffable: Any = None  # Callable[[], str] | None


@dataclass
class TrackedState:
    """Snapshot of prompt/tool state for change detection."""

    system_hash: int = 0
    tools_hash: int = 0
    cache_control_hash: int = 0
    tool_names: list[str] = field(default_factory=list)
    per_tool_hashes: dict[str, int] = field(default_factory=dict)
    system_char_count: int = 0
    model: str = ""
    fast_mode: bool = False
    global_cache_strategy: str = ""
    betas: list[str] = field(default_factory=list)
    auto_mode_active: bool = False
    is_using_overage: bool = False
    cached_mc_enabled: bool = False
    effort_value: str = ""
    extra_body_hash: int = 0
    call_count: int = 0
    pending_changes: PendingChanges | None = None
    prev_cache_read_tokens: int | None = None
    cache_deletions_pending: bool = False
    _build_diffable: Any = None  # Callable[[], str] | None


@dataclass
class PromptStateSnapshot:
    """Input snapshot for phase 1 recording."""

    system: list[dict[str, Any]]
    tool_schemas: list[dict[str, Any]]
    query_source: str
    model: str
    agent_id: str | None = None
    fast_mode: bool = False
    global_cache_strategy: str = ""
    betas: list[str] = field(default_factory=list)
    auto_mode_active: bool = False
    is_using_overage: bool = False
    cached_mc_enabled: bool = False
    effort_value: str = ""
    extra_body_params: Any = None


# --- Core detector ---


class CacheBreakDetector:
    """Two-phase prompt cache break detector.

    Usage:
        detector = CacheBreakDetector()

        # Phase 1: Before API call
        detector.record_prompt_state(snapshot)

        # Phase 2: After API call
        await detector.check_response_for_cache_break(
            query_source, cache_read_tokens, cache_creation_tokens, messages
        )
    """

    def __init__(self, *, diff_dir: str | None = None) -> None:
        self._state_by_source: dict[str, TrackedState] = {}
        self._diff_dir = diff_dir or tempfile.gettempdir()

    def record_prompt_state(self, snapshot: PromptStateSnapshot) -> None:
        """Phase 1: Record current state, detect changes from previous."""
        try:
            self._record_prompt_state_inner(snapshot)
        except Exception as exc:
            logger.warning("Cache break detection record failed: %s", exc)

    def _record_prompt_state_inner(self, snapshot: PromptStateSnapshot) -> None:
        key = _get_tracking_key(snapshot.query_source, snapshot.agent_id)
        if key is None:
            return

        stripped_system = _strip_cache_control(snapshot.system)
        stripped_tools = _strip_cache_control(snapshot.tool_schemas)

        system_hash = _compute_hash(stripped_system)
        tools_hash = _compute_hash(stripped_tools)
        cache_control_hash = _compute_hash([block.get("cache_control") for block in snapshot.system])
        tool_names = [t.get("name", "unknown") for t in snapshot.tool_schemas]
        system_char_count = _get_system_char_count(snapshot.system)
        sorted_betas = sorted(snapshot.betas)
        effort_str = str(snapshot.effort_value) if snapshot.effort_value else ""
        extra_body_hash = _compute_hash(snapshot.extra_body_params) if snapshot.extra_body_params is not None else 0

        def lazy_diffable() -> str:
            return _build_diffable_content(snapshot.system, snapshot.tool_schemas, snapshot.model)

        prev = self._state_by_source.get(key)

        if prev is None:
            # Evict oldest if at capacity
            while len(self._state_by_source) >= MAX_TRACKED_SOURCES:
                oldest_key = next(iter(self._state_by_source))
                del self._state_by_source[oldest_key]

            self._state_by_source[key] = TrackedState(
                system_hash=system_hash,
                tools_hash=tools_hash,
                cache_control_hash=cache_control_hash,
                tool_names=tool_names,
                per_tool_hashes=_compute_per_tool_hashes(stripped_tools, tool_names),
                system_char_count=system_char_count,
                model=snapshot.model,
                fast_mode=snapshot.fast_mode,
                global_cache_strategy=snapshot.global_cache_strategy,
                betas=sorted_betas,
                auto_mode_active=snapshot.auto_mode_active,
                is_using_overage=snapshot.is_using_overage,
                cached_mc_enabled=snapshot.cached_mc_enabled,
                effort_value=effort_str,
                extra_body_hash=extra_body_hash,
                call_count=1,
                _build_diffable=lazy_diffable,
            )
            return

        prev.call_count += 1

        # Detect per-field changes
        sp_changed = system_hash != prev.system_hash
        ts_changed = tools_hash != prev.tools_hash
        model_changed = snapshot.model != prev.model
        fm_changed = snapshot.fast_mode != prev.fast_mode
        cc_changed = cache_control_hash != prev.cache_control_hash
        gcs_changed = snapshot.global_cache_strategy != prev.global_cache_strategy
        betas_changed = sorted_betas != prev.betas
        auto_changed = snapshot.auto_mode_active != prev.auto_mode_active
        overage_changed = snapshot.is_using_overage != prev.is_using_overage
        cmc_changed = snapshot.cached_mc_enabled != prev.cached_mc_enabled
        effort_changed = effort_str != prev.effort_value
        eb_changed = extra_body_hash != prev.extra_body_hash

        any_change = (
            sp_changed
            or ts_changed
            or model_changed
            or fm_changed
            or cc_changed
            or gcs_changed
            or betas_changed
            or auto_changed
            or overage_changed
            or cmc_changed
            or effort_changed
            or eb_changed
        )

        if any_change:
            prev_tool_set = set(prev.tool_names)
            new_tool_set = set(tool_names)
            prev_beta_set = set(prev.betas)
            new_beta_set = set(sorted_betas)

            added_tools = [n for n in tool_names if n not in prev_tool_set]
            removed_tools = [n for n in prev.tool_names if n not in new_tool_set]
            changed_schemas: list[str] = []

            if ts_changed:
                new_hashes = _compute_per_tool_hashes(stripped_tools, tool_names)
                for name in tool_names:
                    if name in prev_tool_set and new_hashes.get(name) != prev.per_tool_hashes.get(name):
                        changed_schemas.append(name)
                prev.per_tool_hashes = new_hashes

            prev.pending_changes = PendingChanges(
                system_prompt_changed=sp_changed,
                tool_schemas_changed=ts_changed,
                model_changed=model_changed,
                fast_mode_changed=fm_changed,
                cache_control_changed=cc_changed,
                global_cache_strategy_changed=gcs_changed,
                betas_changed=betas_changed,
                auto_mode_changed=auto_changed,
                overage_changed=overage_changed,
                cached_mc_changed=cmc_changed,
                effort_changed=effort_changed,
                extra_body_changed=eb_changed,
                added_tool_count=len(added_tools),
                removed_tool_count=len(removed_tools),
                added_tools=added_tools,
                removed_tools=removed_tools,
                changed_tool_schemas=changed_schemas,
                system_char_delta=system_char_count - prev.system_char_count,
                previous_model=prev.model,
                new_model=snapshot.model,
                prev_global_cache_strategy=prev.global_cache_strategy,
                new_global_cache_strategy=snapshot.global_cache_strategy,
                added_betas=[b for b in sorted_betas if b not in prev_beta_set],
                removed_betas=[b for b in prev.betas if b not in new_beta_set],
                prev_effort_value=prev.effort_value,
                new_effort_value=effort_str,
                _build_prev_diffable=prev._build_diffable,
            )
        else:
            prev.pending_changes = None

        # Update state
        prev.system_hash = system_hash
        prev.tools_hash = tools_hash
        prev.cache_control_hash = cache_control_hash
        prev.tool_names = tool_names
        prev.system_char_count = system_char_count
        prev.model = snapshot.model
        prev.fast_mode = snapshot.fast_mode
        prev.global_cache_strategy = snapshot.global_cache_strategy
        prev.betas = sorted_betas
        prev.auto_mode_active = snapshot.auto_mode_active
        prev.is_using_overage = snapshot.is_using_overage
        prev.cached_mc_enabled = snapshot.cached_mc_enabled
        prev.effort_value = effort_str
        prev.extra_body_hash = extra_body_hash
        prev._build_diffable = lazy_diffable

    async def check_response_for_cache_break(
        self,
        query_source: str,
        cache_read_tokens: int,
        cache_creation_tokens: int,
        messages: list[dict[str, Any]],
        agent_id: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Phase 2: Check if a cache break occurred and explain why.

        Returns a diagnostic dict if a break was detected, None otherwise.
        """
        try:
            return await self._check_inner(
                query_source,
                cache_read_tokens,
                cache_creation_tokens,
                messages,
                agent_id,
                request_id,
            )
        except Exception as exc:
            logger.warning("Cache break detection check failed: %s", exc)
            return None

    async def _check_inner(
        self,
        query_source: str,
        cache_read_tokens: int,
        cache_creation_tokens: int,
        messages: list[dict[str, Any]],
        agent_id: str | None,
        request_id: str | None,
    ) -> dict[str, Any] | None:
        key = _get_tracking_key(query_source, agent_id)
        if key is None:
            return None

        state = self._state_by_source.get(key)
        if state is None:
            return None

        if _is_excluded_model(state.model):
            return None

        prev_cache_read = state.prev_cache_read_tokens
        state.prev_cache_read_tokens = cache_read_tokens

        # Calculate time since last assistant message for TTL detection
        last_assistant_ts = None
        for msg in reversed(messages):
            if msg.get("type") == "assistant" or msg.get("role") == "assistant":
                ts = msg.get("timestamp")
                if ts:
                    try:
                        import datetime

                        if isinstance(ts, str):
                            dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            last_assistant_ts = dt.timestamp()
                        elif isinstance(ts, (int, float)):
                            last_assistant_ts = float(ts)
                    except (ValueError, TypeError):
                        pass
                break

        time_since_last = time.time() - last_assistant_ts if last_assistant_ts else None

        # Skip first call — no baseline
        if prev_cache_read is None:
            return None

        changes = state.pending_changes

        # Cache deletions via microcompact — expected drop
        if state.cache_deletions_pending:
            state.cache_deletions_pending = False
            logger.debug(
                "[PROMPT CACHE] deletion applied, read: %d → %d (expected)",
                prev_cache_read,
                cache_read_tokens,
            )
            state.pending_changes = None
            return None

        # Detect break: >5% drop AND exceeds minimum threshold
        token_drop = prev_cache_read - cache_read_tokens
        if cache_read_tokens >= prev_cache_read * 0.95 or token_drop < MIN_CACHE_MISS_TOKENS:
            state.pending_changes = None
            return None

        # Build explanation
        parts: list[str] = []
        if changes:
            if changes.model_changed:
                parts.append(f"model changed ({changes.previous_model} → {changes.new_model})")
            if changes.system_prompt_changed:
                delta = changes.system_char_delta
                char_info = f" ({delta:+d} chars)" if delta != 0 else ""
                parts.append(f"system prompt changed{char_info}")
            if changes.tool_schemas_changed:
                if changes.added_tool_count > 0 or changes.removed_tool_count > 0:
                    tool_diff = f" (+{changes.added_tool_count}/-{changes.removed_tool_count} tools)"
                else:
                    tool_diff = " (tool prompt/schema changed, same tool set)"
                parts.append(f"tools changed{tool_diff}")
            if changes.fast_mode_changed:
                parts.append("fast mode toggled")
            if changes.global_cache_strategy_changed:
                prev_s = changes.prev_global_cache_strategy or "none"
                new_s = changes.new_global_cache_strategy or "none"
                parts.append(f"global cache strategy changed ({prev_s} → {new_s})")
            if changes.cache_control_changed and not changes.global_cache_strategy_changed and not changes.system_prompt_changed:
                parts.append("cache_control changed (scope or TTL)")
            if changes.betas_changed:
                added = f"+{','.join(changes.added_betas)}" if changes.added_betas else ""
                removed = f"-{','.join(changes.removed_betas)}" if changes.removed_betas else ""
                diff_str = " ".join(filter(None, [added, removed]))
                parts.append(f"betas changed ({diff_str})" if diff_str else "betas changed")
            if changes.auto_mode_changed:
                parts.append("auto mode toggled")
            if changes.overage_changed:
                parts.append("overage state changed (TTL latched, no flip)")
            if changes.cached_mc_changed:
                parts.append("cached microcompact toggled")
            if changes.effort_changed:
                prev_e = changes.prev_effort_value or "default"
                new_e = changes.new_effort_value or "default"
                parts.append(f"effort changed ({prev_e} → {new_e})")
            if changes.extra_body_changed:
                parts.append("extra body params changed")

        # TTL expiration detection
        over_5min = time_since_last is not None and time_since_last > CACHE_TTL_5MIN_S
        over_1hr = time_since_last is not None and time_since_last > CACHE_TTL_1HOUR_S

        if parts:
            reason = ", ".join(parts)
        elif over_1hr:
            reason = "possible 1h TTL expiry (prompt unchanged)"
        elif over_5min:
            reason = "possible 5min TTL expiry (prompt unchanged)"
        elif time_since_last is not None:
            reason = "likely server-side (prompt unchanged, <5min gap)"
        else:
            reason = "unknown cause"

        # Build telemetry event
        event_data: dict[str, Any] = {
            "system_prompt_changed": changes.system_prompt_changed if changes else False,
            "tool_schemas_changed": changes.tool_schemas_changed if changes else False,
            "model_changed": changes.model_changed if changes else False,
            "fast_mode_changed": changes.fast_mode_changed if changes else False,
            "cache_control_changed": changes.cache_control_changed if changes else False,
            "global_cache_strategy_changed": changes.global_cache_strategy_changed if changes else False,
            "betas_changed": changes.betas_changed if changes else False,
            "auto_mode_changed": changes.auto_mode_changed if changes else False,
            "overage_changed": changes.overage_changed if changes else False,
            "cached_mc_changed": changes.cached_mc_changed if changes else False,
            "effort_changed": changes.effort_changed if changes else False,
            "extra_body_changed": changes.extra_body_changed if changes else False,
            "added_tool_count": changes.added_tool_count if changes else 0,
            "removed_tool_count": changes.removed_tool_count if changes else 0,
            "system_char_delta": changes.system_char_delta if changes else 0,
            "added_tools": ",".join(_sanitize_tool_name(t) for t in (changes.added_tools if changes else [])),
            "removed_tools": ",".join(_sanitize_tool_name(t) for t in (changes.removed_tools if changes else [])),
            "changed_tool_schemas": ",".join(_sanitize_tool_name(t) for t in (changes.changed_tool_schemas if changes else [])),
            "call_number": state.call_count,
            "prev_cache_read_tokens": prev_cache_read,
            "cache_read_tokens": cache_read_tokens,
            "cache_creation_tokens": cache_creation_tokens,
            "time_since_last_assistant_msg": time_since_last if time_since_last is not None else -1,
            "last_assistant_msg_over_5min_ago": over_5min,
            "last_assistant_msg_over_1hr_ago": over_1hr,
            "request_id": request_id or "",
            "reason": reason,
            "query_source": query_source,
        }

        _write_event("prompt_cache_break", event_data)

        # Write diff for debugging
        diff_path: str | None = None
        if changes and changes._build_prev_diffable and state._build_diffable:
            diff_path = self._write_diff(changes._build_prev_diffable(), state._build_diffable())

        summary = (
            f"[PROMPT CACHE BREAK] {reason} "
            f"[source={query_source}, call #{state.call_count}, "
            f"cache read: {prev_cache_read} → {cache_read_tokens}, "
            f"creation: {cache_creation_tokens}" + (f", diff: {diff_path}" if diff_path else "") + "]"
        )
        logger.warning(summary)

        state.pending_changes = None
        return event_data

    def _write_diff(self, prev_content: str, new_content: str) -> str | None:
        """Write a unified diff to disk for debugging."""
        try:
            suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            diff_path = Path(self._diff_dir) / f"cache-break-{suffix}.diff"
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_lines = difflib.unified_diff(
                prev_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
            )
            diff_path.write_text("".join(diff_lines))
            return str(diff_path)
        except Exception:
            return None

    def notify_cache_deletion(
        self,
        query_source: str,
        agent_id: str | None = None,
    ) -> None:
        """Mark that cache_edits deletions were sent — next drop is expected."""
        key = _get_tracking_key(query_source, agent_id)
        state = self._state_by_source.get(key) if key else None
        if state:
            state.cache_deletions_pending = True

    def notify_compaction(
        self,
        query_source: str,
        agent_id: str | None = None,
    ) -> None:
        """Reset baseline after compaction — drop is expected."""
        key = _get_tracking_key(query_source, agent_id)
        state = self._state_by_source.get(key) if key else None
        if state:
            state.prev_cache_read_tokens = None

    def cleanup_agent_tracking(self, agent_id: str) -> None:
        """Remove tracking state for a terminated agent."""
        self._state_by_source.pop(agent_id, None)

    def reset(self) -> None:
        """Clear all tracking state."""
        self._state_by_source.clear()

    @property
    def tracked_source_count(self) -> int:
        return len(self._state_by_source)
