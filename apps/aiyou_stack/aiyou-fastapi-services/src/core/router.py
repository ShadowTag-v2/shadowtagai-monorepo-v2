# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SELF-ROUTE Controller Implementation
Intelligent routing between RAG and Long-Context modes

Key Features:
- RAG-and-Route: Try RAG first, route to LC if unanswerable
- Cost optimization: 38.6% token usage vs LC-only
- Performance: 93% of LC-only baseline
- Task-aware routing with complexity classification
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum

from ..prompts.templates import PromptTemplates, QueryClassifier, TaskType
from .retriever import RetrievedChunk, VertexRAGRetriever

logger = logging.getLogger(__name__)


class RoutingMethod(Enum):
    """Routing decision outcome"""

    RAG = "RAG"
    LONG_CONTEXT = "LONG_CONTEXT"
    FORCED_LC = "FORCED_LC"  # Bypassed RAG due to complexity


@dataclass
class GenerationConfig:
    """Configuration for Gemini model generation"""

    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 512
    stop_sequences: list[str] | None = None


@dataclass
class RouteResponse:
    """Response from SELF-ROUTE controller"""

    answer: str
    method: RoutingMethod
    tokens_used: int
    confidence: str
    task_type: TaskType
    retrieved_chunks: list[RetrievedChunk] | None = None
    metadata: dict | None = None


class SelfRouteController:
    """Main controller implementing SELF-ROUTE logic

    Architecture:
    1. Query classification (complexity, task type)
    2. RAG-and-Route (try RAG first)
    3. Intelligent routing to LC if needed
    4. Cost tracking and optimization
    """

    def __init__(
        self,
        gemini_model: str = "gemini-3.1-flash-lite-preview",
        retriever: VertexRAGRetriever | None = None,
        project_id: str | None = None,
        location: str = "us-central1",
        cost_threshold: float = 0.5,
        default_k: int = 5,
    ):
        """Initialize SELF-ROUTE controller

        Args:
            gemini_model: Gemini model name (pro or flash)
            retriever: VertexRAGRetriever instance (or create default)
            project_id: GCP project ID
            location: GCP region
            cost_threshold: Max acceptable cost ratio vs LC
            default_k: Default number of chunks to retrieve

        """
        self.gemini_model = gemini_model
        self.project_id = project_id
        self.location = location
        self.cost_threshold = cost_threshold
        self.default_k = default_k

        # Initialize retriever
        self.retriever = retriever or VertexRAGRetriever(project_id=project_id, location=location)

        # Lazy load Gemini model
        self._model = None

        # Statistics tracking
        self.stats = {
            "total_queries": 0,
            "rag_routes": 0,
            "lc_routes": 0,
            "forced_lc": 0,
            "total_tokens": 0,
            "avg_latency": 0.0,
        }

        logger.info(
            f"Initialized SelfRouteController: model={gemini_model}, "
            f"k={default_k}, cost_threshold={cost_threshold}",
        )

    @property
    def model(self):
        """Lazy load Gemini model"""
        if self._model is None:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel

                if self.project_id:
                    vertexai.init(project=self.project_id, location=self.location)

                self._model = GenerativeModel(self.gemini_model)
                logger.info(f"Loaded Gemini model: {self.gemini_model}")

            except ImportError:
                logger.error("vertexai package not installed")
                raise
            except Exception as e:
                logger.error(f"Failed to load Gemini model: {e}")
                raise

        return self._model

    def _get_generation_config(self, mode: str = "rag") -> dict:
        """Get generation configuration for RAG or LC mode

        Args:
            mode: "rag" or "lc"

        Returns:
            Generation config dict

        """
        if mode == "rag":
            return {
                "temperature": 0.1,  # Low for factual retrieval
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 512,  # Short answers expected
            }
        # LC mode
        return {
            "temperature": 0.2,  # Slightly higher for reasoning
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,  # Longer reasoning chains
        }

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approximate: 1.3 tokens per word)

        Args:
            text: Input text

        Returns:
            Estimated token count

        """
        return int(len(text.split()) * 1.3)

    def _generate(self, prompt: str, mode: str = "rag") -> str:
        """Generate response using Gemini

        Args:
            prompt: Input prompt
            mode: "rag" or "lc"

        Returns:
            Generated text

        """
        try:
            from vertexai.generative_models import GenerationConfig

            config = self._get_generation_config(mode)
            gen_config = GenerationConfig(**config)

            response = self.model.generate_content(prompt, generation_config=gen_config)

            return response.text

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def classify_query(
        self,
        query: str,
        domain_hint: str | None = None,
    ) -> tuple[TaskType, str, bool]:
        """Classify query for routing strategy

        Args:
            query: User query
            domain_hint: Optional domain hint

        Returns:
            Tuple of (task_type, complexity, force_lc)

        """
        task_type = QueryClassifier.detect_task_type(query, domain_hint)
        complexity = QueryClassifier.classify_complexity(query)
        force_lc = QueryClassifier.should_force_lc(query)

        logger.debug(
            f"Query classification: task={task_type}, complexity={complexity}, force_lc={force_lc}",
        )

        return task_type, complexity, force_lc

    def route(
        self,
        query: str,
        context: str,
        document_id: str = "default",
        k: int | None = None,
        task_type: TaskType | None = None,
        domain_hint: str | None = None,
    ) -> RouteResponse:
        """Main routing logic: RAG-and-Route implementation

        Args:
            query: User query
            context: Full document text
            document_id: Document identifier
            k: Number of chunks to retrieve (default: self.default_k)
            task_type: Optional explicit task type
            domain_hint: Optional domain hint

        Returns:
            RouteResponse with answer and metadata

        """
        start_time = time.time()

        # Use default k if not specified
        k = k or self.default_k

        # Classify query
        if task_type is None:
            task_type, complexity, force_lc = self.classify_query(query, domain_hint)
        else:
            complexity = QueryClassifier.classify_complexity(query)
            force_lc = QueryClassifier.should_force_lc(query)

        # Check if we should skip RAG entirely
        if force_lc:
            logger.info(f"Forcing LC due to query complexity: {complexity}")
            return self._route_to_lc(
                query,
                context,
                task_type,
                method=RoutingMethod.FORCED_LC,
                start_time=start_time,
            )

        # STEP 1: RAG-and-Route
        logger.info(f"Starting RAG-and-Route with k={k}, task_type={task_type}")

        # Retrieve chunks
        try:
            retrieved_chunks = self.retriever.retrieve(
                query=query,
                document_text=context,
                document_id=document_id,
                k=k,
            )

            chunk_texts = [chunk.text for chunk in retrieved_chunks]
            chunk_indices = [chunk.chunk_index for chunk in retrieved_chunks]

        except Exception as e:
            logger.error(f"Retrieval failed: {e}, falling back to LC")
            return self._route_to_lc(
                query,
                context,
                task_type,
                method=RoutingMethod.LONG_CONTEXT,
                start_time=start_time,
                error=str(e),
            )

        # Generate RAG prompt
        rag_prompt = PromptTemplates.get_rag_prompt(
            task_type=task_type,
            query=query,
            chunks=chunk_texts,
            indices=chunk_indices,
        )

        # Try RAG
        try:
            rag_response = self._generate(rag_prompt, mode="rag")

            # STEP 2: Routing decision
            if "unanswerable" in rag_response.lower():
                logger.info("RAG deemed query unanswerable, routing to LC")
                return self._route_to_lc(
                    query,
                    context,
                    task_type,
                    method=RoutingMethod.LONG_CONTEXT,
                    start_time=start_time,
                    retrieved_chunks=retrieved_chunks,
                )
            # RAG succeeded
            tokens_used = self._estimate_tokens(rag_prompt) + self._estimate_tokens(
                rag_response,
            )

            latency = time.time() - start_time

            # Update stats
            self._update_stats(RoutingMethod.RAG, tokens_used, latency)

            logger.info(f"RAG success: {tokens_used} tokens, {latency:.2f}s")

            return RouteResponse(
                answer=rag_response,
                method=RoutingMethod.RAG,
                tokens_used=tokens_used,
                confidence="MEDIUM",
                task_type=task_type,
                retrieved_chunks=retrieved_chunks,
                metadata={
                    "k": k,
                    "complexity": complexity,
                    "latency": latency,
                    "avg_chunk_score": sum(c.score for c in retrieved_chunks)
                    / len(retrieved_chunks),
                },
            )

        except Exception as e:
            logger.error(f"RAG generation failed: {e}, falling back to LC")
            return self._route_to_lc(
                query,
                context,
                task_type,
                method=RoutingMethod.LONG_CONTEXT,
                start_time=start_time,
                error=str(e),
            )

    def _route_to_lc(
        self,
        query: str,
        context: str,
        task_type: TaskType,
        method: RoutingMethod,
        start_time: float,
        retrieved_chunks: list[RetrievedChunk] | None = None,
        error: str | None = None,
    ) -> RouteResponse:
        """Route to Long-Context mode

        Args:
            query: User query
            context: Full document
            task_type: Task type
            method: Routing method (LONG_CONTEXT or FORCED_LC)
            start_time: Query start time
            retrieved_chunks: Optional retrieved chunks (for metadata)
            error: Optional error message

        Returns:
            RouteResponse

        """
        # Generate LC prompt
        lc_prompt = PromptTemplates.get_lc_prompt(
            task_type=task_type,
            query=query,
            full_context=context,
        )

        try:
            lc_response = self._generate(lc_prompt, mode="lc")

            tokens_used = self._estimate_tokens(lc_prompt) + self._estimate_tokens(lc_response)

            latency = time.time() - start_time

            # Update stats
            self._update_stats(method, tokens_used, latency)

            logger.info(f"LC route: {tokens_used} tokens, {latency:.2f}s")

            return RouteResponse(
                answer=lc_response,
                method=method,
                tokens_used=tokens_used,
                confidence="HIGH",
                task_type=task_type,
                retrieved_chunks=retrieved_chunks,
                metadata={
                    "latency": latency,
                    "context_length": len(context.split()),
                    "error": error,
                },
            )

        except Exception as e:
            logger.error(f"LC generation failed: {e}")
            raise

    def _update_stats(self, method: RoutingMethod, tokens: int, latency: float):
        """Update routing statistics"""
        self.stats["total_queries"] += 1
        self.stats["total_tokens"] += tokens

        if method == RoutingMethod.RAG:
            self.stats["rag_routes"] += 1
        elif method == RoutingMethod.LONG_CONTEXT:
            self.stats["lc_routes"] += 1
        elif method == RoutingMethod.FORCED_LC:
            self.stats["forced_lc"] += 1

        # Update average latency
        total = self.stats["total_queries"]
        self.stats["avg_latency"] = (self.stats["avg_latency"] * (total - 1) + latency) / total

    def get_stats(self) -> dict:
        """Get routing statistics

        Returns:
            Dictionary with performance metrics

        """
        total = self.stats["total_queries"]

        if total == 0:
            return {**self.stats, "rag_percentage": 0.0, "lc_percentage": 0.0}

        return {
            **self.stats,
            "rag_percentage": (self.stats["rag_routes"] / total) * 100,
            "lc_percentage": (self.stats["lc_routes"] / total) * 100,
            "forced_lc_percentage": (self.stats["forced_lc"] / total) * 100,
            "avg_tokens_per_query": self.stats["total_tokens"] / total,
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_queries": 0,
            "rag_routes": 0,
            "lc_routes": 0,
            "forced_lc": 0,
            "total_tokens": 0,
            "avg_latency": 0.0,
        }
        logger.info("Statistics reset")
