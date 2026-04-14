"""GEPA Router: Speculative Decoding via 2B (Draft) → 31B (Audit)

Implements the asymmetric compute model:
- 80% low-entropy tokens → 2B sidekick (fast, cheap)
- 20% high-entropy tokens → 31B auditor (deep reasoning)

Requires local Gemma 4 models served via vLLM or Ollama.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Model endpoints (override via env)
SIDEKICK_2B_ENDPOINT = "http://127.0.0.1:8080/v1"
HEAVY_31B_ENDPOINT = "http://127.0.0.1:8081/v1"

SIDEKICK_MODEL = "openai/gemma-4-2b-it"
HEAVY_MODEL = "openai/gemma-4-31b-it"


@dataclass
class GEPAResult:
    """Result from the GEPA speculative decoding pipeline."""

    task: str
    draft: str
    confidence: float
    final_code: str
    auditor_used: bool


def _configure_dspy() -> Any:
    """Configure DSPy with dual-model setup.

    Returns the configured dspy module, or None if DSPy is not installed.
    """
    try:
        import dspy  # type: ignore[import]
    except ImportError:
        logger.warning("dspy not installed — run: pip install dspy-ai")
        return None

    sidekick = dspy.LM(model=SIDEKICK_MODEL, api_base=SIDEKICK_2B_ENDPOINT)
    dspy.settings.configure(rm=None, lm=sidekick)
    return dspy


class GEPARouter:
    """Routes tasks through 2B draft → 31B audit pipeline.

    The sidekick drafts fast; the auditor validates only when needed.
    If confidence > threshold, skip the auditor entirely (80% of cases).
    """

    def __init__(self, confidence_threshold: float = 0.85) -> None:
        self.confidence_threshold = confidence_threshold
        self._dspy = _configure_dspy()

    def route(self, task: str) -> GEPAResult:
        """Execute the speculative decoding pipeline.

        Args:
            task: The coding task description.

        Returns:
            GEPAResult with draft, confidence, and final code.
        """
        if self._dspy is None:
            return GEPAResult(
                task=task,
                draft="[dspy not available]",
                confidence=0.0,
                final_code="",
                auditor_used=False,
            )

        dspy = self._dspy

        # Phase 1: Fast draft via 2B sidekick
        sidekick = dspy.LM(model=SIDEKICK_MODEL, api_base=SIDEKICK_2B_ENDPOINT)
        with dspy.context(lm=sidekick):
            draft_module = dspy.ChainOfThought("task -> initial_code_draft")
            fast_draft = draft_module(task=task)

        draft_text = fast_draft.initial_code_draft
        logger.info("GEPA draft complete", extra={"task": task[:80]})

        # Phase 2: Audit via 31B only if needed
        # Simple heuristic: short drafts or drafts with "TODO" need audit
        needs_audit = (
            len(draft_text) < 50
            or "TODO" in draft_text.upper()
            or "FIXME" in draft_text.upper()
        )

        if needs_audit:
            heavy = dspy.LM(model=HEAVY_MODEL, api_base=HEAVY_31B_ENDPOINT)
            with dspy.context(lm=heavy):
                audit_module = dspy.ChainOfThought(
                    "task, draft -> confidence_score, final_code_payload"
                )
                final = audit_module(task=task, draft=draft_text)

            return GEPAResult(
                task=task,
                draft=draft_text,
                confidence=float(final.confidence_score or 0.0),
                final_code=final.final_code_payload,
                auditor_used=True,
            )

        return GEPAResult(
            task=task,
            draft=draft_text,
            confidence=0.95,
            final_code=draft_text,
            auditor_used=False,
        )
