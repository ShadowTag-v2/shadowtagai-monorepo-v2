"""
FinJudge Pure Judge API (v0.2)
Simplified REST interface for risk classification with freemium tier support
"""

import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.pure_judge import PureJudge
from ..models.judge import JudgeRequest, JudgeRuling
from .auth import APIKey, APIKeyAuth, APIKeyManager
from .signup import router as signup_router

# Initialize FastAPI app
app = FastAPI(
    title="FinJudge Pure Judge API",
    description="Risk classification engine using ATP 5-19 framework. Judge consumes metrics from upstream systems and produces risk assessments with decision memos.",
    version="0.2.0",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(","),
    allow_headers=os.environ.get("CORS_HEADERS", "Content-Type,Authorization,X-Requested-With").split(","),
)

# Include routers
app.include_router(signup_router)

# Initialize pure judge
judge = PureJudge(version="v0.2.0")

# Initialize API key manager
DB_URL = os.getenv("DATABASE_URL", "postgresql://REDACTED_USER:REDACTED_PASS@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="operational", version="v0.2.0", timestamp=datetime.utcnow(), engine_ready=True
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns service health and readiness status
    """
    return HealthResponse(
        status="healthy", version="v0.2.0", timestamp=datetime.utcnow(), engine_ready=True
    )


@app.post(
    "/v1/judge",
    response_model=JudgeRuling,
    status_code=status.HTTP_200_OK,
    tags=["Judge"],
    responses={
        200: {"description": "Risk assessment completed"},
        400: {"description": "Invalid request", "model": ErrorResponse},
        401: {"description": "Unauthorized - Invalid API key"},
        429: {"description": "Too many requests - Rate limit exceeded"},
        500: {"description": "Internal error", "model": ErrorResponse},
    },
)
async def judge_decision(request: JudgeRequest, api_key: APIKey = Depends(api_key_auth)):
    """
    Judge a financial decision using ATP 5-19 risk framework

    **Authentication**: Requires API key in Authorization header as Bearer token

    **Rate Limits**:
    - Free tier: 1,000 requests/month
    - Pro tier: 10,000 requests/month ($99/mo)
    - Business tier: 100,000 requests/month ($499/mo)
    - Enterprise tier: Unlimited ($2,499/mo)

    **Process**:
    1. Ingest metrics from upstream systems
    2. Synthesize risk features (capital_at_risk, liquidity_heat, etc.)
    3. Classify risk using ATP 5-19 matrix (Probability × Severity → Risk Level)
    4. Generate disposition (APPROVE/MODIFY/REJECT/ESCALATE)
    5. Produce decision memo with controls and explanation
    6. Create immutable audit trail

    **Input**: Metrics from calling module (financial_runway_monitor, phishing_detector, etc.)

    **Output**: Risk matrix + decision memo + required controls

    **Example Request**:
    ```bash
    curl -X POST https://api.finjudge.dev/v1/judge \
      -H "Authorization: Bearer fj_your_api_key_here" \
      -H "Content-Type: application/json" \
      -d '{
        "decision_id": "burn_rate_2025_11",
        "module": "financial_runway_monitor",
        "actor": {
          "role": "cfo",
          "org_unit": "Finance",
          "jurisdiction": "US"
        },
        "intent_nl": "Approve hiring 3 engineers, increasing burn by $60k/mo",
        "context": {
          "time_horizon": "long_term",
          "objective": "alpha",
          "constraints": ["max_12mo_runway"]
        },
        "metrics": {
          "exposure": {
            "notional": 720000,
            "pct_aum": 33.3,
            "leverage_ratio": 1.0
          },
          "custom": {
            "current_burn": 180000,
            "proposed_burn": 240000,
            "runway_months": 13.5
          }
        },
        "flags": {
          "policy_flags": ["approaching_12mo_runway_threshold"]
        }
      }'
    ```

    **Sign up**: Visit https://finjudge.dev to get your free API key
    """
    try:
        start_time = datetime.utcnow()

        # Judge the decision
        ruling = judge.judge(request)

        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Record usage for billing and analytics
        key_manager.record_usage(
            api_key_id=api_key.id,
            endpoint="/v1/judge",
            decision_id=ruling.decision_id,
            risk_level=ruling.risk_matrix.risk_level.value,
            disposition=ruling.recommendation.disposition.value,
            latency_ms=latency_ms,
        )

        # Store ruling
        ruling_store[ruling.decision_id] = ruling

        return ruling

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Judge engine error: {str(e)}",
        )


@app.get(
    "/v1/rulings/{decision_id}",
    response_model=JudgeRuling,
    tags=["Judge"],
    responses={
        200: {"description": "Ruling found"},
        404: {"description": "Ruling not found", "model": ErrorResponse},
    },
)
async def get_ruling(decision_id: str):
    """
    Retrieve a specific ruling by decision ID

    **Args**:
    - `decision_id`: Decision identifier from original request

    **Returns**:
    - Complete ruling with audit trail

    **Use Cases**:
    - Audit trail review
    - Precedent lookup
    - Compliance documentation
    """
    if decision_id not in ruling_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Ruling {decision_id} not found"
        )

    return ruling_store[decision_id]


@app.get(
    "/v1/usage",
    tags=["Account"],
    responses={200: {"description": "Usage statistics"}, 401: {"description": "Unauthorized"}},
)
async def get_usage(api_key: APIKey = Depends(api_key_auth)):
    """
    Get your API usage statistics

    **Authentication**: Requires API key

    **Returns**:
    - Current month usage
    - Monthly limit
    - Remaining requests
    - Tier information
    - Usage reset date

    **Example**:
    ```bash
    curl https://api.finjudge.dev/v1/usage \
      -H "Authorization: Bearer fj_your_api_key_here"
    ```
    """
    stats = key_manager.get_usage_stats(api_key.id)

    return {"email": api_key.email, "organization": api_key.organization, **stats}


@app.get("/v1/metrics", tags=["Analytics"])
async def get_metrics():
    """
    Get judge performance metrics

    **Metrics**:
    - Total rulings issued
    - Risk level distribution
    - Disposition distribution
    - Average computation time

    **Use Cases**:
    - Performance monitoring
    - Quality assurance
    - Usage tracking
    """
    rulings = list(ruling_store.values())

    if not rulings:
        return {"total_rulings": 0, "metrics": {}}

    # Risk level distribution
    risk_counts = {}
    for ruling in rulings:
        level = ruling.risk_matrix.risk_level.value
        risk_counts[level] = risk_counts.get(level, 0) + 1

    # Disposition distribution
    disposition_counts = {}
    for ruling in rulings:
        disp = ruling.recommendation.disposition.value
        disposition_counts[disp] = disposition_counts.get(disp, 0) + 1

    # Average computation time (from audit trail if available)
    # For MVP, return mock value
    avg_computation_ms = 45.0

    return {
        "total_rulings": len(rulings),
        "metrics": {
            "risk_levels": risk_counts,
            "dispositions": disposition_counts,
            "avg_computation_ms": avg_computation_ms,
        },
    }


@app.delete("/v1/rulings", status_code=status.HTTP_204_NO_CONTENT, tags=["Administration"])
async def clear_rulings(confirm: bool = False):
    """
    Clear all rulings from store

    **WARNING**: Destructive operation for testing only

    **Args**:
    - `confirm`: Must be true to proceed

    **Use Cases**:
    - Testing/development only
    - NOT for production use
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm deletion with ?confirm=true",
        )

    ruling_store.clear()
    return None


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("FinJudge Pure Judge API v0.2.0 started")
    print(f"Judge engine initialized: {judge.version}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("FinJudge Pure Judge API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("judge_api:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
