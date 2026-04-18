"""FastAPI Application for Vertex AI RAG vs Long-Context Service

Endpoints:
- POST /query: Process query with SELF-ROUTE
- GET /stats: Get routing statistics
- GET /verticals: List available verticals
- GET /health: Health check
"""

import logging
import os
import sys
import traceback

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..config.verticals import (
    VerticalType,
    get_cost_tier_summary,
    get_vertical_by_name,
    get_vertical_config,
)
from ..core.router import SelfRouteController
from ..prompts.templates import TaskType
from ..routers.agents import agents_router
from .eventarc import router as eventarc_router
from .intercept import router as intercept_router
from .zt_identity import verify_zero_trust_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vertex AI RAG Service",
    description="SELF-ROUTE implementation for intelligent RAG vs Long-Context routing",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire the Cor.Firebase Edge Interceptor (Shield 1)
app.include_router(intercept_router)

# Wire the Cor.Firebase Leviathan Wake (Eventarc)
app.include_router(eventarc_router)

# Wire the Zero-Trust Agents router (Temporal / Swarm execution)
app.include_router(agents_router)

# Global controller instance (initialized on startup)
controller: SelfRouteController | None = None

# ============================================================================
# CINEMATIC TELEMETRY & AUTO-REPAIR
# ============================================================================

# Ensure root scripts can be resolved reliably
_root_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
)
if _root_dir not in sys.path:
    sys.path.append(_root_dir)

try:
    from scripts.cinematic_studio import CinematicTelemetry

    cinematic_telemetry = CinematicTelemetry()
    logger.info("Cinematic Telemetry active. 500-Drop Auto-Repair is online.")
except ImportError as e:
    logger.warning(f"CinematicTelemetry import failed: {e}. Autonomous repair disengaged.")
    cinematic_telemetry = None


@app.exception_handler(Exception)
async def cinematic_global_exception_handler(request: Request, exc: Exception):
    """Catch-all 500 exception handler that intercepts fatal runtime errors
    and pipes them straight to the Cinematic Telemetry queue to potentially trigger
    the Temporal auto-repair swarm pipeline.
    """
    stack_trace = traceback.format_exc()
    if cinematic_telemetry:
        cinematic_telemetry.log_http_response(500, request.url.path, stack_trace)

    logger.error(f"Captured HTTP 500: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class QueryRequest(BaseModel):
    """Request model for query endpoint"""

    query: str = Field(..., description="User query")
    context: str = Field(..., description="Full document text to search")
    document_id: str = Field(default="default", description="Document identifier")
    vertical: str | None = Field(
        None,
        description="Industry vertical (e.g., 'healthcare_compliance')",
    )
    k: int | None = Field(
        None,
        description="Number of chunks to retrieve (overrides vertical default)",
    )
    task_type: str | None = Field(None, description="Task type (legal_compliance, multi_hop, etc.)")
    model_override: str | None = Field(None, description="Override Gemini model (pro or flash)")

    class Config:
        schema_extra = {
            "example": {
                "query": "What are the HIPAA requirements for patient data storage?",
                "context": "HIPAA regulations specify that... [full document text]",
                "document_id": "hipaa_regulations_2024",
                "vertical": "healthcare_compliance",
            },
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint"""

    answer: str
    method: str  # RAG, LONG_CONTEXT, or FORCED_LC
    tokens_used: int
    confidence: str  # LOW, MEDIUM, HIGH
    task_type: str
    vertical: str | None
    metadata: dict

    class Config:
        schema_extra = {
            "example": {
                "answer": "According to chunk 3, HIPAA requires...",
                "method": "RAG",
                "tokens_used": 6500,
                "confidence": "MEDIUM",
                "task_type": "legal_compliance",
                "vertical": "healthcare_compliance",
                "metadata": {"k": 10, "latency": 2.3, "avg_chunk_score": 0.87},
            },
        }


class StatsResponse(BaseModel):
    """Response model for stats endpoint"""

    total_queries: int
    rag_routes: int
    lc_routes: int
    forced_lc: int
    rag_percentage: float
    lc_percentage: float
    forced_lc_percentage: float
    avg_tokens_per_query: float
    avg_latency: float


class VerticalInfo(BaseModel):
    """Information about a vertical"""

    name: str
    value: str
    description: str
    k: int
    model: str
    temperature: float
    citation_required: bool


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize controller on startup"""
    global controller

    logger.info("Initializing SELF-ROUTE controller...")

    # TODO: Load these from environment variables
    project_id = None  # Set to your GCP project ID
    location = "us-central1"

    try:
        controller = SelfRouteController(
            gemini_model="gemini-1.5-pro-001",  # Default to Pro
            project_id=project_id,
            location=location,
            default_k=5,
        )
        logger.info("Controller initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize controller: {e}")
        # Don't fail startup - allow health check to report status


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down service...")


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vertex AI RAG Service",
        "version": "1.0.0",
        "description": "SELF-ROUTE implementation for intelligent RAG vs Long-Context routing",
        "endpoints": {
            "query": "/query (POST)",
            "stats": "/stats (GET)",
            "verticals": "/verticals (GET)",
            "health": "/health (GET)",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if controller is None:
        return {"status": "unhealthy", "error": "Controller not initialized"}

    return {
        "status": "healthy",
        "model": controller.gemini_model,
        "retriever": "VertexRAGRetriever",
        "verticals_available": len(VerticalType),
    }


@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_zero_trust_token)])
async def process_query(request: QueryRequest):
    """Process query with SELF-ROUTE logic

    This endpoint:
    1. Applies vertical-specific configuration
    2. Routes query through RAG-and-Route logic
    3. Returns answer with routing metadata
    """
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not initialized")

    try:
        # Get vertical config if specified
        vertical_config = None
        vertical_type = None

        if request.vertical:
            try:
                vertical_type = get_vertical_by_name(request.vertical)
                vertical_config = get_vertical_config(vertical_type)
                logger.info(f"Using vertical config: {vertical_config.name}")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Determine k value
        k = request.k
        if k is None and vertical_config:
            k = vertical_config.k
        elif k is None:
            k = controller.default_k

        # Determine task type
        task_type = None
        if request.task_type:
            try:
                task_type = TaskType(request.task_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid task_type: {request.task_type}",
                )

        # Override model if specified
        original_model = controller.gemini_model
        if request.model_override:
            controller.gemini_model = request.model_override
            controller._model = None  # Force reload
        elif vertical_config:
            controller.gemini_model = vertical_config.model
            controller._model = None

        # Process query
        logger.info(
            f"Processing query: '{request.query[:50]}...' (vertical={request.vertical}, k={k})",
        )

        response = controller.route(
            query=request.query,
            context=request.context,
            document_id=request.document_id,
            k=k,
            task_type=task_type,
            domain_hint=request.vertical,
        )

        # Restore original model
        if request.model_override or vertical_config:
            controller.gemini_model = original_model
            controller._model = None

        # Format response
        return QueryResponse(
            answer=response.answer,
            method=response.method.value,
            tokens_used=response.tokens_used,
            confidence=response.confidence,
            task_type=response.task_type.value,
            vertical=request.vertical,
            metadata=response.metadata or {},
        )

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get routing statistics"""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not initialized")

    stats = controller.get_stats()

    return StatsResponse(**stats)


@app.post("/stats/reset")
async def reset_stats():
    """Reset statistics"""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not initialized")

    controller.reset_stats()

    return {"message": "Statistics reset successfully"}


@app.get("/verticals")
async def get_verticals():
    """List all available verticals with descriptions"""
    verticals_list = []

    for vertical_type in VerticalType:
        config = get_vertical_config(vertical_type)
        verticals_list.append(
            VerticalInfo(
                name=config.name,
                value=vertical_type.value,
                description=config.description,
                k=config.k,
                model=config.model,
                temperature=config.temperature,
                citation_required=config.citation_required,
            ),
        )

    return {
        "total": len(verticals_list),
        "verticals": verticals_list,
        "cost_tiers": get_cost_tier_summary(),
    }


@app.get("/verticals/{vertical_name}")
async def get_vertical_details(vertical_name: str):
    """Get detailed configuration for a specific vertical"""
    try:
        vertical_type = get_vertical_by_name(vertical_name)
        config = get_vertical_config(vertical_type)

        return {
            "vertical": vertical_type.value,
            "name": config.name,
            "description": config.description,
            "configuration": {
                "k": config.k,
                "chunk_size": config.chunk_size,
                "overlap": config.overlap,
                "temperature": config.temperature,
                "force_lc_threshold": config.force_lc_threshold,
                "enable_reranking": config.enable_reranking,
                "citation_required": config.citation_required,
                "model": config.model,
                "max_output_tokens": config.max_output_tokens,
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.post("/cache/clear")
async def clear_cache(document_id: str | None = None):
    """Clear retriever cache"""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not initialized")

    controller.retriever.clear_cache(document_id)

    return {"message": f"Cache cleared for {document_id or 'all documents'}"}


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not initialized")

    stats = controller.retriever.get_cache_stats()

    return stats


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
