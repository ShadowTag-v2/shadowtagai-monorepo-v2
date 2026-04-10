"""
Prefetch Pipeline - Minimize LLM Usage

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
    "PrefetchPipeline",
    "SemanticCache",
    "WebPrefetcher",
    "PrefetchChain",
    "PrefetchResult",
    "PrefetchStrategy",
    "CacheHitType",
    "CacheEntry",
    "create_prefetch_pipeline",
]
