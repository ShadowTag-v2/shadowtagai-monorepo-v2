# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prefetch Pipeline - Minimize LLM Usage

Exports:
- PrefetchPipeline: Main pipeline for query optimization
- SemanticCache: Embedding-based semantic cache
- WebPrefetcher: Web context gathering
- PrefetchChain: LangChain integration wrapper
- create_prefetch_pipeline: Factory function
"""

from .pipeline import (
    CacheEntry,
    CacheHitType,
    PrefetchChain,
    PrefetchPipeline,
    PrefetchResult,
    PrefetchStrategy,
    SemanticCache,
    WebPrefetcher,
    create_prefetch_pipeline,
)

__all__ = [
    "CacheEntry",
    "CacheHitType",
    "PrefetchChain",
    "PrefetchPipeline",
    "PrefetchResult",
    "PrefetchStrategy",
    "SemanticCache",
    "WebPrefetcher",
    "create_prefetch_pipeline",
]
