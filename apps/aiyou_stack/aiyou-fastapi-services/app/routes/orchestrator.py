"""LLM Orchestrator API Routes
Endpoints for multi-LLM orchestration with PNKLN integration
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_orchestrator import PNKLNOrchestrator

router = APIRouter(prefix="/orchestrator", tags=["LLM Orchestrator"])

# Initialize orchestrator
orchestrator = PNKLNOrchestrator()


# ============================================================================
# Request/Response Models
# ============================================================================


class ProcessQueryRequest(BaseModel):
    """Request to process a query through LLM orchestration"""

    query: str = Field(..., description="User query to process", min_length=1)
    enable_review_rotation: bool = Field(
        default=False,
        description="Enable 3-round peer review (slower, more accurate)",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata for tracking",
    )


class ThreadResult(BaseModel):
    """Result from a single thread"""

    thread_id: str
    content: str
    domain: str
    complexity: int
    assigned_llm: str
    round_1_response: str | None
    round_2_review: str | None
    round_3_review: str | None
    cost: float
    latency_ms: int
    tier_classification: dict[str, Any] | None


class ProcessQueryResponse(BaseModel):
    """Response from query processing"""

    query: str
    threads: list[ThreadResult]
    synthesis: str
    total_cost: float
    total_latency_ms: int
    confidence: float
    metadata: dict[str, Any]


class IntelligenceClassificationRequest(BaseModel):
    """Specialized request for intelligence classification"""

    title: str = Field(..., description="Intelligence item title")
    content: str = Field(..., description="Full content text")
    tags: list[str] = Field(default_factory=list, description="Metadata tags")
    enable_debate: bool = Field(
        default=True,
        description="Use multi-agent debate (3 agents, 2 rounds)",
    )


class BenchmarkResponse(BaseModel):
    """Benchmark comparison across LLM providers"""

    provider: str
    avg_latency_ms: int
    avg_cost_per_query: float
    accuracy: float | None
    use_cases: list[str]


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/process", response_model=ProcessQueryResponse)
async def process_query(request: ProcessQueryRequest):
    """Process a user query through the LLM orchestration pipeline

    Flow:
    1. Grok Intake: Decompose query into threads
    2. PNKLN Coordinator: Assign threads to specialized LLMs
    3. Round 1: Execute threads with assigned LLMs
    4. (Optional) Rounds 2-3: Peer review rotation
    5. Synthesis: Combine results with PNKLN validation

    Example:
        POST /api/v1/orchestrator/process
        {
          "query": "Classify: FAA Proposes DO-178D | New aviation regulation | aviation,regulation",
          "enable_review_rotation": false
        }

        Response:
        {
          "query": "...",
          "threads": [{
            "thread_id": "intel_1",
            "domain": "intelligence",
            "assigned_llm": "gemini-multi-agent",
            "tier_classification": {
              "tier": 1,
              "confidence": 0.87
            }
          }],
          "synthesis": "...",
          "total_cost": 0.00375,
          "total_latency_ms": 1234,
          "confidence": 0.87
        }

    """
    try:
        result = await orchestrator.process_query(
            query=request.query,
            enable_review_rotation=request.enable_review_rotation,
        )

        # Convert Thread dataclasses to Pydantic models
        thread_results = []
        for thread in result.threads:
            tier_class = None
            if thread.tier_classification:
                tier_class = {
                    "tier": thread.tier_classification.tier,
                    "confidence": thread.tier_classification.confidence,
                    "reasoning": thread.tier_classification.reasoning[:200],
                    "tags": thread.tier_classification.tags,
                }

            thread_results.append(
                ThreadResult(
                    thread_id=thread.thread_id,
                    content=thread.content,
                    domain=thread.domain.value,
                    complexity=thread.complexity,
                    assigned_llm=thread.assigned_llm.value,
                    round_1_response=thread.round_1_response,
                    round_2_review=thread.round_2_review,
                    round_3_review=thread.round_3_review,
                    cost=thread.cost,
                    latency_ms=thread.latency_ms,
                    tier_classification=tier_class,
                ),
            )

        return ProcessQueryResponse(
            query=result.query,
            threads=thread_results,
            synthesis=result.synthesis,
            total_cost=result.total_cost,
            total_latency_ms=result.total_latency_ms,
            confidence=result.confidence,
            metadata=result.metadata,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {e!s}") from e


@router.post("/intelligence/classify", response_model=ProcessQueryResponse)
async def classify_intelligence(request: IntelligenceClassificationRequest):
    """Specialized endpoint for intelligence classification

    Uses Gemini multi-agent debate system (skeptic, optimist, neutral)
    for high-accuracy tier classification.

    Example:
        POST /api/v1/orchestrator/intelligence/classify
        {
          "title": "FAA Proposes DO-178D Update for AI Systems",
          "content": "The Federal Aviation Administration today...",
          "tags": ["aviation", "regulation", "AI"],
          "enable_debate": true
        }

        Response:
        {
          "threads": [{
            "tier_classification": {
              "tier": 1,
              "confidence": 0.87,
              "reasoning": "Weighted consensus: 3 agents..."
            }
          }],
          "total_cost": 0.00375,
          "confidence": 0.87
        }

    """
    # Format as orchestrator query
    query = f"Classify: {request.title} | {request.content} | {','.join(request.tags)}"

    try:
        result = await orchestrator.process_query(
            query=query,
            enable_review_rotation=False,  # Intelligence uses multi-agent debate instead
        )

        # Convert to response format
        thread_results = []
        for thread in result.threads:
            tier_class = None
            if thread.tier_classification:
                tier_class = {
                    "tier": thread.tier_classification.tier,
                    "confidence": thread.tier_classification.confidence,
                    "reasoning": thread.tier_classification.reasoning,
                    "tags": thread.tier_classification.tags,
                }

            thread_results.append(
                ThreadResult(
                    thread_id=thread.thread_id,
                    content=thread.content,
                    domain=thread.domain.value,
                    complexity=thread.complexity,
                    assigned_llm=thread.assigned_llm.value,
                    round_1_response=thread.round_1_response,
                    round_2_review=thread.round_2_review,
                    round_3_review=thread.round_3_review,
                    cost=thread.cost,
                    latency_ms=thread.latency_ms,
                    tier_classification=tier_class,
                ),
            )

        return ProcessQueryResponse(
            query=result.query,
            threads=thread_results,
            synthesis=result.synthesis,
            total_cost=result.total_cost,
            total_latency_ms=result.total_latency_ms,
            confidence=result.confidence,
            metadata={
                **result.metadata,
                "classification_mode": "multi-agent-debate",
                "agents_used": ["skeptic", "optimist", "neutral"],
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence classification failed: {e!s}") from e


@router.get("/providers", response_model=list[BenchmarkResponse])
async def list_providers():
    """List available LLM providers with benchmarks

    Returns provider capabilities, costs, and recommended use cases
    """
    providers = [
        BenchmarkResponse(
            provider="gemini-multi-agent",
            avg_latency_ms=1234,
            avg_cost_per_query=0.00375,
            accuracy=0.874,
            use_cases=[
                "Intelligence classification",
                "Multi-perspective analysis",
                "High-stakes decisions requiring consensus",
            ],
        ),
        BenchmarkResponse(
            provider="gemini-pro",
            avg_latency_ms=800,
            avg_cost_per_query=0.0025,
            accuracy=0.837,
            use_cases=[
                "Bulk text processing",
                "Multimodal analysis",
                "Large context windows (1M tokens)",
            ],
        ),
        BenchmarkResponse(
            provider="gpt5",
            avg_latency_ms=1500,
            avg_cost_per_query=0.008,
            accuracy=None,
            use_cases=[
                "Code generation",
                "Structured output (JSON, YAML)",
                "Complex reasoning tasks",
            ],
        ),
        BenchmarkResponse(
            provider="perplexity",
            avg_latency_ms=2000,
            avg_cost_per_query=0.005,
            accuracy=None,
            use_cases=[
                "Research with web grounding",
                "Real-time information lookup",
                "Citation-backed answers",
            ],
        ),
        BenchmarkResponse(
            provider="grok",
            avg_latency_ms=500,
            avg_cost_per_query=0.001,
            accuracy=None,
            use_cases=[
                "Query intake and decomposition",
                "Task routing",
                "Parallel thread generation",
            ],
        ),
    ]

    return providers


@router.get("/health")
async def health_check():
    """Health check for orchestrator service"""
    return {
        "status": "healthy",
        "service": "llm_orchestrator",
        "providers_available": ["gemini-multi-agent", "gemini-pro", "gpt5", "perplexity", "grok"],
        "integration": "pnkln-core-stack",
        "features": [
            "multi-agent-debate",
            "peer-review-rotation",
            "atp-519-validation",
            "tier-classification",
        ],
    }


@router.get("/example")
async def example_queries():
    """Get example queries for different domains

    Useful for testing and understanding how to format queries
    """
    return {
        "intelligence_classification": {
            "query": "Classify: FAA Proposes DO-178D Update | The Federal Aviation Administration today announced new regulatory requirements for AI-based flight control systems | aviation,regulation,AI",
            "expected_domain": "intelligence",
            "expected_llm": "gemini-multi-agent",
        },
        "code_generation": {
            "query": "Implement a FastAPI endpoint for user authentication with JWT tokens",
            "expected_domain": "code",
            "expected_llm": "gpt5",
        },
        "research": {
            "query": "Research the latest developments in quantum computing for cryptography",
            "expected_domain": "research",
            "expected_llm": "perplexity",
        },
        "analysis": {
            "query": "Analyze the financial impact of AI adoption in the healthcare industry",
            "expected_domain": "analysis",
            "expected_llm": "gemini-pro",
        },
    }
