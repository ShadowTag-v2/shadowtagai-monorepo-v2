# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cost Tracker — Session-scoped token usage and cost tracking.

Ported from src/cost-tracker.ts (Claude Code v2.1.91, 295 lines).

Batch 2 Security Constraints:
  - NO external API tracking (Datadog counters stripped)
  - NO analytics/logEvent calls
  - NO chalk rendering (text-only formatting)
  - Strictly local cost persistence via JSON config files
  - NO GrowthBook feature flags (fastMode check removed)

Usage:
    from agnt_cost_tracker import CostTracker

    tracker = CostTracker()
    tracker.add_usage("gemini-3.1-pro", input_tokens=1200, output_tokens=500)
    print(tracker.format_total_cost())
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "CostTracker",
    "ModelUsage",
    "StoredCostState",
    "format_cost",
    "format_duration",
    "format_number",
]


# ---------------------------------------------------------------------------
# Formatting helpers — ported from src/utils/format.ts
# ---------------------------------------------------------------------------


def format_number(n: int) -> str:
    """Format an integer with comma separators."""
    return f"{n:,}"


def format_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs:.0f}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins}m"


def format_cost(cost: float, max_decimal_places: int = 4) -> str:
    """Format a USD cost value."""
    if cost > 0.5:
        rounded = round(cost * 100) / 100
        return f"${rounded:.2f}"
    return f"${cost:.{max_decimal_places}f}"


# ---------------------------------------------------------------------------
# Model cost table — Gemini pricing (as of 2026-05)
# ---------------------------------------------------------------------------

# Per-token pricing in USD: (input, output, cache_read, cache_write)
_MODEL_COST_TABLE: dict[str, tuple[float, float, float, float]] = {
    "gemini-3.1-pro": (1.25e-6, 5.0e-6, 0.3125e-6, 1.5625e-6),
    "gemini-3.1-flash": (0.15e-6, 0.6e-6, 0.0375e-6, 0.1875e-6),
    "gemini-3.1-flash-lite-preview-thinking": (0.075e-6, 0.3e-6, 0.01875e-6, 0.09375e-6),
    "gemini-3-pro": (1.25e-6, 5.0e-6, 0.3125e-6, 1.5625e-6),
    "gemini-3-flash": (0.15e-6, 0.6e-6, 0.0375e-6, 0.1875e-6),
    "gemini-2.5-pro": (1.25e-6, 10.0e-6, 0.3125e-6, 3.175e-6),
    "gemini-2.5-flash": (0.15e-6, 0.6e-6, 0.0375e-6, 0.1875e-6),
}


def _calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> float:
    """Calculate USD cost for a given model and token counts."""
    canonical = model.rsplit("/", 1)[-1].lower().strip()

    # Try exact match, then prefix match
    pricing = _MODEL_COST_TABLE.get(canonical)
    if pricing is None:
        for key, val in _MODEL_COST_TABLE.items():
            if canonical.startswith(key):
                pricing = val
                break

    if pricing is None:
        return 0.0  # Unknown model — flag via has_unknown_model_cost

    inp_rate, out_rate, cache_read_rate, cache_write_rate = pricing
    return input_tokens * inp_rate + output_tokens * out_rate + cache_read_tokens * cache_read_rate + cache_write_tokens * cache_write_rate


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ModelUsage:
    """Per-model accumulated usage counters."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    web_search_requests: int = 0
    cost_usd: float = 0.0
    context_window: int = 0
    max_output_tokens: int = 0


@dataclass
class StoredCostState:
    """Serializable snapshot of session costs for persistence."""

    total_cost_usd: float = 0.0
    total_api_duration: float = 0.0
    total_api_duration_without_retries: float = 0.0
    total_tool_duration: float = 0.0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    last_duration: float | None = None
    model_usage: dict[str, dict[str, Any]] | None = None


# ---------------------------------------------------------------------------
# CostTracker — main class
# ---------------------------------------------------------------------------


class CostTracker:
    """Session-scoped cost tracker.

    Thread-safe for single-writer use. All external API tracking has been
    stripped — counters are strictly in-process.
    """

    def __init__(self, session_id: str | None = None) -> None:
        self._session_id = session_id
        self._total_cost_usd: float = 0.0
        self._total_api_duration: float = 0.0
        self._total_api_duration_without_retries: float = 0.0
        self._total_tool_duration: float = 0.0
        self._total_duration: float = 0.0
        self._total_lines_added: int = 0
        self._total_lines_removed: int = 0
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._total_cache_read_tokens: int = 0
        self._total_cache_write_tokens: int = 0
        self._total_web_search_requests: int = 0
        self._has_unknown_model_cost: bool = False
        self._model_usage: dict[str, ModelUsage] = {}
        self._start_time: float = time.monotonic()

    # -- Properties ----------------------------------------------------------

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def total_cost_usd(self) -> float:
        return self._total_cost_usd

    @property
    def total_duration(self) -> float:
        return time.monotonic() - self._start_time

    @property
    def total_api_duration(self) -> float:
        return self._total_api_duration

    @property
    def total_input_tokens(self) -> int:
        return self._total_input_tokens

    @property
    def total_output_tokens(self) -> int:
        return self._total_output_tokens

    @property
    def total_cache_read_tokens(self) -> int:
        return self._total_cache_read_tokens

    @property
    def total_cache_write_tokens(self) -> int:
        return self._total_cache_write_tokens

    @property
    def total_lines_added(self) -> int:
        return self._total_lines_added

    @property
    def total_lines_removed(self) -> int:
        return self._total_lines_removed

    @property
    def has_unknown_model_cost(self) -> bool:
        return self._has_unknown_model_cost

    @property
    def model_usage(self) -> dict[str, ModelUsage]:
        return dict(self._model_usage)

    # -- Mutation methods ----------------------------------------------------

    def add_usage(
        self,
        model: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
        web_search_requests: int = 0,
        api_duration: float = 0.0,
    ) -> float:
        """Record a single API call's usage. Returns the incremental cost."""
        cost = _calculate_cost(model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens)

        # Check for unknown model
        canonical = model.rsplit("/", 1)[-1].lower().strip()
        pricing = _MODEL_COST_TABLE.get(canonical)
        if pricing is None and not any(canonical.startswith(k) for k in _MODEL_COST_TABLE):
            self._has_unknown_model_cost = True

        # Accumulate totals
        self._total_cost_usd += cost
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._total_cache_read_tokens += cache_read_tokens
        self._total_cache_write_tokens += cache_write_tokens
        self._total_web_search_requests += web_search_requests
        self._total_api_duration += api_duration

        # Per-model usage
        usage = self._model_usage.setdefault(model, ModelUsage())
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.cache_read_input_tokens += cache_read_tokens
        usage.cache_creation_input_tokens += cache_write_tokens
        usage.web_search_requests += web_search_requests
        usage.cost_usd += cost

        return cost

    def add_lines_changed(self, added: int = 0, removed: int = 0) -> None:
        """Record lines added/removed."""
        self._total_lines_added += added
        self._total_lines_removed += removed

    def add_tool_duration(self, duration: float) -> None:
        """Record tool execution duration."""
        self._total_tool_duration += duration

    # -- Reset ---------------------------------------------------------------

    def reset(self) -> None:
        """Reset all counters (for tests or session restart)."""
        self._total_cost_usd = 0.0
        self._total_api_duration = 0.0
        self._total_api_duration_without_retries = 0.0
        self._total_tool_duration = 0.0
        self._total_lines_added = 0
        self._total_lines_removed = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_cache_read_tokens = 0
        self._total_cache_write_tokens = 0
        self._total_web_search_requests = 0
        self._has_unknown_model_cost = False
        self._model_usage.clear()
        self._start_time = time.monotonic()

    # -- Formatting ----------------------------------------------------------

    def format_total_cost(self) -> str:
        """Produce a multi-line cost summary (text-only, no chalk)."""
        cost_display = format_cost(self._total_cost_usd)
        if self._has_unknown_model_cost:
            cost_display += " (costs may be inaccurate due to usage of unknown models)"

        model_display = self._format_model_usage()

        added_label = "line" if self._total_lines_added == 1 else "lines"
        removed_label = "line" if self._total_lines_removed == 1 else "lines"

        return (
            f"Total cost:            {cost_display}\n"
            f"Total duration (API):  {format_duration(self._total_api_duration)}\n"
            f"Total duration (wall): {format_duration(self.total_duration)}\n"
            f"Total code changes:    {self._total_lines_added} {added_label} added, "
            f"{self._total_lines_removed} {removed_label} removed\n"
            f"{model_display}"
        )

    def _format_model_usage(self) -> str:
        """Format per-model usage breakdown."""
        if not self._model_usage:
            return "Usage:                 0 input, 0 output, 0 cache read, 0 cache write"

        result = "Usage by model:"
        for model_name, usage in self._model_usage.items():
            # Canonicalize to short name
            short = model_name.rsplit("/", 1)[-1]
            parts = [
                f"  {format_number(usage.input_tokens)} input",
                f"{format_number(usage.output_tokens)} output",
                f"{format_number(usage.cache_read_input_tokens)} cache read",
                f"{format_number(usage.cache_creation_input_tokens)} cache write",
            ]
            if usage.web_search_requests > 0:
                parts.append(f"{format_number(usage.web_search_requests)} web search")
            parts.append(f"({format_cost(usage.cost_usd)})")
            usage_str = ", ".join(parts)
            result += f"\n{short:>21}:{usage_str}"

        return result

    # -- Persistence ---------------------------------------------------------

    def save_to_file(self, path: Path) -> None:
        """Persist current state to a JSON file."""
        state = StoredCostState(
            total_cost_usd=self._total_cost_usd,
            total_api_duration=self._total_api_duration,
            total_api_duration_without_retries=self._total_api_duration_without_retries,
            total_tool_duration=self._total_tool_duration,
            total_lines_added=self._total_lines_added,
            total_lines_removed=self._total_lines_removed,
            last_duration=self.total_duration,
            model_usage={model: asdict(usage) for model, usage in self._model_usage.items()},
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(state), indent=2))

    def restore_from_file(self, path: Path, session_id: str | None = None) -> bool:
        """Restore cost state from a JSON file.

        Returns ``True`` if state was restored, ``False`` otherwise.
        """
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return False

        self._total_cost_usd = data.get("total_cost_usd", 0.0)
        self._total_api_duration = data.get("total_api_duration", 0.0)
        self._total_api_duration_without_retries = data.get("total_api_duration_without_retries", 0.0)
        self._total_tool_duration = data.get("total_tool_duration", 0.0)
        self._total_lines_added = data.get("total_lines_added", 0)
        self._total_lines_removed = data.get("total_lines_removed", 0)

        # Restore per-model usage
        if data.get("model_usage"):
            for model, usage_dict in data["model_usage"].items():
                self._model_usage[model] = ModelUsage(**usage_dict)

        return True
