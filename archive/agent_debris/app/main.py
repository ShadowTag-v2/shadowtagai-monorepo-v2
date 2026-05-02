"""
Main FastAPI application for ShadowTagAI Governance Service
"""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, status

from app.api.v1 import api_router


# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info(
        "Starting SHADOWTAGAI Kernel Chain service",
        extra={
            "service_name": settings.service_name,
            "gemini_model": settings.gemini_model,
        },
    )

    # Validate kernel chain with JR Engine
    jr_engine = JREngine()
    validation = jr_engine.validate_kernel_chain(
        [
            "ATP519ScanKernel",
            "JudgeSixClassifyKernel",
            "AuditCompressKernel",
        ]
    )

    if not validation.passed:
        logger.error("Kernel chain failed JR Engine validation", extra={"validation": validation.dict()})
        raise RuntimeError("Kernel chain validation failed")

    logger.info(
        "Kernel chain validated by JR Engine",
        extra={
            "approved_kernels": validation.approved_kernels,
            "total_kernels": validation.total_kernels,
        },
    )

    yield

    logger.info("Shutting down SHADOWTAGAI Kernel Chain service")


# Create FastAPI app
app = FastAPI(
    title="SHADOWTAGAI Kernel Chain",
    description="Sequential specialized prompts for ATP 5-19 decision governance",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount Prometheus metrics endpoint
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Initialize kernel chain (singleton pattern)
def create_kernel_chain() -> ChainExecutor:
    """Create and configure the kernel chain."""
    kernels = [
        ATP519ScanKernel(),
        JudgeSixClassifyKernel(),
        AuditCompressKernel(),
    ]
    chain = KernelChain(kernels)
    return ChainExecutor(chain)


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": "0.1.0",
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict[str, Any]:
    """Readiness check endpoint"""
    # TODO: Add actual readiness checks (DB, Redis, etc.)
    return {
        "service": "SHADOWTAGAI Kernel Chain",
        "description": "Sequential specialized prompts for efficient decision-making",
        "architecture": "3-kernel chain (ATP scan → Judge classify → Audit compress)",
        "endpoints": {
            "POST /decision": "Execute decision pipeline",
            "GET /health": "Health check",
            "GET /metrics": "Prometheus metrics (if enabled)",
            "GET /validation": "JR Engine validation report",
        },
    }


@app.post("/decision", response_model=DecisionResult)
async def execute_decision(context: DecisionContext):
    """
    Execute the full kernel chain decision pipeline.

    This endpoint orchestrates:
    1. ATP 5-19 violation scanning (Gemini Flash)
    2. Binary go/no-go classification (PyTorch local)
    3. Audit trail compression (zstd)

    Returns structured decision with full metrics and audit trail.
    """
    start_time = time.perf_counter()

    try:
        # Execute kernel chain
        result = await chain_executor.execute_decision(context)

        # Record metrics
        if metrics_collector:
            metrics_collector.record_decision(
                latency_ms=result.total_latency_ms,
                cost_usd=result.total_cost_usd,
                confidence=result.confidence,
                risk_tier=result.risk_tier,
                violations_count=len(result.violations),
                success=True,
            )

            # Record per-kernel metrics
            for kernel_name, metrics in result.kernel_metrics.items():
                metrics_collector.record_kernel_execution(
                    kernel_name=kernel_name,
                    latency_ms=metrics["latency_ms"],
                    success=True,
                    tokens_input=metrics.get("token_count_input"),
                    tokens_output=metrics.get("token_count_output"),
                )

            # Record compression ratio
            metrics_collector.record_compression(result.audit_trail.compression_ratio)

        logger.info(
            "Decision executed successfully",
            extra={
                "trace_id": result.trace_id,
                "decision": result.decision,
                "confidence": result.confidence,
                "risk_tier": result.risk_tier.name,
                "total_latency_ms": result.total_latency_ms,
                "total_cost_usd": result.total_cost_usd,
            },
        )

        return result

    except KernelChainError as e:
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Record failure metrics
        if metrics_collector:
            metrics_collector.decisions_total.labels(status="failure").inc()

        logger.error(
            "Decision execution failed",
            extra={
                "trace_id": context.trace_id,
                "error": str(e),
                "latency_ms": latency_ms,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Kernel chain execution failed",
                "message": str(e),
                "trace_id": context.trace_id,
                "latency_ms": latency_ms,
            },
        )

    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000

        logger.error(
            "Unexpected error",
            extra={
                "trace_id": context.trace_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "latency_ms": latency_ms,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "trace_id": context.trace_id,
            },
        )


@app.get("/validation")
async def get_validation_report():
    """
    Get JR Engine validation report for the kernel chain.

    Returns validation status for each kernel against:
    - Purpose: Does this kernel advance revenue/security?
    - Reasons: Can I defend this kernel's necessity?
    - Brakes: What's p99 failure mode? Cost blowup scenario?
    """
    jr_engine = JREngine()
    validation = jr_engine.validate_kernel_chain(
        [
            "ATP519ScanKernel",
            "JudgeSixClassifyKernel",
            "AuditCompressKernel",
        ]
    )

    return validation.dict()


# Global tracer instance
governance_tracer = GovernanceTracer()

# Mock tier check - replace with actual tier logic
PAID_TIER_KEYS = {"founder_key_001", "pro_tier_001"}


@app.get("/api/v1/audit/{decision_id}")
async def get_audit_trail(decision_id: str, x_api_key: str = Header(...)):
    """
    Get signed URL for decision audit trail.

    Returns:
        - 200: Signed URL (15 min expiry)
        - 402: Payment Required (free tier)
        - 404: Decision not found
    """
    # Check tier
    if x_api_key not in PAID_TIER_KEYS:
        raise HTTPException(
            status_code=402,
            detail={"error": "Payment Required", "message": "Audit trail access requires Pro tier", "upgrade_url": "https://shadowtag.ai/pricing"},
        )

    # Get or generate signed URL
    url = governance_tracer.get_or_generate_trace(decision_id)

    if not url:
        raise HTTPException(status_code=404, detail={"error": "Not Found", "message": f"No audit trail found for decision: {decision_id}"})

    logger.info("Audit trail accessed", extra={"decision_id": decision_id, "api_key": x_api_key[:8] + "..."})

    return {"decision_id": decision_id, "audit_trail": {"access_type": "temporary_signed_url", "expires_in": "15 minutes", "url": url}}


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "description": "ShadowTagAI Governance Service - Full compliance & infrastructure management",
        "persona_iq": settings.persona_iq_override,
        "governance": {
            "eu_ai_act": settings.eu_ai_act_enabled,
            "dsa_vlop": settings.dsa_vlop_mode,
            "nist_rmf": settings.nist_rmf_enabled,
            "iso_42001": settings.iso_42001_enabled,
        },
        "docs": "/docs",
        "health": "/health",
    }


# Include API routers
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
