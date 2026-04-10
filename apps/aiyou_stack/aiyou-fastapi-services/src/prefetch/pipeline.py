"""
Prefetch Pipeline - Minimize LLM Usage Through Smart Caching & Web Investigation

Strategy:
1. SEMANTIC CACHE: Use embeddings to find similar past queries (skip LLM if hit)
2. WEB PREFETCH: Gather context from web before calling LLM (reduce tokens)
3. PIPELINE BATCH: Aggregate similar queries, call LLM once
4. FASTGPT RETRIEVAL: Use local embeddings for instant answers when possible

Target: 60-80% reduction in LLM API calls through intelligent prefetching.
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class CacheHitType(StrEnum):
    """Type of cache hit"""

    EXACT = "exact"  # Exact query match
    SEMANTIC = "semantic"  # Similar query match (>0.85 similarity)
    PARTIAL = "partial"  # Partial match - needs refinement
    MISS = "miss"  # No cache hit


class PrefetchStrategy(StrEnum):
    """Prefetch strategy for context gathering"""

    WEB_SEARCH = "web_search"  # Search web for context
    RAG_LOCAL = "rag_local"  # Search local documents
    MEMORY_LOOKUP = "memory_lookup"  # Check sovereign memory
    HYBRID = "hybrid"  # All of the above


@dataclass
class CacheEntry:
    """Cached query-response pair with metadata"""

    query_hash: str
    query_text: str
    response: str
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    ttl_hours: int = 24
    hit_count: int = 0
    confidence: float = 1.0
    source: str = "llm"  # llm, web, rag, memory

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(hours=self.ttl_hours)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_hash": self.query_hash,
            "query_text": self.query_text,
            "response": self.response,
            "created_at": self.created_at.isoformat(),
            "hit_count": self.hit_count,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class PrefetchResult:
    """Result from prefetch pipeline"""

    query: str
    cache_hit: CacheHitType
    response: str | None = None
    confidence: float = 0.0
    source: str = "none"
    prefetch_context: str | None = None
    tokens_saved: int = 0
    latency_ms: float = 0.0

    @property
    def needs_llm(self) -> bool:
        """Whether LLM call is still needed"""
        return self.cache_hit in [CacheHitType.MISS, CacheHitType.PARTIAL]


class SemanticCache:
    """
    Semantic cache using embeddings for similarity matching.

    Uses cosine similarity to find similar past queries.
    Threshold: 0.85 for semantic match, 0.95 for near-exact.
    """

    def __init__(
        self,
        max_entries: int = 10000,
        similarity_threshold: float = 0.85,
        embedding_model: str = "models/embedding-001",
    ):
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.embedding_model = embedding_model

        # In-memory cache (production would use Redis + vector DB)
        self._cache: dict[str, CacheEntry] = {}
        self._embeddings: dict[str, list[float]] = {}

        # Stats
        self.stats = {
            "exact_hits": 0,
            "semantic_hits": 0,
            "partial_hits": 0,
            "misses": 0,
            "tokens_saved": 0,
        }

        # Try to import embedding provider
        self._embedder = None
        try:
            import google.generativeai as genai

            self._embedder = genai
        except ImportError:
            logger.warning("google-generativeai not available, semantic matching disabled")

    def _hash_query(self, query: str) -> str:
        """Generate hash for exact matching"""
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    async def _get_embedding(self, text: str) -> list[float] | None:
        """Get embedding for text using Gemini"""
        if not self._embedder:
            return None

        try:
            result = self._embedder.embed_content(
                model=self.embedding_model, content=text, task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            return None

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b or len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    async def lookup(self, query: str) -> tuple[CacheHitType, CacheEntry | None, float]:
        """
        Look up query in cache.

        Returns:
            Tuple of (hit_type, cache_entry, similarity_score)
        """
        query_hash = self._hash_query(query)

        # 1. Check exact match
        if query_hash in self._cache:
            entry = self._cache[query_hash]
            if not entry.is_expired():
                entry.hit_count += 1
                self.stats["exact_hits"] += 1
                return CacheHitType.EXACT, entry, 1.0

        # 2. Check semantic similarity
        query_embedding = await self._get_embedding(query)
        if query_embedding:
            best_match = None
            best_score = 0.0

            for hash_key, entry in self._cache.items():
                if entry.is_expired():
                    continue

                if hash_key in self._embeddings:
                    similarity = self._cosine_similarity(
                        query_embedding, self._embeddings[hash_key]
                    )

                    if similarity > best_score:
                        best_score = similarity
                        best_match = entry

            if best_match and best_score >= 0.95:
                best_match.hit_count += 1
                self.stats["exact_hits"] += 1
                return CacheHitType.EXACT, best_match, best_score

            if best_match and best_score >= self.similarity_threshold:
                best_match.hit_count += 1
                self.stats["semantic_hits"] += 1
                return CacheHitType.SEMANTIC, best_match, best_score

            if best_match and best_score >= 0.70:
                self.stats["partial_hits"] += 1
                return CacheHitType.PARTIAL, best_match, best_score

        self.stats["misses"] += 1
        return CacheHitType.MISS, None, 0.0

    async def store(
        self,
        query: str,
        response: str,
        source: str = "llm",
        confidence: float = 1.0,
        ttl_hours: int = 24,
    ) -> str:
        """Store query-response pair in cache"""
        query_hash = self._hash_query(query)

        # Get embedding for semantic matching
        embedding = await self._get_embedding(query)

        entry = CacheEntry(
            query_hash=query_hash,
            query_text=query,
            response=response,
            embedding=embedding,
            confidence=confidence,
            source=source,
            ttl_hours=ttl_hours,
        )

        self._cache[query_hash] = entry
        if embedding:
            self._embeddings[query_hash] = embedding

        # Evict old entries if at capacity
        if len(self._cache) > self.max_entries:
            self._evict_lru()

        return query_hash

    def _evict_lru(self):
        """Evict least recently used entries"""
        # Sort by hit_count, remove bottom 10%
        sorted_entries = sorted(
            self._cache.items(), key=lambda x: (x[1].hit_count, x[1].created_at)
        )

        to_remove = len(sorted_entries) // 10
        for hash_key, _ in sorted_entries[:to_remove]:
            del self._cache[hash_key]
            self._embeddings.pop(hash_key, None)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_lookups = sum(
            [
                self.stats["exact_hits"],
                self.stats["semantic_hits"],
                self.stats["partial_hits"],
                self.stats["misses"],
            ]
        )

        hit_rate = 0.0
        if total_lookups > 0:
            hits = self.stats["exact_hits"] + self.stats["semantic_hits"]
            hit_rate = hits / total_lookups

        return {
            **self.stats,
            "total_lookups": total_lookups,
            "hit_rate": round(hit_rate, 3),
            "cache_size": len(self._cache),
        }


class WebPrefetcher:
    """
    Prefetch web context before calling LLM.

    Gathers relevant context from web to reduce prompt tokens
    and provide more accurate answers without full LLM reasoning.
    """

    def __init__(self, max_results: int = 5, timeout_seconds: int = 10):
        self.max_results = max_results
        self.timeout_seconds = timeout_seconds

        # Try to import httpx for async requests
        try:
            import httpx

            self._http_available = True
        except ImportError:
            self._http_available = False
            logger.warning("httpx not available, web prefetch disabled")

    async def prefetch(self, query: str) -> str | None:
        """
        Prefetch web context for query.

        Returns:
            Summarized context string or None
        """
        if not self._http_available:
            return None

        try:
            import httpx

            # Use DuckDuckGo instant answers API (no auth required)
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1,
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    # Extract relevant context
                    context_parts = []

                    # Abstract (main answer)
                    if data.get("Abstract"):
                        context_parts.append(f"Summary: {data['Abstract']}")

                    # Related topics
                    for topic in data.get("RelatedTopics", [])[:3]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            context_parts.append(f"- {topic['Text'][:200]}")

                    if context_parts:
                        return "\n".join(context_parts)

        except Exception as e:
            logger.warning(f"Web prefetch failed: {e}")

        return None

    async def search_and_summarize(self, query: str) -> dict[str, Any]:
        """
        Search web and return structured results.

        Returns dict with:
        - context: Summarized context string
        - sources: List of source URLs
        - confidence: How confident we are in the context
        """
        context = await self.prefetch(query)

        return {
            "context": context,
            "sources": [],  # Would populate from actual search
            "confidence": 0.7 if context else 0.0,
            "tokens_estimated": len(context.split()) if context else 0,
        }


class PrefetchPipeline:
    """
    Main prefetch pipeline combining all strategies.

    Flow:
    1. Check semantic cache (instant, free)
    2. Check memory/RAG (fast, cheap)
    3. Prefetch web context (medium speed, free)
    4. Only call LLM if needed (slow, expensive)

    Target: 60-80% reduction in LLM calls.
    """

    def __init__(
        self,
        cache: SemanticCache | None = None,
        web_prefetcher: WebPrefetcher | None = None,
        memory_client: Any | None = None,  # SovereignMemory instance
        default_strategy: PrefetchStrategy = PrefetchStrategy.HYBRID,
    ):
        self.cache = cache or SemanticCache()
        self.web = web_prefetcher or WebPrefetcher()
        self.memory = memory_client
        self.default_strategy = default_strategy

        # Metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "web_prefetch_used": 0,
            "memory_hits": 0,
            "llm_calls_needed": 0,
            "tokens_saved": 0,
        }

    async def process(
        self,
        query: str,
        strategy: PrefetchStrategy | None = None,
        min_confidence: float = 0.80,
    ) -> PrefetchResult:
        """
        Process query through prefetch pipeline.

        Args:
            query: User query
            strategy: Prefetch strategy (default: HYBRID)
            min_confidence: Minimum confidence to skip LLM

        Returns:
            PrefetchResult with cache info, context, and whether LLM needed
        """
        start_time = time.perf_counter()
        strategy = strategy or self.default_strategy

        self.metrics["total_queries"] += 1

        result = PrefetchResult(query=query, cache_hit=CacheHitType.MISS)
        prefetch_contexts = []

        # Step 1: Check semantic cache
        cache_hit, cache_entry, similarity = await self.cache.lookup(query)

        if cache_hit == CacheHitType.EXACT:
            self.metrics["cache_hits"] += 1
            result.cache_hit = CacheHitType.EXACT
            result.response = cache_entry.response
            result.confidence = cache_entry.confidence
            result.source = f"cache:{cache_entry.source}"
            result.tokens_saved = len(cache_entry.response.split()) * 2  # Estimate
            result.latency_ms = (time.perf_counter() - start_time) * 1000
            return result

        if cache_hit == CacheHitType.SEMANTIC and similarity >= min_confidence:
            self.metrics["cache_hits"] += 1
            result.cache_hit = CacheHitType.SEMANTIC
            result.response = cache_entry.response
            result.confidence = similarity
            result.source = f"semantic_cache:{cache_entry.source}"
            result.tokens_saved = len(cache_entry.response.split()) * 2
            result.latency_ms = (time.perf_counter() - start_time) * 1000
            return result

        # Partial hit - use as context
        if cache_hit == CacheHitType.PARTIAL and cache_entry:
            prefetch_contexts.append(f"Similar past response: {cache_entry.response[:500]}")

        # Step 2: Check memory (if available)
        if self.memory and strategy in [PrefetchStrategy.MEMORY_LOOKUP, PrefetchStrategy.HYBRID]:
            try:
                similar = await self._check_memory(query)
                if similar:
                    self.metrics["memory_hits"] += 1
                    prefetch_contexts.append(f"Memory context: {similar}")
            except Exception as e:
                logger.warning(f"Memory lookup failed: {e}")

        # Step 3: Web prefetch
        if strategy in [PrefetchStrategy.WEB_SEARCH, PrefetchStrategy.HYBRID]:
            web_result = await self.web.search_and_summarize(query)
            if web_result["context"]:
                self.metrics["web_prefetch_used"] += 1
                prefetch_contexts.append(f"Web context: {web_result['context']}")

                # If web has high-quality answer and confidence is high enough
                if web_result["confidence"] >= min_confidence:
                    result.cache_hit = CacheHitType.PARTIAL
                    result.response = web_result["context"]
                    result.confidence = web_result["confidence"]
                    result.source = "web"

        # Combine prefetch contexts
        if prefetch_contexts:
            result.prefetch_context = "\n\n---\n\n".join(prefetch_contexts)
            result.tokens_saved = len(
                result.prefetch_context.split()
            )  # Context reduces LLM reasoning

        # Determine if LLM still needed
        if result.response and result.confidence >= min_confidence:
            result.cache_hit = (
                CacheHitType.SEMANTIC if cache_hit != CacheHitType.MISS else CacheHitType.PARTIAL
            )
        else:
            self.metrics["llm_calls_needed"] += 1
            result.cache_hit = cache_hit

        result.latency_ms = (time.perf_counter() - start_time) * 1000
        self.metrics["tokens_saved"] += result.tokens_saved

        return result

    async def _check_memory(self, query: str) -> str | None:
        """Check sovereign memory for relevant context"""
        if not self.memory:
            return None

        try:
            # Use async method if available
            if hasattr(self.memory, "get_similar_decisions"):
                results = await self.memory.get_similar_decisions(query, limit=3)
                if results:
                    return " | ".join([r.get("content", "")[:200] for r in results])
        except Exception:
            pass

        return None

    async def process_batch(
        self,
        queries: list[str],
        strategy: PrefetchStrategy | None = None,
    ) -> list[PrefetchResult]:
        """
        Process batch of queries, deduplicating similar ones.
        """
        # Deduplicate queries
        unique_queries = list(set(queries))

        # Process in parallel
        results = await asyncio.gather(*[self.process(q, strategy) for q in unique_queries])

        # Map back to original order
        result_map = {r.query: r for r in results}
        return [
            result_map.get(q, PrefetchResult(query=q, cache_hit=CacheHitType.MISS)) for q in queries
        ]

    async def store_response(
        self,
        query: str,
        response: str,
        source: str = "llm",
        confidence: float = 1.0,
    ):
        """Store response in cache for future queries"""
        await self.cache.store(query, response, source, confidence)

    def get_metrics(self) -> dict[str, Any]:
        """Get pipeline metrics"""
        total = self.metrics["total_queries"]

        cache_rate = 0.0
        skip_rate = 0.0

        if total > 0:
            cache_rate = self.metrics["cache_hits"] / total
            skip_rate = 1 - (self.metrics["llm_calls_needed"] / total)

        return {
            **self.metrics,
            "cache_hit_rate": round(cache_rate, 3),
            "llm_skip_rate": round(skip_rate, 3),
            "cache_stats": self.cache.get_stats(),
        }


# =============================================================================
# LANGCHAIN INTEGRATION
# =============================================================================


class PrefetchChain:
    """
    LangChain-style chain with prefetch pipeline.

    Wraps any LLM and adds prefetch layer to minimize calls.
    """

    def __init__(
        self,
        llm: Any,  # LangChain LLM instance
        pipeline: PrefetchPipeline | None = None,
        min_confidence: float = 0.85,
    ):
        self.llm = llm
        self.pipeline = pipeline or PrefetchPipeline()
        self.min_confidence = min_confidence

    async def __call__(self, query: str) -> str:
        """Process query with prefetch optimization"""
        # Try prefetch first
        prefetch = await self.pipeline.process(query, min_confidence=self.min_confidence)

        if not prefetch.needs_llm:
            # Cache hit - return without LLM call
            return prefetch.response

        # Need LLM - but use prefetch context to reduce tokens
        prompt = query
        if prefetch.prefetch_context:
            prompt = f"""Context from prior knowledge:
{prefetch.prefetch_context}

User query: {query}

Using the context above, provide a concise answer:"""

        # Call LLM
        response = await self._call_llm(prompt)

        # Store in cache for future
        await self.pipeline.store_response(query, response, source="llm")

        return response

    async def _call_llm(self, prompt: str) -> str:
        """Call underlying LLM"""
        # Handle different LLM interfaces
        if hasattr(self.llm, "ainvoke"):
            result = await self.llm.ainvoke(prompt)
            return result.content if hasattr(result, "content") else str(result)
        elif hasattr(self.llm, "invoke"):
            result = self.llm.invoke(prompt)
            return result.content if hasattr(result, "content") else str(result)
        elif callable(self.llm):
            return self.llm(prompt)
        else:
            raise ValueError("Unknown LLM interface")


# =============================================================================
# FACTORY & CLI
# =============================================================================


def create_prefetch_pipeline(
    use_cache: bool = True,
    use_web: bool = True,
    use_memory: bool = True,
    memory_client: Any = None,
) -> PrefetchPipeline:
    """
    Factory to create configured prefetch pipeline.

    Args:
        use_cache: Enable semantic cache
        use_web: Enable web prefetch
        use_memory: Enable memory lookup
        memory_client: Optional SovereignMemory instance

    Returns:
        Configured PrefetchPipeline
    """
    cache = SemanticCache() if use_cache else None
    web = WebPrefetcher() if use_web else None

    strategy = PrefetchStrategy.HYBRID
    if not use_web:
        strategy = PrefetchStrategy.MEMORY_LOOKUP
    if not use_memory:
        strategy = PrefetchStrategy.WEB_SEARCH

    return PrefetchPipeline(
        cache=cache,
        web_prefetcher=web,
        memory_client=memory_client if use_memory else None,
        default_strategy=strategy,
    )


if __name__ == "__main__":

    async def demo():
        print("=" * 60)
        print("PREFETCH PIPELINE - LLM Usage Minimization Demo")
        print("=" * 60)

        # Create pipeline
        pipeline = create_prefetch_pipeline()

        # Test queries
        queries = [
            "What is the capital of France?",
            "What is the capital of France?",  # Exact duplicate
            "What's France's capital city?",  # Semantic duplicate
            "Explain quantum computing basics",
            "How does quantum computing work?",  # Semantic similar
        ]

        print("\n📥 Processing queries...\n")

        for query in queries:
            result = await pipeline.process(query)

            print(f"Query: {query[:50]}...")
            print(f"  Cache: {result.cache_hit.value}")
            print(f"  Needs LLM: {result.needs_llm}")
            print(f"  Latency: {result.latency_ms:.2f}ms")

            if result.response:
                print(f"  Response: {result.response[:100]}...")

            # Store mock response for testing
            if result.cache_hit == CacheHitType.MISS:
                await pipeline.store_response(query, f"Mock response for: {query}")

            print()

        # Show metrics
        print("\n📊 Pipeline Metrics:")
        metrics = pipeline.get_metrics()
        print(f"  Total Queries: {metrics['total_queries']}")
        print(f"  Cache Hits: {metrics['cache_hits']}")
        print(f"  LLM Calls Needed: {metrics['llm_calls_needed']}")
        print(f"  LLM Skip Rate: {metrics['llm_skip_rate']:.0%}")
        print(f"  Tokens Saved: ~{metrics['tokens_saved']}")

    asyncio.run(demo())
