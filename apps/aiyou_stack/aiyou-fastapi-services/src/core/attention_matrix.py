"""
================================================================================
attention_matrix.py

Philosophical Mandate:
Implementation of arXiv:2512.14982 (Prompt Repetition Improves Non-Reasoning LLMs).
Calculates and injects the highest-priority operator_invariants into the final
pre-fill context of downstream Edge LLMs to mathematically force Attention Alignment.
================================================================================
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Primary location of the canonical UphillSnowball Operator Invariants
DEFAULT_INVARIANT_PATH = Path(
    "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/operator_invariants.json"
)


class AttentionInjector:
    """
    Ingests the master operator_invariants.json payload (58+ dicts).
    Dynamically slices the matrix down to the top-N critical laws
    based on contextual keywords, and returns an ArXiv Prompt Repetition tail.
    """

    def __init__(self, json_path: Path = DEFAULT_INVARIANT_PATH):
        self.json_path = json_path
        self.invariants = self._load_invariants()

    def _load_invariants(self) -> list[dict]:
        if not self.json_path.exists():
            logger.warning(
                f"CRITICAL: Operator invariants missing at {self.json_path}. Falling back to empty matrix."
            )
            return []

        try:
            with open(self.json_path, encoding="utf-8") as f:
                data = json.load(f)
                return data.get("invariants", [])
        except Exception as e:
            logger.error(f"Failed to parse invariants JSON: {e}")
            return []

    def _score_invariant(self, invariant: dict, context_tags: list[str]) -> int:
        """
        Determines the relevance of an invariant relative to the current task.
        Prioritizes Stage 6, State A (YOLO), and Zero-Trust mechanically.
        """
        score = 0
        name = invariant.get("name", "").lower()
        desc = invariant.get("description", "").lower()

        # Absolute universal baselines
        if "model isolation doctrine" in name:
            score += 1000
        if "arXiv 2512.14982" in name or "prompt repetition" in name:
            score += 950
        if "sovereign silicon" in name:
            score += 500

        # Contextual scoring based on passed string tags
        for tag in context_tags:
            tag = tag.lower()
            if tag in name:
                score += 100
            if tag in desc:
                score += 50

        return score

    def build_attention_tail(self, context_tags: list[str], top_n: int = 3) -> str:
        """
        Executes the Head-and-Tail Compression Loop.
        1. Filters and scores all 58 invariants against the context.
        2. Slices the exact Top N critical rules.
        3. Formats them as an explicitly hostile Promp Repetition suffix.
        """
        if not self.invariants:
            return ""

        # Score and sort invariants descending
        scored = sorted(
            self.invariants, key=lambda x: self._score_invariant(x, context_tags), reverse=True
        )

        # Slice the critical threshold
        critical_slice = scored[:top_n]

        # Construct the ArXiv Injection
        tail_payload = [
            "---",
            "[arXiv:2512.14982] CRITICAL ATTENTION ANCHOR (YOLO MODE LIMITERS):",
            "Before generating your final token response, you MUST adhere to these absolute Sovereign Invariants:\n",
        ]

        for i, inv in enumerate(critical_slice, 1):
            tail_payload.append(f"{i}. [{inv.get('name')}] {inv.get('description')}")

        tail_payload.append("\nProceed with Generation:")

        return "\n".join(tail_payload)


# Example test logic if run directly
if __name__ == "__main__":
    injector = AttentionInjector()
    # Test a UI / FastAPI context block
    print("Testing Context Injection: ['FastAPI', 'Zero-Trust', 'React']")
    output = injector.build_attention_tail(["FastAPI", "Zero-Trust", "React"])
    print(output)
