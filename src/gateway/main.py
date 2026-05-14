# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Governance Gateway - FastAPI Application

The elegant interface to agent-based governance.
Every endpoint purposeful. Every response complete.

"Simplicity is the ultimate sophistication." - Steve Jobs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from .models import GovernanceRequest, GovernanceResponse
from .router import GovernanceRouter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.

    Startup: Initialize clients, warm caches
    Shutdown: Graceful cleanup
    """
    logger.info("🚀 Governance Gateway starting...")

    # TODO: Initialize OPA client
    # TODO: Initialize Agent client
    # TODO: Initialize observability (AgentOps, Cloud Trace)
    # TODO: Load policies into cache

    logger.info("✅ Governance Gateway ready")

    yield

    logger.info("🛑 Governance Gateway shutting down...")
    # TODO: Cleanup resources


# Create FastAPI application
app = FastAPI(
    title="AiYou Governance Gateway",
    description="Agent-based governance with hybrid OPA/Agent routing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize router
# TODO: Pass actual OPA and Agent clients
router = GovernanceRouter(opa_client=None, agent_client=None)


@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    """
    Add timing headers to all responses.

    Observability starts with measurement.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time-Ms"] = str(int(process_time))
    return response


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AiYou Governance Gateway",
        "status": "operational",
        "version": "0.1.0",
        "architecture": "hybrid_opa_agent",
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check.

    Returns system health including dependencies.
    """
    # TODO: Check OPA connectivity
    # TODO: Check Agent Engine connectivity
    # TODO: Check Vector DB connectivity

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {
            "opa": "not_configured",  # TODO: Implement
            "agent_engine": "not_configured",  # TODO: Implement
            "vector_db": "not_configured",  # TODO: Implement
        },
    }


@app.post(
    "/governance/decide",
    response_model=GovernanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Make governance decision",
    description="""
    Primary governance decision endpoint.

    Routes request through risk assessment to optimal decision path:
    - High risk → OPA fast path (<10ms deterministic)
    - Medium/Low risk → Agent slow path (2-5s contextual)

    Returns complete decision with reasoning and audit trail.
    """,
)
async def make_decision(request: GovernanceRequest) -> GovernanceResponse:
    """
    Make a governance decision.

    This is the heart of the system. Every request routed optimally.
    """
    try:
        logger.info(f"Governance request: {request.request_id} | Action: {request.action} | User: {request.user_id}")

        routing_decision, governance_response = await router.route_request(request)

        logger.info(
            f"Decision complete: {request.request_id} | "
            f"Outcome: {governance_response.outcome} | "
            f"Path: {routing_decision.path} | "
            f"Latency: {governance_response.latency_ms}ms"
        )

        return governance_response

    except Exception as e:
        logger.error(f"Decision error: {request.request_id} | Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Governance decision failed: {str(e)}",
        )


@app.post(
    "/governance/decide/explain",
    response_model=dict,
    summary="Get routing explanation without executing",
    description="""
    Dry-run endpoint: shows routing decision without executing.

    Useful for:
    - Testing risk classification
    - Understanding routing logic
    - Debugging policy issues
    """,
)
async def explain_routing(request: GovernanceRequest) -> dict:
    """
    Explain how request would be routed (dry run).

    Transparency builds trust.
    """
    try:
        risk_assessment = router.classifier.assess_risk(request)
        path = router.classifier.determine_path(risk_assessment)
        estimated_latency = router.classifier.estimate_latency(path)

        return {
            "request_id": request.request_id,
            "risk_assessment": {
                "probability": risk_assessment.probability,
                "severity": risk_assessment.severity,
                "risk_level": risk_assessment.risk_level,
                "hazards": risk_assessment.hazards,
                "controls": risk_assessment.controls,
            },
            "routing": {
                "path": path,
                "reason": router._explain_routing(risk_assessment, path),
                "estimated_latency_ms": estimated_latency,
            },
        }

    except Exception as e:
        logger.error(f"Routing explanation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing explanation failed: {str(e)}",
        )


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus-compatible metrics endpoint.

    TODO: Implement actual metrics collection.
    """
    # TODO: Return Prometheus metrics
    # - Request count by path (fast/slow)
    # - Decision latency histogram
    # - Decision outcome distribution
    # - Agent confidence distribution
    # - Error rates
    return {
        "status": "not_implemented",
        "message": "Metrics collection pending implementation",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.

    Fail gracefully. Log completely. Return safely.
    """
    logger.error(
        f"Unhandled exception: {exc} | Path: {request.url.path} | Method: {request.method}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "Governance gateway encountered an unexpected error",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development only
        log_level="info",
    )
