"""Pnkln Swiper Vertical
Geo-beacon commerce films optimization.
"""

from __future__ import annotations

import base64

from vertexai.generative_models import GenerativeModel, Part

from src.pnkln.prompts import PNKLN_PROMPTS


def swiper_plan(query: str, model_name: str = "gemini-1.5-flash-001") -> str:
    """Generate a Swiper plan based on a query."""
    model = GenerativeModel(model_name)
    system_prompt = PNKLN_PROMPTS.get("sys_swiper", "You are pnkln-swiper.")

    response = model.generate_content(
        [
            {"role": "system", "parts": [Part.from_text(system_prompt)]},  # type: ignore
            {"role": "user", "parts": [Part.from_text(query)]},  # type: ignore
        ],
        generation_config={"temperature": 0.3},
    )
    return response.text


def swiper_visualize(img_b64: str, gear: str, model_name: str = "gemini-1.5-flash-001") -> str:
    """Visualize gear placement in a scene."""
    model = GenerativeModel(model_name)
    prompt_text = f"Blend {gear} into scene, return JSON placements and style."

    try:
        image_data = base64.b64decode(img_b64)
    except Exception:
        return "Error: Invalid base64 image data."

    response = model.generate_content(
        [
            {"role": "system", "parts": [Part.from_text("Return JSON only.")]},  # type: ignore
            {
                "role": "user",
                "parts": [
                    Part.from_data(mime_type="image/jpeg", data=image_data),  # type: ignore
                    Part.from_text(prompt_text),  # type: ignore
                ],
            },
        ],
        generation_config={"temperature": 0.2},
    )
    return response.text
