# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Discovery — Core implementation.

Ported from Claude Code v2.1.91 toolSearch.ts:
  - ToolSearchMode: tst / tst-auto / standard
  - DEFAULT_AUTO_TOOL_SEARCH_PERCENTAGE = 10
  - CHARS_PER_TOKEN = 2.5 approximation
  - modelSupportsToolReference: model capability check
  - calculateDeferredToolDescriptionChars: budget calculation
  - isToolSearchEnabled / isToolSearchEnabledOptimistic

All GrowthBook feature flag dependencies replaced with local config.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)

# Constants from upstream
DEFAULT_AUTO_TOOL_SEARCH_PERCENTAGE: int = 10
CHARS_PER_TOKEN: float = 2.5


class ToolSearchMode(StrEnum):
    """Tool search mode enum.

    - TST: Tool Search Technology — explicit tool reference mode
    - TST_AUTO: Automatic mode with percentage-based rollout
    - STANDARD: Standard mode — all tools loaded eagerly
    """

    TST = "tst"
    TST_AUTO = "tst-auto"
    STANDARD = "standard"


@dataclass(frozen=True, slots=True)
class ToolSearchConfig:
    """Configuration for tool search behavior."""

    mode: ToolSearchMode = ToolSearchMode.STANDARD
    auto_percentage: int = DEFAULT_AUTO_TOOL_SEARCH_PERCENTAGE
    max_deferred_tokens: int = 4096
    enabled_models: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "gemini-3.1-flash-lite",
                "gemini-3.1-flash-lite-preview-thinking",
                "gemini-3-pro",
                "gemini-3.1-pro",
            }
        )
    )


@dataclass
class DeferredToolEntry:
    """A tool registered for deferred/lazy loading."""

    name: str
    description: str
    module_path: str
    char_cost: int = 0
    priority: int = 0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.char_cost == 0:
            self.char_cost = len(self.description)

    @property
    def token_cost(self) -> float:
        """Estimated token cost of including this tool's description."""
        return self.char_cost / CHARS_PER_TOKEN


class ToolDiscovery:
    """Dynamic deferred tool loading with threshold-based auto-enable.

    Manages a registry of tools that can be lazily loaded based on
    model capabilities and token budget constraints.
    """

    def __init__(
        self,
        config: ToolSearchConfig | None = None,
        model: str = "gemini-3.1-flash-lite",
    ) -> None:
        self._config = config or ToolSearchConfig()
        self._model = model
        self._registry: dict[str, DeferredToolEntry] = {}
        self._loaded: set[str] = set()

    @property
    def config(self) -> ToolSearchConfig:
        return self._config

    @property
    def model(self) -> str:
        return self._model

    def register_tool(self, entry: DeferredToolEntry) -> None:
        """Register a tool for deferred loading."""
        self._registry[entry.name] = entry
        logger.debug("Registered deferred tool: %s", entry.name)

    def unregister_tool(self, name: str) -> bool:
        """Unregister a deferred tool. Returns True if it was registered."""
        if name in self._registry:
            del self._registry[name]
            self._loaded.discard(name)
            return True
        return False

    def is_enabled(self) -> bool:
        """Check if tool search is enabled for current config/model.

        Mirrors isToolSearchEnabled from upstream.
        """
        if self._config.mode == ToolSearchMode.STANDARD:
            return False

        if not self._model_supports_tool_reference():
            return False

        if self._config.mode == ToolSearchMode.TST:
            return True

        # TST_AUTO: percentage-based rollout (locally always enabled)
        return self._config.mode == ToolSearchMode.TST_AUTO

    def is_enabled_optimistic(self) -> bool:
        """Optimistic check — returns True if mode could be enabled.

        Mirrors isToolSearchEnabledOptimistic from upstream.
        Used for pre-computing deferred descriptions before mode is finalized.
        """
        return self._config.mode in (ToolSearchMode.TST, ToolSearchMode.TST_AUTO)

    def _model_supports_tool_reference(self) -> bool:
        """Check if the current model supports tool references.

        Negative test — models NOT in the enabled set are excluded.
        """
        return self._model in self._config.enabled_models

    def get_deferred_tools(self) -> list[DeferredToolEntry]:
        """Get all deferred tools sorted by priority (highest first)."""
        return sorted(
            self._registry.values(),
            key=lambda t: t.priority,
            reverse=True,
        )

    def get_deferred_tools_within_budget(self, max_tokens: int | None = None) -> list[DeferredToolEntry]:
        """Get deferred tools that fit within the token budget.

        Args:
            max_tokens: Override for max deferred tokens. Uses config default
                        if not specified.

        Returns:
            List of tools that fit within budget, sorted by priority.
        """
        budget = max_tokens or self._config.max_deferred_tokens
        sorted_tools = self.get_deferred_tools()

        result = []
        consumed = 0.0

        for tool in sorted_tools:
            if consumed + tool.token_cost <= budget:
                result.append(tool)
                consumed += tool.token_cost

        return result

    def calculate_deferred_description_chars(self) -> int:
        """Calculate total character cost of all deferred tool descriptions.

        Mirrors calculateDeferredToolDescriptionChars from upstream.
        """
        return sum(entry.char_cost for entry in self._registry.values())

    def calculate_deferred_description_tokens(self) -> float:
        """Calculate estimated total token cost of all deferred descriptions."""
        return self.calculate_deferred_description_chars() / CHARS_PER_TOKEN

    def mark_loaded(self, name: str) -> bool:
        """Mark a deferred tool as loaded. Returns True if it was deferred."""
        if name in self._registry:
            self._loaded.add(name)
            return True
        return False

    @property
    def stats(self) -> dict[str, int | float]:
        """Get registry statistics."""
        return {
            "total_registered": len(self._registry),
            "total_loaded": len(self._loaded),
            "total_deferred": len(self._registry) - len(self._loaded),
            "total_chars": self.calculate_deferred_description_chars(),
            "total_tokens": self.calculate_deferred_description_tokens(),
        }
