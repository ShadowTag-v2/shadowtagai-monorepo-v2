# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pnkln Tokable Vertical
Create emotion-first creator flows.
"""

from __future__ import annotations

from vertexai.generative_models import GenerativeModel, Part

from src.pnkln.prompts import PNKLN_PROMPTS


def tokable_script(
    theme: str, persona: str, model_name: str = "gemini-3.1-flash-lite-preview-001"
) -> str:
    """Write a 45-90s emotion-first script."""
    model = GenerativeModel(model_name)
    system_prompt = PNKLN_PROMPTS.get("sys_tokable", "You are pnkln-tokable.")

    user_content = f"{theme} | {persona}"

    response = model.generate_content(
        [
            {"role": "system", "parts": [Part.from_text(system_prompt)]},  # type: ignore
            {"role": "user", "parts": [Part.from_text(user_content)]},  # type: ignore
        ],
        generation_config={"temperature": 0.55, "response_mime_type": "application/json"},
    )
    return response.text
