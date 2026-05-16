# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pnkln Standardized Tool Schemas
================================

SK PATTERN 3: Plugin Schema Standardization

Type-annotated tools for LLM function calling with:
- Explicit type hints
- Detailed descriptions
- Structured I/O validation
- LangGraph/AutoGen compatibility

Tools:
- shadowtag_embed_video: DCT watermarking for video
- shadowtag_embed_audio: Ultrasonic watermarking for audio
- governance_validate: ATP 5-19 validation
- risk_assess: Monte Carlo risk assessment
"""

from pnkln.tools.shadowtag_tools import shadowtag_embed_video, shadowtag_embed_audio, shadowtag_verify
from pnkln.tools.governance_tools import governance_validate, risk_assess_monte_carlo

__all__ = [
    "shadowtag_embed_video",
    "shadowtag_embed_audio",
    "shadowtag_verify",
    "governance_validate",
    "risk_assess_monte_carlo",
]
