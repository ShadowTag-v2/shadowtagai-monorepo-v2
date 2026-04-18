"""Pnkln VC Mirror Vertical
Investor thesis extraction and pitch copy generation.
"""

from __future__ import annotations

from vertexai.generative_models import GenerativeModel, Part

from src.pnkln.prompts import PNKLN_PROMPTS


def vcmirror(profile_txt: str, company_info: str, model_name: str = "gemini-3.1-flash-lite-preview") -> str:
    """Extract investor thesis and produce pitch copy."""
    model = GenerativeModel(model_name)
    system_prompt = PNKLN_PROMPTS.get("sys_vcm", "You are pnkln-vc-mirror.")

    user_content = f"Investor Profile:\n{profile_txt}\n\nCompany Info:\n{company_info}"

    response = model.generate_content(
        [
            {"role": "system", "parts": [Part.from_text(system_prompt)]},  # type: ignore
            {"role": "user", "parts": [Part.from_text(user_content)]},  # type: ignore
        ],
        generation_config={"temperature": 0.2},
    )
    return response.text
