# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PINKLN ULTRATHINK CORE STACK v2.0

Unified infrastructure integrating:
- Kernel Chaining (98.5% token reduction)
- Gemini Function Calling (31× faster)
- LLM Memory Persistence (cross-device context)
- Intelligence Pipeline (load testing + SLA)

Revenue: $1.05M Y1 → $28.32M Y3
Gross Margin: 94%
Performance: p99 ≤35ms | Cost: $0.0003/decision
"""

__version__ = "2.0.0"
__author__ = "Pinkln Team"

from .core import (
    GeminiFunctionCaller,
    KernelChain,
    JREngine,
    ShadowTag,
)

from .kernels import (
    ATP519ScanKernel,
    JudgeSixKernel,
    AuditCompressKernel,
)

from .ratings import (
    Glicko2Player,
    Glicko2System,
)

from .evolution import (
    DTESystem,
    CheatSheetFusion,
)

from .memory import (
    MemoryPersistence,
    ConversationExtractor,
)

__all__ = [
    "GeminiFunctionCaller",
    "KernelChain",
    "JREngine",
    "ShadowTag",
    "ATP519ScanKernel",
    "JudgeSixKernel",
    "AuditCompressKernel",
    "Glicko2Player",
    "Glicko2System",
    "DTESystem",
    "CheatSheetFusion",
    "MemoryPersistence",
    "ConversationExtractor",
]
