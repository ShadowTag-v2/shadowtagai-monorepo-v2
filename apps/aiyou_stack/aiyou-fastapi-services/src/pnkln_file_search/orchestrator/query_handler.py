"""Query Handler with File Search Integration
Orchestrates parallel execution of file search and Judge 6 enforcement
"""

import asyncio
import time

import structlog
from vertexai.generative_models import GenerativeModel
from vertexai.preview import rag

from pnkln_file_search.config.mock_mode import MockGenerativeModel, is_mock_mode
from pnkln_file_search.config.settings import get_settings
from pnkln_file_search.corpus.manager import CorpusManager
from pnkln_file_search.monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


class PolicyContext:
    """Container for policy context retrieved from file search"""

    def __init__(
        self,
        citations: list[dict],
        context_text: str,
        retrieval_time_ms: float,
        source_documents: list[str],
    ):
        self.citations = citations
        self.context_text = context_text
        self.retrieval_time_ms = retrieval_time_ms
        self.source_documents = source_documents


class QueryHandler:
    """Handles query processing with integrated file search and Judge 6

    Architecture:
    1. Parallel execution: File search + Judge 6 Layer 1 (Gemini)
    2. Merge contexts for enhanced enforcement
    3. Sequential execution: Judge 6 Layers 2+3 (PyTorch + Rules)
    """

    def __init__(self, corpus_manager: CorpusManager | None = None):
        """Initialize query handler"""
        self.settings = get_settings()
        self.corpus_manager = corpus_manager or CorpusManager()
        self.metrics = MetricsCollector()
        self._model = None

    async def initialize(self) -> None:
        """Initialize handler and dependencies"""
        await self.corpus_manager.initialize()

        # Initialize Gemini model for file search (or mock)
        if is_mock_mode():
            self._model = MockGenerativeModel(self.settings.vertex_ai_model)
            logger.info("query_handler_initialized", model="mock", mock_mode=True)
        else:
            self._model = GenerativeModel(self.settings.vertex_ai_model)
            logger.info("query_handler_initialized", model=self.settings.vertex_ai_model)

    async def get_policy_context(
        self,
        corpus_name: str,
        query: str,
        top_k: int | None = None,
    ) -> PolicyContext:
        """Query File Search API with retrieval config

        Args:
            corpus_name: Corpus to query
            query: User query
            top_k: Number of top results (overrides default)

        Returns:
            PolicyContext with citations and source attribution

        """
        start_time = time.time()
        top_k = top_k or self.settings.file_search_top_k

        try:
            # Create retrieval tool
            retrieval_tool = rag.Tool(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[corpus_name],
                    ),
                    similarity_top_k=top_k,
                ),
            )

            # Generate content with file search
            response = self._model.generate_content(
                query,
                tools=[retrieval_tool],
            )

            # Extract grounding metadata
            grounding_metadata = response.candidates[0].grounding_metadata
            chunks = grounding_metadata.grounding_chunks if grounding_metadata else []

            # Parse citations
            citations = []
            source_docs = set()

            for chunk in chunks:
                if hasattr(chunk, "web") and chunk.web:
                    # Handle web sources
                    citations.append(
                        {
                            "type": "web",
                            "uri": chunk.web.uri,
                            "title": chunk.web.title or "",
                        },
                    )
                    source_docs.add(chunk.web.uri)
                elif hasattr(chunk, "retrieved_context"):
                    # Handle retrieved context from corpus
                    citations.append(
                        {
                            "type": "corpus",
                            "text": chunk.retrieved_context.text,
                            "uri": getattr(chunk.retrieved_context, "uri", ""),
                        },
                    )
                    if hasattr(chunk.retrieved_context, "uri"):
                        source_docs.add(chunk.retrieved_context.uri)

            retrieval_time_ms = (time.time() - start_time) * 1000

            # Record metrics
            self.metrics.record_file_search_latency(retrieval_time_ms)

            context = PolicyContext(
                citations=citations,
                context_text=response.text,
                retrieval_time_ms=retrieval_time_ms,
                source_documents=list(source_docs),
            )

            logger.info(
                "policy_context_retrieved",
                corpus=corpus_name,
                citations_count=len(citations),
                retrieval_time_ms=retrieval_time_ms,
                top_k=top_k,
            )

            return context

        except Exception as e:
            retrieval_time_ms = (time.time() - start_time) * 1000
            self.metrics.record_file_search_error()

            logger.error(
                "policy_context_retrieval_failed",
                corpus=corpus_name,
                error=str(e),
                retrieval_time_ms=retrieval_time_ms,
            )
            raise

    async def judge_gemini_layer1(self, query: str) -> dict:
        """Execute Judge 6 Layer 1 (Gemini fine-tuned model)

        This is a placeholder for your actual Judge 6 Layer 1 implementation.
        Replace with real ATP 5-19 compliance checks.

        Args:
            query: User query to assess

        Returns:
            Assessment with risk signals

        """
        start_time = time.time()

        # TODO: Replace with actual Judge 6 Layer 1 implementation
        # This should call your fine-tuned Gemini model for ATP 5-19 checks
        try:
            # Placeholder assessment
            assessment = {
                "atp_5_19_flags": [],  # Risk signals from ATP 5-19 framework
                "risk_level": "low",  # low, medium, high
                "layer1_latency_ms": 0,
            }

            layer1_time_ms = (time.time() - start_time) * 1000
            assessment["layer1_latency_ms"] = layer1_time_ms

            self.metrics.record_judge_layer1_latency(layer1_time_ms)

            logger.info(
                "judge_layer1_completed",
                risk_level=assessment["risk_level"],
                latency_ms=layer1_time_ms,
            )

            return assessment

        except Exception as e:
            logger.error("judge_layer1_failed", error=str(e))
            raise

    async def judge_hybrid_enforce(self, enhanced_context: dict) -> dict:
        """Execute Judge 6 Layers 2+3 sequentially (deterministic)

        Args:
            enhanced_context: Merged context from file search and Layer 1

        Returns:
            Final enforcement decision

        """
        start_time = time.time()

        # TODO: Replace with actual Judge 6 Layers 2+3 implementation
        # Layer 2: PyTorch model (~30ms)
        # Layer 3: Rules engine (~20ms)

        try:
            enforcement_decision = {
                "allowed": True,
                "confidence": 0.95,
                "policy_violations": [],
                "required_actions": [],
                "layer2_latency_ms": 0,
                "layer3_latency_ms": 0,
                "total_enforcement_latency_ms": 0,
            }

            total_time_ms = (time.time() - start_time) * 1000
            enforcement_decision["total_enforcement_latency_ms"] = total_time_ms

            self.metrics.record_enforcement_latency(total_time_ms)

            logger.info(
                "enforcement_completed",
                allowed=enforcement_decision["allowed"],
                latency_ms=total_time_ms,
            )

            return enforcement_decision

        except Exception as e:
            logger.error("enforcement_failed", error=str(e))
            raise

    async def process_query_with_context(
        self,
        user_query: str,
        vertical: str,
        corpus_name: str | None = None,
    ) -> dict:
        """Process query with file search and Judge 6 enforcement

        Step 1: Parallel execution - File search + Judge 6 Layer 1
        Step 2: Merge contexts
        Step 3: Sequential execution - Judge 6 Layers 2+3

        Args:
            user_query: User's query
            vertical: Vertical name (e.g., "defense", "healthcare")
            corpus_name: Optional corpus name (auto-detected if not provided)

        Returns:
            Complete response with enforcement decision and context

        """
        overall_start = time.time()

        try:
            # Auto-detect corpus if not provided
            if not corpus_name:
                corpus_name = self.corpus_manager.get_corpus_name(vertical)
                if not corpus_name:
                    raise ValueError(f"No corpus found for vertical: {vertical}")

            # Step 1: Parallel execution
            logger.info(
                "query_processing_started",
                vertical=vertical,
                corpus=corpus_name,
            )

            policy_context, judge_layer1 = await asyncio.gather(
                self.get_policy_context(corpus_name, user_query),
                self.judge_gemini_layer1(user_query),
            )

            # Step 2: Merge contexts
            enhanced_context = {
                "query": user_query,
                "vertical": vertical,
                "policy_refs": policy_context.citations,
                "policy_context": policy_context.context_text,
                "source_documents": policy_context.source_documents,
                "risk_signals": judge_layer1["atp_5_19_flags"],
                "layer1_risk_level": judge_layer1["risk_level"],
            }

            # Step 3: Judge 6 Layers 2+3 (sequential, deterministic)
            enforcement_decision = await self.judge_hybrid_enforce(enhanced_context)

            # Compile final response
            total_time_ms = (time.time() - overall_start) * 1000

            response = {
                "query": user_query,
                "vertical": vertical,
                "enforcement": enforcement_decision,
                "policy_context": {
                    "citations": policy_context.citations,
                    "source_documents": policy_context.source_documents,
                    "retrieval_time_ms": policy_context.retrieval_time_ms,
                },
                "timing": {
                    "file_search_ms": policy_context.retrieval_time_ms,
                    "judge_layer1_ms": judge_layer1["layer1_latency_ms"],
                    "enforcement_ms": enforcement_decision["total_enforcement_latency_ms"],
                    "total_ms": total_time_ms,
                },
                "metadata": {
                    "corpus": corpus_name,
                    "model": self.settings.vertex_ai_model,
                },
            }

            logger.info(
                "query_processing_completed",
                vertical=vertical,
                allowed=enforcement_decision["allowed"],
                total_time_ms=total_time_ms,
            )

            return response

        except Exception as e:
            total_time_ms = (time.time() - overall_start) * 1000
            logger.error(
                "query_processing_failed",
                vertical=vertical,
                error=str(e),
                total_time_ms=total_time_ms,
            )
            raise
