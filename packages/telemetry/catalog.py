# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Telemetry Event Catalog.

Maps all 34+ Claude Code tengu_* Datadog events to AGNT equivalents.
Each event is a typed dataclass for structured emission.

Categories:
    - API: Request/response lifecycle events
    - Compaction: Context compaction pipeline events
    - Tool: Tool execution lifecycle events
    - Classifier: Permission decision events
    - Shell: Bash security events
    - Memory: Session memory events
    - VCR: Record/replay events
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventCategory(StrEnum):
    """Event category for filtering and dashboarding."""

    API = "api"
    COMPACTION = "compaction"
    TOOL = "tool"
    CLASSIFIER = "classifier"
    SHELL = "shell"
    MEMORY = "memory"
    VCR = "vcr"
    SESSION = "session"
    ERROR = "error"
    GEMINI = "gemini"
    RESEARCH = "research"


@dataclass
class TelemetryEvent:
    """A single telemetry event.

    Attributes:
        event: Event name (e.g., "agnt_api_success").
        category: Event category for grouping.
        timestamp: Unix epoch when event occurred.
        properties: Arbitrary key-value properties.
        duration_ms: Duration for timed events.
        success: Whether the operation succeeded.
        error_message: Error details if success=False.
    """

    event: str
    category: EventCategory
    timestamp: float = 0.0
    properties: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    success: bool = True
    error_message: str = ""

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL output."""
        d: dict[str, Any] = {
            "event": self.event,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "success": self.success,
        }
        if self.properties:
            d["properties"] = self.properties
        if self.duration_ms > 0:
            d["duration_ms"] = self.duration_ms
        if self.error_message:
            d["error_message"] = self.error_message
        return d


class EventCatalog:
    """Factory for creating typed telemetry events.

    Maps Claude Code tengu_* events to AGNT equivalents.

    Usage:
        catalog = EventCatalog()
        event = catalog.api_success(model="gemini-3.1-flash", tokens=1500)
        sink.emit(event)
    """

    # --- API Events ---

    @staticmethod
    def api_success(
        model: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_api_success — Successful Gemini API call.

        CC equivalent: tengu_api_success
        """
        return TelemetryEvent(
            event="agnt_api_success",
            category=EventCategory.API,
            duration_ms=latency_ms,
            properties={
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )

    @staticmethod
    def api_error(
        model: str = "",
        error_type: str = "",
        error_message: str = "",
        latency_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_api_error — Failed Gemini API call.

        CC equivalent: tengu_api_error
        """
        return TelemetryEvent(
            event="agnt_api_error",
            category=EventCategory.API,
            success=False,
            duration_ms=latency_ms,
            error_message=error_message,
            properties={
                "model": model,
                "error_type": error_type,
            },
        )

    @staticmethod
    def api_retry(
        model: str = "",
        attempt: int = 0,
        reason: str = "",
    ) -> TelemetryEvent:
        """agnt_api_retry — API call retried.

        CC equivalent: tengu_api_retry
        """
        return TelemetryEvent(
            event="agnt_api_retry",
            category=EventCategory.API,
            properties={
                "model": model,
                "attempt": attempt,
                "reason": reason,
            },
        )

    # --- Compaction Events ---

    @staticmethod
    def compact_started(
        layer: int = 0,
        token_count: int = 0,
        threshold: int = 0,
    ) -> TelemetryEvent:
        """agnt_compact_started — Compaction layer initiated.

        CC equivalent: tengu_compact_started
        """
        return TelemetryEvent(
            event="agnt_compact_started",
            category=EventCategory.COMPACTION,
            properties={
                "layer": layer,
                "token_count": token_count,
                "threshold": threshold,
            },
        )

    @staticmethod
    def compact_success(
        layer: int = 0,
        tokens_before: int = 0,
        tokens_after: int = 0,
        tokens_reclaimed: int = 0,
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_compact_success — Compaction completed successfully.

        CC equivalent: tengu_compact_success
        """
        return TelemetryEvent(
            event="agnt_compact_success",
            category=EventCategory.COMPACTION,
            duration_ms=duration_ms,
            properties={
                "layer": layer,
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "tokens_reclaimed": tokens_reclaimed,
                "reclaim_pct": (round(tokens_reclaimed / tokens_before * 100, 1) if tokens_before > 0 else 0),
            },
        )

    @staticmethod
    def compact_failed(
        layer: int = 0,
        error_message: str = "",
        circuit_breaker_open: bool = False,
    ) -> TelemetryEvent:
        """agnt_compact_failed — Compaction failed.

        CC equivalent: tengu_compact_failed
        """
        return TelemetryEvent(
            event="agnt_compact_failed",
            category=EventCategory.COMPACTION,
            success=False,
            error_message=error_message,
            properties={
                "layer": layer,
                "circuit_breaker_open": circuit_breaker_open,
            },
        )

    # --- Tool Events ---

    @staticmethod
    def tool_use_success(
        tool_id: str = "",
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_tool_use_success — Tool executed successfully.

        CC equivalent: tengu_tool_use_success
        """
        return TelemetryEvent(
            event="agnt_tool_use_success",
            category=EventCategory.TOOL,
            duration_ms=duration_ms,
            properties={"tool_id": tool_id},
        )

    @staticmethod
    def tool_use_error(
        tool_id: str = "",
        error_message: str = "",
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_tool_use_error — Tool execution failed.

        CC equivalent: tengu_tool_use_error
        """
        return TelemetryEvent(
            event="agnt_tool_use_error",
            category=EventCategory.TOOL,
            success=False,
            duration_ms=duration_ms,
            error_message=error_message,
            properties={"tool_id": tool_id},
        )

    # --- Classifier Events ---

    @staticmethod
    def classifier_outcome(
        tool_id: str = "",
        verdict: str = "",
        stage: int = 1,
        fail_closed: bool = False,
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_classifier_outcome — Permission decision.

        CC equivalent: tengu_auto_mode_outcome
        """
        return TelemetryEvent(
            event="agnt_classifier_outcome",
            category=EventCategory.CLASSIFIER,
            duration_ms=duration_ms,
            properties={
                "tool_id": tool_id,
                "verdict": verdict,
                "stage": stage,
                "fail_closed": fail_closed,
            },
        )

    # --- Shell Security Events ---

    @staticmethod
    def bash_classifier(
        command_hash: str = "",
        subcommand_count: int = 0,
        verdict: str = "",
        unsafe_vars: list[str] | None = None,
    ) -> TelemetryEvent:
        """agnt_bash_classifier — Shell security classification.

        CC equivalent: tengu_internal_bash_classifier_result
        """
        return TelemetryEvent(
            event="agnt_bash_classifier",
            category=EventCategory.SHELL,
            properties={
                "command_hash": command_hash,
                "subcommand_count": subcommand_count,
                "verdict": verdict,
                "unsafe_vars": unsafe_vars or [],
            },
        )

    # --- Memory Events ---

    @staticmethod
    def memory_compact(
        memories_before: int = 0,
        memories_after: int = 0,
        deduped: int = 0,
        archived: int = 0,
    ) -> TelemetryEvent:
        """agnt_memory_compact — Session memory compaction.

        CC equivalent: tengu_sm_compact
        """
        return TelemetryEvent(
            event="agnt_memory_compact",
            category=EventCategory.MEMORY,
            properties={
                "memories_before": memories_before,
                "memories_after": memories_after,
                "deduped": deduped,
                "archived": archived,
            },
        )

    # --- VCR Events ---

    @staticmethod
    def vcr_record(
        cassette: str = "",
        entry_count: int = 0,
    ) -> TelemetryEvent:
        """agnt_vcr_record — VCR recording event."""
        return TelemetryEvent(
            event="agnt_vcr_record",
            category=EventCategory.VCR,
            properties={
                "cassette": cassette,
                "entry_count": entry_count,
            },
        )

    @staticmethod
    def vcr_replay_hit(cassette: str = "") -> TelemetryEvent:
        """agnt_vcr_replay_hit — VCR replay cache hit."""
        return TelemetryEvent(
            event="agnt_vcr_replay_hit",
            category=EventCategory.VCR,
            properties={"cassette": cassette},
        )

    @staticmethod
    def vcr_replay_miss(cassette: str = "") -> TelemetryEvent:
        """agnt_vcr_replay_miss — VCR replay cache miss."""
        return TelemetryEvent(
            event="agnt_vcr_replay_miss",
            category=EventCategory.VCR,
            success=False,
            properties={"cassette": cassette},
        )

    @staticmethod
    def vcr_diff_mismatch(
        cassette: str = "",
        diff_lines: int = 0,
    ) -> TelemetryEvent:
        """agnt_vcr_diff_mismatch — VCR diff regression detected."""
        return TelemetryEvent(
            event="agnt_vcr_diff_mismatch",
            category=EventCategory.VCR,
            success=False,
            properties={
                "cassette": cassette,
                "diff_lines": diff_lines,
            },
        )

    # --- Session Events ---

    @staticmethod
    def session_started(
        conversation_id: str = "",
        context_budget: int = 0,
    ) -> TelemetryEvent:
        """agnt_session_started — Agent session initialized."""
        return TelemetryEvent(
            event="agnt_session_started",
            category=EventCategory.SESSION,
            properties={
                "conversation_id": conversation_id,
                "context_budget": context_budget,
            },
        )

    @staticmethod
    def session_ended(
        conversation_id: str = "",
        total_turns: int = 0,
        total_tokens: int = 0,
        total_tool_calls: int = 0,
        duration_seconds: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_session_ended — Agent session completed."""
        return TelemetryEvent(
            event="agnt_session_ended",
            category=EventCategory.SESSION,
            duration_ms=duration_seconds * 1000,
            properties={
                "conversation_id": conversation_id,
                "total_turns": total_turns,
                "total_tokens": total_tokens,
                "total_tool_calls": total_tool_calls,
            },
        )

    # --- Error Events ---

    @staticmethod
    def context_decay_warning(
        tokens_remaining: int = 0,
        pct_remaining: float = 0.0,
        threshold: str = "",
    ) -> TelemetryEvent:
        """agnt_context_decay_warning — Context window pressure.

        CC equivalent: tengu_context_decay
        """
        return TelemetryEvent(
            event="agnt_context_decay_warning",
            category=EventCategory.ERROR,
            properties={
                "tokens_remaining": tokens_remaining,
                "pct_remaining": pct_remaining,
                "threshold": threshold,
            },
        )

    @staticmethod
    def circuit_breaker_open(
        subsystem: str = "",
        failure_count: int = 0,
    ) -> TelemetryEvent:
        """agnt_circuit_breaker_open — Circuit breaker tripped."""
        return TelemetryEvent(
            event="agnt_circuit_breaker_open",
            category=EventCategory.ERROR,
            success=False,
            properties={
                "subsystem": subsystem,
                "failure_count": failure_count,
            },
        )

    # --- Gemini API Events (P4.1) ---

    @staticmethod
    def gemini_interactions_turn(
        session_id: str = "",
        turn_index: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
        function_calls: int = 0,
    ) -> TelemetryEvent:
        """agnt_gemini_interactions_turn — Single Interactions API turn."""
        return TelemetryEvent(
            event="agnt_gemini_interactions_turn",
            category=EventCategory.GEMINI,
            duration_ms=latency_ms,
            properties={
                "session_id": session_id,
                "turn_index": turn_index,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "function_calls": function_calls,
            },
        )

    @staticmethod
    def gemini_interactions_session_end(
        session_id: str = "",
        total_turns: int = 0,
        total_tokens: int = 0,
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_gemini_interactions_session_end — Interactions session completed."""
        return TelemetryEvent(
            event="agnt_gemini_interactions_session_end",
            category=EventCategory.GEMINI,
            duration_ms=duration_ms,
            properties={
                "session_id": session_id,
                "total_turns": total_turns,
                "total_tokens": total_tokens,
            },
        )

    @staticmethod
    def gemini_interactions_error(
        session_id: str = "",
        error_type: str = "",
        error_message: str = "",
        reconnect_attempt: int = 0,
    ) -> TelemetryEvent:
        """agnt_gemini_interactions_error — Interactions API error."""
        return TelemetryEvent(
            event="agnt_gemini_interactions_error",
            category=EventCategory.GEMINI,
            success=False,
            error_message=error_message,
            properties={
                "session_id": session_id,
                "error_type": error_type,
                "reconnect_attempt": reconnect_attempt,
            },
        )

    # --- Deep Research Events (P4.1) ---

    @staticmethod
    def deep_research_started(
        query: str = "",
        depth: str = "",
        collaborative_planning: bool = False,
    ) -> TelemetryEvent:
        """agnt_deep_research_started — Deep Research sweep initiated."""
        return TelemetryEvent(
            event="agnt_deep_research_started",
            category=EventCategory.RESEARCH,
            properties={
                "query_length": len(query),
                "depth": depth,
                "collaborative_planning": collaborative_planning,
            },
        )

    @staticmethod
    def deep_research_completed(
        query: str = "",
        depth: str = "",
        sources_found: int = 0,
        duration_ms: float = 0.0,
        token_usage: int = 0,
    ) -> TelemetryEvent:
        """agnt_deep_research_completed — Deep Research sweep finished."""
        return TelemetryEvent(
            event="agnt_deep_research_completed",
            category=EventCategory.RESEARCH,
            duration_ms=duration_ms,
            properties={
                "query_length": len(query),
                "depth": depth,
                "sources_found": sources_found,
                "token_usage": token_usage,
            },
        )

    @staticmethod
    def deep_research_error(
        query: str = "",
        error_type: str = "",
        error_message: str = "",
        duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_deep_research_error — Deep Research sweep failed."""
        return TelemetryEvent(
            event="agnt_deep_research_error",
            category=EventCategory.RESEARCH,
            success=False,
            duration_ms=duration_ms,
            error_message=error_message,
            properties={
                "query_length": len(query),
                "error_type": error_type,
            },
        )

    # --- Rate Limit Events (OTel Histograms) ---

    @staticmethod
    def throttle_invocation(
        function_name: str = "",
        interval_ms: float = 0.0,
        was_suppressed: bool = False,
        elapsed_since_last_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_throttle_invocation — Tracks throttle execution/suppression.

        OTel histogram buckets on elapsed_since_last_ms reveal rate-limit
        pressure: spikes at low-ms values indicate callers hitting the
        suppression wall, while even distribution means healthy pacing.
        """
        return TelemetryEvent(
            event="agnt_throttle_invocation",
            category=EventCategory.TOOL,
            duration_ms=elapsed_since_last_ms,
            properties={
                "function_name": function_name,
                "interval_ms": interval_ms,
                "was_suppressed": was_suppressed,
            },
        )

    @staticmethod
    def debounce_invocation(
        function_name: str = "",
        wait_ms: float = 0.0,
        was_coalesced: bool = False,
        max_wait_triggered: bool = False,
        pending_duration_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_debounce_invocation — Tracks debounce coalescing behavior.

        OTel histogram on pending_duration_ms shows how long events queue
        before firing. Frequent max_wait_triggered=True signals the
        debounce ceiling is being hit under sustained load.
        """
        return TelemetryEvent(
            event="agnt_debounce_invocation",
            category=EventCategory.TOOL,
            duration_ms=pending_duration_ms,
            properties={
                "function_name": function_name,
                "wait_ms": wait_ms,
                "was_coalesced": was_coalesced,
                "max_wait_triggered": max_wait_triggered,
            },
        )

    @staticmethod
    def cooldown_check(
        throttle_name: str = "",
        cooldown_ms: float = 0.0,
        was_allowed: bool = True,
        time_until_next_ms: float = 0.0,
    ) -> TelemetryEvent:
        """agnt_cooldown_check — Tracks CooldownThrottle gate decisions.

        Histogram on time_until_next_ms shows how close callers are to
        the cooldown boundary. Clustering near 0ms = good pacing;
        clustering near cooldown_ms = premature retries.
        """
        return TelemetryEvent(
            event="agnt_cooldown_check",
            category=EventCategory.TOOL,
            properties={
                "throttle_name": throttle_name,
                "cooldown_ms": cooldown_ms,
                "was_allowed": was_allowed,
                "time_until_next_ms": time_until_next_ms,
            },
        )
