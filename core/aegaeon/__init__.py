# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/aegaeon — Gemini Aegaeon Protocol
Context Cache Slab + 7-instance Swarm Router achieving ~84% token cost reduction.

Mapping: Aegaeon VRAM Slab  →  Gemini Context Cache
         Multi-Model Pool    →  gemini-3.1-flash-lite-preview Swarm (7 instances)
         Prefill disaggreg.  →  Cached content (75% input-token discount)
         Decode disaggreg.   →  Fast Path (1-5) / Heavy Lift (6-7) tier routing
"""

from .context_cache import AegaeonContextCache
from .swarm_router import SwarmRouter, SwarmTask, SwarmTier

__all__ = ["AegaeonContextCache", "SwarmRouter", "SwarmTask", "SwarmTier"]
