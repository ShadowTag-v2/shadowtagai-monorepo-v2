# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/sovereign_mlx — Sovereign MLX Protocol
Mapping Aegaeon's VRAM pooling to Apple Silicon Unified Memory.

M1 Max Advantage: CPU / GPU (Metal) / ANE share the same physical RAM pool.
No discrete VRAM boundary = no vLLM CUDA required.

Components:
  kv_cache_slab   — precomputes .beads KV-cache via llama.cpp/MLX (one-time)
  ane_bridge      — token-level async dispatcher; loads model ONCE, routes N requests
"""

from .ane_bridge import ANEBridge
from .kv_cache_slab import KVCacheSlab

__all__ = ["KVCacheSlab", "ANEBridge"]
