# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Production API Server for Consensus Orchestrator
FastAPI-based REST API with authentication, rate limiting, and monitoring
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Import orchestrator
from atomic_consensus_orchestrator import AtomicConsensusOrchestrator
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Consensus Orchestrator API",
    description="Multi-LLM consensus system with Ultrathink architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (simple in-memory)
request_counts = {}
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "100"))  # requests per minute
RATE_WINDOW = 60  # seconds

# API key validation
API_KEYS = os.environ.get("API_KEYS", "").split(",")
if not API_KEYS or API_KEYS == [""]:
    logger.warning("No API_KEYS set - running in open mode (not recommended for production)")
    API_KEYS = None


# === Request/Response Models ===


class QueryRequest(BaseModel):
    """Request model for consensus queries"""

    message: str = Field(..., description="The query to process")
    max_threads: int = Field(6, ge=1, le=20, description="Maximum threads for decomposition")
    tags: list[str] | None = Field(None, description="Tags for archiving")
    auto_archive: bool = Field(True, description="Auto-archive the result")

    class Config:
        schema_extra = {
            "example": {
                "message": "Design a scalable FastAPI microservice with authentication",
                "max_threads": 6,
                "tags": ["architecture", "fastapi"],
                "auto_archive": True,
            },
        }


class QueryResponse(BaseModel):
    """Response model for consensus queries"""

    query_id: str | None = None
    final_output: str
    threads: list[dict[str, Any]]
    execution_summary: dict[str, Any]
    cost_breakdown: dict[str, Any] | None = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str
    memory_loaded: bool
    models_available: dict[str, bool]


class MetricsResponse(BaseModel):
    """Metrics response"""

    total_queries: int
    total_cost: float
    avg_response_time: float
    uptime_seconds: float


# === Middleware ===


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s",
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# === Authentication ===


async def verify_api_key(x_api_key: str | None = Header(None)) -> str:
    """Verify API key from header"""
    if API_KEYS is None:
        # Open mode (development only)
        return "open-mode"

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Provide X-API-Key header.")

    if x_api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(status_code=403, detail="Invalid API key")

    return x_api_key


# === Rate Limiting ===


async def check_rate_limit(request: Request, api_key: str = Depends(verify_api_key)):
    """Check rate limiting"""
    client_id = api_key
    current_time = time.time()

    # Clean old entries
    if client_id in request_counts:
        request_counts[client_id] = [
            t for t in request_counts[client_id] if current_time - t < RATE_WINDOW
        ]
    else:
        request_counts[client_id] = []

    # Check limit
    if len(request_counts[client_id]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per minute.",
        )

    # Add current request
    request_counts[client_id].append(current_time)

    return True


# === Orchestrator Singleton ===

orchestrator = None
app_start_time = time.time()
query_metrics = {"total_queries": 0, "total_cost": 0.0, "total_time": 0.0}


def get_orchestrator() -> AtomicConsensusOrchestrator:
    """Get or create orchestrator singleton"""
    global orchestrator
    if orchestrator is None:
        logger.info("Initializing consensus orchestrator...")
        orchestrator = AtomicConsensusOrchestrator()

        # Load memory if available
        memory_path = os.environ.get("MEMORY_PATH", "/memory/memory.md")
        if Path(memory_path).exists():
            logger.info(f"Memory loaded from: {memory_path}")
        else:
            logger.warning(f"No memory file found at: {memory_path}")

    return orchestrator


# === Health & Monitoring Endpoints ===


@app.get("/", response_model=dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "Consensus Orchestrator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for K8s probes"""
    orch = get_orchestrator()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        memory_loaded=Path(os.environ.get("MEMORY_PATH", "/memory/memory.md")).exists(),
        models_available={
            "gemini": orch.gemini_model is not None,
            "claude": orch.anthropic_key is not None,
            "gpt": orch.openai_key is not None,
            "perplexity": orch.perplexity_key is not None,
            "grok": orch.xai_key is not None,
        },
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics(api_key: str = Depends(verify_api_key)):
    """Metrics endpoint for monitoring"""
    uptime = time.time() - app_start_time

    avg_time = (
        query_metrics["total_time"] / query_metrics["total_queries"]
        if query_metrics["total_queries"] > 0
        else 0.0
    )

    return MetricsResponse(
        total_queries=query_metrics["total_queries"],
        total_cost=query_metrics["total_cost"],
        avg_response_time=avg_time,
        uptime_seconds=uptime,
    )


@app.get("/ready")
async def readiness_check():
    """Readiness probe for K8s"""
    orch = get_orchestrator()

    # Check at least one model is available
    models_ready = any(
        [
            orch.gemini_model is not None,
            orch.anthropic_key is not None,
            orch.openai_key is not None,
        ],
    )

    if not models_ready:
        raise HTTPException(status_code=503, detail="No models available")

    return {"status": "ready"}


# === Main Query Endpoint ===


@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key),
    rate_limit: bool = Depends(check_rate_limit),
):
    """Process a consensus query with multi-LLM orchestration.

    This endpoint:
    1. Pre-processes query with Grok intake
    2. Decomposes into atomic threads with Claude
    3. Executes threads with model allocation (Gemini 40%, Claude 35%, GPT 15%, Perplexity 5%, Grok 5%)
    4. Performs circular peer review (2 rounds)
    5. Stitches results with Claude
    6. Archives and tracks costs

    Returns comprehensive consensus result with cost breakdown.
    """
    start_time = time.time()

    try:
        logger.info(f"Processing query: {request.message[:100]}...")

        # Get orchestrator
        orch = get_orchestrator()

        # Process query
        result = await orch.process_message(
            user_message=request.message,
            max_threads=request.max_threads,
            auto_archive=request.auto_archive,
            tags=request.tags,
        )

        # Update metrics
        process_time = time.time() - start_time
        query_metrics["total_queries"] += 1
        query_metrics["total_time"] += process_time

        if "cost_breakdown" in result:
            query_metrics["total_cost"] += result["cost_breakdown"].get("total_cost", 0.0)

        logger.info(f"Query completed in {process_time:.2f}s")

        return QueryResponse(
            query_id=result.get("transcript_id"),
            final_output=result["final_output"],
            threads=result["threads"],
            execution_summary=result["execution_summary"],
            cost_breakdown=result.get("cost_breakdown"),
            timestamp=result.get("timestamp", datetime.utcnow().isoformat()),
        )

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {e!s}") from e


# === Error Handlers ===


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# === Startup/Shutdown Events ===


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 60)
    logger.info("CONSENSUS ORCHESTRATOR API STARTING")
    logger.info("=" * 60)

    # Initialize orchestrator
    orch = get_orchestrator()

    # Log configuration
    logger.info(f"Environment: {os.environ.get('ENV', 'production')}")
    logger.info(f"Rate limit: {RATE_LIMIT} requests/minute")
    logger.info(f"API keys: {'Enabled' if API_KEYS else 'Disabled (OPEN MODE)'}")

    # Log model availability
    logger.info("Models available:")
    logger.info(f"  - Gemini: {orch.gemini_model is not None}")
    logger.info(f"  - Claude: {orch.anthropic_key is not None}")
    logger.info(f"  - GPT: {orch.openai_key is not None}")
    logger.info(f"  - Perplexity: {orch.perplexity_key is not None}")
    logger.info(f"  - Grok: {orch.xai_key is not None}")

    logger.info("=" * 60)
    logger.info("API READY - Listening on port 8000")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down consensus orchestrator API...")
    logger.info(f"Total queries processed: {query_metrics['total_queries']}")
    logger.info(f"Total cost: ${query_metrics['total_cost']:.2f}")


# === Run Server ===

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")

    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
