# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Core Stack Integration.

The four pillars:
1. JR Engine - Purpose/Reasons/Brakes validation
2. Cor - Unified execution brain
3. ShadowTag - DCT watermarking & audit trail
4. NS - Semantic memory retrieval

NOTE: All imports are lazy to prevent cascade failures from
``from ..core.gemini_function_calling`` relative imports in cor.py
and judge_six.py, which break when pnkln is imported as a top-level
package (``./core/`` at repo root shadows ``src/core/``).
"""

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
  "CorOrchestrator": (".cor", "CorOrchestrator"),
  "JudgeSix": (".judge_six", "JudgeSix"),
  "JRValidation": (".judge_six", "JRValidation"),
  "ValidationResult": (".judge_six", "ValidationResult"),
  "ShadowTag": (".shadowtag", "ShadowTag"),
  "SemanticMemory": (".ns", "SemanticMemory"),
}


def __getattr__(name: str):
  """Lazy import all public symbols to avoid cascade import failures."""
  if name in _LAZY_IMPORTS:
    module_path, attr = _LAZY_IMPORTS[name]
    import importlib
    mod = importlib.import_module(module_path, __name__)
    return getattr(mod, attr)
  raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
