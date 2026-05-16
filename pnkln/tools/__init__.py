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

NOTE: Imports are lazy to prevent cascade failures from
governance_tools → pnkln.core.judge_six_pipeline (missing module).
"""

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "shadowtag_embed_video": ("pnkln.tools.shadowtag_tools", "shadowtag_embed_video"),
    "shadowtag_embed_audio": ("pnkln.tools.shadowtag_tools", "shadowtag_embed_audio"),
    "shadowtag_verify": ("pnkln.tools.shadowtag_tools", "shadowtag_verify"),
    "governance_validate": ("pnkln.tools.governance_tools", "governance_validate"),
    "risk_assess_monte_carlo": ("pnkln.tools.governance_tools", "risk_assess_monte_carlo"),
}


def __getattr__(name: str):
    """Lazy import all public symbols to avoid cascade import failures."""
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())

