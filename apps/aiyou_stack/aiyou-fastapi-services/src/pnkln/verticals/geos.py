"""Pnkln Geos Vertical
Summarize geo/polygon events and economic triggers.
"""

from __future__ import annotations

from vertexai.generative_models import GenerativeModel, Part

from src.pnkln.prompts import PNKLN_PROMPTS


def geos_skim(text: str, model_name: str = "gemini-3.1-flash-lite-preview-001") -> str:
    """Summarize geo triggers, actors, capital flow, compliance."""
    model = GenerativeModel(model_name)
    system_prompt = PNKLN_PROMPTS.get("sys_geos", "You are pnkln-geos.")

    response = model.generate_content(
        [
            {"role": "system", "parts": [Part.from_text(system_prompt)]},  # type: ignore
            {"role": "user", "parts": [Part.from_text(text)]},  # type: ignore
        ],
        generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
    )
    return response.text
