# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge Architecture Framework — v2.0.0 (Rich Hickey Refactor)"""

try:
    from .formatter import JudgeVerdictFormatter
    from .judge import JudgeArchitecture
    from .models import Decision, DecisionStatus, JudgeVerdict, RiskLevel

    __all__ = [
        "Decision",
        "DecisionStatus",
        "JudgeArchitecture",
        "JudgeVerdict",
        "JudgeVerdictFormatter",
        "RiskLevel",
    ]
except ImportError:
    # Some submodules depend on src.kosmos.doctrine (not yet built).
    # Individual submodules (models.py, infrastructure.py) remain
    # importable if their own deps are satisfied.
    __all__ = []
