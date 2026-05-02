# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Gemini Core service — model fallback chain and API wrapper.

Stub module providing the interface expected by test_gemini_failover.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Default fallback chain matching production configuration
MODEL_FALLBACK_CHAIN: list[str] = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


class GeminiAntigravity:
    """Gemini API client with automatic model failover.

    When a model is unavailable or rate-limited, automatically falls back
    to the next model in the chain.
    """

    def __init__(
        self,
        api_key: str = "test-key",
        fallback_chain: list[str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.fallback_chain = fallback_chain or MODEL_FALLBACK_CHAIN
        self.timeout = timeout
        self._current_model_idx = 0
        self._failure_counts: dict[str, int] = {}

    @property
    def current_model(self) -> str:
        """Return the currently active model name."""
        return self.fallback_chain[self._current_model_idx]

    def failover(self) -> str | None:
        """Advance to the next model in the chain. Returns None if exhausted."""
        self._current_model_idx += 1
        if self._current_model_idx >= len(self.fallback_chain):
            self._current_model_idx = len(self.fallback_chain) - 1
            return None
        return self.current_model

    def reset(self) -> None:
        """Reset to the primary model."""
        self._current_model_idx = 0
        self._failure_counts.clear()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response, failing over on errors."""
        for _i in range(len(self.fallback_chain)):
            try:
                return self._call_model(prompt, **kwargs)
            except Exception:
                model = self.current_model
                self._failure_counts[model] = self._failure_counts.get(model, 0) + 1
                next_model = self.failover()
                if next_model is None:
                    raise
        raise RuntimeError("All models in fallback chain exhausted")

    def _call_model(self, prompt: str, **kwargs: Any) -> str:
        """Call the current model. Override in tests via mock."""
        raise NotImplementedError("Stub — mock this method in tests")
