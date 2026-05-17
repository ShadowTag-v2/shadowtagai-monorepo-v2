# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""High-level prompt runners and templates."""

from __future__ import annotations
from vertexai.generative_models import Part
from .vertex import gemini

_gm = gemini()
PROMPTS = {
  "spec": "You are PNKLN Systems. Produce a machine-parseable JSON plan.",
  "contract": "Summarize contract positions into his/hers matrix JSON.",
  "lawcal": "Extract deadlines & triggers JSON.",
  "neg": "List open issues, missing terms JSON.",
  "risk": "Top-5 risks JSON with mitigations.",
}


def run(tag: str, text: str) -> str:
  tpl = PROMPTS[tag]
  return _gm.generate_content([Part.from_text(tpl), Part.from_text(text)]).text
