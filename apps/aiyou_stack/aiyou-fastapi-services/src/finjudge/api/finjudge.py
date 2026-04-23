"""FinJudge API
FastAPI endpoints for financial governance decisions
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.decision_engine import DecisionEngine
from ..models.base import DecisionOutcome, DecisionRequest, DecisionRuling

# Initialize FastAPI app
app = FastAPI(
    title="FinJudge API",
    description="Supreme Court Clerk for Financial Decisions - ATP 5-19 Risk Governance",
    version="0.1.0",
    docs_url="/finjudge/docs",
    redoc_url="/finjudge/redoc",
)

# Initialize decision engine
decision_engine = DecisionEngine(model_version="v0.1.0")

# In-memory ruling storage (replace with PostgreSQL in production)
ruling_store: dict[str, DecisionRuling] = {}


# ============================================================================
# Response Models
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="FinJudge version")
    timestamp: datetime = Field(..., description="Current timestamp")
    engine_ready: bool = Field(..., description="Decision engine status")


class RulingListResponse(BaseModel):
    """Ruling list response"""

    total: int = Field(..., description="Total rulings")
    rulings: list[DecisionRuling] = Field(..., description="Ruling list")


class ErrorResponse(BaseModel):
    """Error response"""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """FinJudge API root endpoint"""
    return HealthResponse(
        status="operational",
        version="v0.1.0",
        timestamp=datetime.utcnow(),
        engine_ready=True,
    )


@app.get("/finjudge/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint

    Returns service health status and readiness
    """
    return HealthResponse(
        status="healthy",
        version="v0.1.0",
        timestamp=datetime.utcnow(),
        engine_ready=True,
    )


@app.post(
    "/finjudge/evaluate",
    response_model=DecisionRuling,
    status_code=status.HTTP_200_OK,
    tags=["Decisions"],
    responses={
        200: {"description": "Ruling issued successfully"},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal error", "model": ErrorResponse},
    },
)
async def evaluate_decision(request: DecisionRequest):
    """Evaluate a financial governance decision request

    **Process**:
    1. Validate request schema and evidence
    2. Assess risk using ATP 5-19 framework
    3. Check regulatory compliance
    4. Apply internal policy rules
    5. Synthesize decision with confidence score
    6. Generate Supreme Court-style ruling
    7. Store ruling in audit trail

    **Returns**:
    - Decision ruling with rationale, risk assessment, and conditions

    **Example Request**:
    ```json
    {
      "decision_type": "trade_approval",
      "context": {
        "timestamp": "2025-11-17T14:30:00Z",
        "entity": "Equity Trading Desk Alpha",
        "purpose": "Approve AAPL 10K share block trade"
      },
      "evidence": [
        {
          "type": "market_data",
          "source": "Bloomberg",
          "data": {"symbol": "AAPL", "price": 175.50},
          "confidence": 95.0
        },
        {
          "type": "risk_metric",
          "source": "Internal Risk System",
          "data": {"probability": 25.0, "expected_loss": 125000},
          "confidence": 90.0
        }
      ],
      "constraints": {
        "regulatory": ["SEC Rule 15c3-1"],
        "risk_limits": {"position_limit": 50000}
      }
    }
    ```

    **Billing**: Each evaluation = 1 billable event
    """
    try:
        # Evaluate decision
        ruling = decision_engine.evaluate(request)

        # Store ruling (in-memory for MVP, PostgreSQL for production)
        ruling_store[str(ruling.ruling_id)] = ruling

        return ruling

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {e!s}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision engine error: {e!s}",
        ) from e


@app.get(
    "/finjudge/rulings/{ruling_id}",
    response_model=DecisionRuling,
    tags=["Decisions"],
    responses={
        200: {"description": "Ruling found"},
        404: {"description": "Ruling not found", "model": ErrorResponse},
    },
)
async def get_ruling(ruling_id: str):
    """Retrieve a specific ruling by ID

    **Args**:
    - `ruling_id`: UUID v7 ruling identifier

    **Returns**:
    - Complete ruling record with audit trail

    **Use Cases**:
    - Audit trail review
    - Precedent lookup
    - Compliance documentation
    """
    if ruling_id not in ruling_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruling {ruling_id} not found",
        )

    return ruling_store[ruling_id]


@app.get("/finjudge/rulings", response_model=RulingListResponse, tags=["Decisions"])
async def list_rulings(
    decision_outcome: DecisionOutcome | None = Query(  # noqa: B008
        None,
        description="Filter by decision outcome",
    ),
    limit: int = Query(100, ge=1, le=1000, description="Max rulings to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """List rulings with optional filters

    **Query Parameters**:
    - `decision_outcome`: Filter by APPROVE, DENY, APPROVE_WITH_CONDITIONS, etc.
    - `limit`: Max results (1-1000)
    - `offset`: Pagination offset

    **Returns**:
    - List of rulings matching criteria

    **Use Cases**:
    - Historical analysis
    - Pattern identification
    - Compliance reporting
    """
    rulings = list(ruling_store.values())

    # Apply filters
    if decision_outcome:
        rulings = [r for r in rulings if r.decision == decision_outcome]

    # Sort by timestamp (newest first)
    rulings.sort(key=lambda r: r.timestamp, reverse=True)

    # Pagination
    paginated = rulings[offset : offset + limit]

    return RulingListResponse(total=len(rulings), rulings=paginated)


@app.get(
    "/finjudge/rulings/{ruling_id}/precedents",
    response_model=list[DecisionRuling],
    tags=["Decisions"],
)
async def get_precedents(
    ruling_id: str,
    limit: int = Query(10, ge=1, le=50, description="Max precedents to return"),
):
    """Find similar past rulings (precedents)

    **Args**:
    - `ruling_id`: Base ruling to find precedents for
    - `limit`: Max precedents to return

    **Returns**:
    - List of similar historical rulings

    **Algorithm** (MVP):
    - Match decision_type
    - Match risk_level
    - Sort by timestamp

    **Production Enhancement**:
    - Semantic similarity (embeddings)
    - Entity matching (counterparties, instruments)
    - Outcome correlation
    """
    if ruling_id not in ruling_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruling {ruling_id} not found",
        )

    base_ruling = ruling_store[ruling_id]
    precedents = []

    for r_id, ruling in ruling_store.items():
        if r_id == ruling_id:
            continue

        # Simple matching: same risk level
        if ruling.risk_assessment.level == base_ruling.risk_assessment.level:
            precedents.append(ruling)

    # Sort by timestamp (newest first)
    precedents.sort(key=lambda r: r.timestamp, reverse=True)

    return precedents[:limit]


@app.get("/finjudge/metrics", tags=["Analytics"])
async def get_metrics(days: int = Query(7, ge=1, le=90, description="Number of days for metrics")):
    """Get FinJudge performance metrics

    **Metrics**:
    - Total rulings issued
    - Decision distribution (APPROVE/DENY/etc.)
    - Average confidence score
    - Risk level distribution
    - Compliance violation rate
    - Average computation time

    **Use Cases**:
    - Performance monitoring
    - Quality assurance
    - SLA validation
    """
    rulings = list(ruling_store.values())

    # Filter by time window
    cutoff = datetime.utcnow().timestamp() - (days * 86400)
    recent_rulings = [r for r in rulings if r.timestamp.timestamp() > cutoff]

    if not recent_rulings:
        return {"period_days": days, "total_rulings": 0, "metrics": {}}

    # Calculate metrics
    decision_counts = {}
    for outcome in DecisionOutcome:
        decision_counts[outcome.value] = sum(1 for r in recent_rulings if r.decision == outcome)

    risk_counts = {}
    for r in recent_rulings:
        level = r.risk_assessment.level.value
        risk_counts[level] = risk_counts.get(level, 0) + 1

    avg_confidence = sum(r.confidence for r in recent_rulings) / len(recent_rulings)
    avg_computation_ms = sum(r.audit_trail.computation_time_ms for r in recent_rulings) / len(
        recent_rulings,
    )

    compliance_violations = sum(
        1 for r in recent_rulings if any(f.status.value == "violation" for f in r.compliance_flags)
    )

    return {
        "period_days": days,
        "total_rulings": len(recent_rulings),
        "metrics": {
            "decisions": decision_counts,
            "risk_levels": risk_counts,
            "avg_confidence": round(avg_confidence, 1),
            "avg_computation_ms": round(avg_computation_ms, 1),
            "compliance_violation_rate": round(
                (compliance_violations / len(recent_rulings)) * 100,
                1,
            ),
        },
    }


@app.delete("/finjudge/rulings", status_code=status.HTTP_204_NO_CONTENT, tags=["Administration"])
async def clear_rulings(confirm: bool = Query(False, description="Confirm deletion")):
    """Clear all rulings from store

    **WARNING**: This is destructive and irreversible in production

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
    print("FinJudge API v0.1.0 started")
    print(f"Decision engine initialized: {decision_engine.model_version}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("FinJudge API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("finjudge:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
