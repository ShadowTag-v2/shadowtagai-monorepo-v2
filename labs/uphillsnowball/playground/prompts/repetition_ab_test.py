"""Playground: Prompt repetition A/B test.

Tests the arXiv 2512.14982 prompt repetition technique on flash-lite models.
Measures accuracy delta with/without repeated instructions.

Per AGENTS.md: labs must not redefine product truth.
Per GEMINI.md: Prompt repetition applies ONLY to non-reasoning tiers.
"""

from __future__ import annotations

# Placeholder — wire up when gemini-3.1-flash-lite-preview is accessible locally.
# This experiment validates the 1-8% accuracy boost claim.

EXPERIMENT_TEMPLATE = {
    "name": "prompt_repetition_ab",
    "model": "gemini-3.1-flash-lite-preview",
    "conditions": {
        "control": "single instruction in system prompt",
        "treatment": "instruction repeated 2x in context",
    },
    "metrics": ["accuracy", "latency_ms", "output_tokens"],
    "sample_size": 100,
    "status": "not_started",
}

if __name__ == "__main__":
    import json

    print(json.dumps(EXPERIMENT_TEMPLATE, indent=2))
