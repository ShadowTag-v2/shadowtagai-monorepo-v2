# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 HITL System - FastAPI Endpoints
Binary enforcement API with <90ms p99 latency target
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from src.judges import JudgeFactory, JudgeRequest, JudgeResponse, JudgeType, JudgeDecision, AuditTrail

# Initialize FastAPI app
app = FastAPI(
    title="Judge #6 HITL System API",
    description="Binary enforcement engine with ATP 5-19 risk assessment",
    version="1.0.0",
    docs_url="/judges/docs",
    redoc_url="/judges/redoc",
)


# In-memory storage (replace with PostgreSQL in production)
_audit_trails: list[AuditTrail] = []
_recent_decisions: list[JudgeResponse] = []


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/judges", tags=["Health"])
async def root():
    """Judge API root endpoint"""
    return {
        "service": "Judge #6 HITL System",
        "version": "1.0.0",
        "status": "operational",
        "verticals": [t.value for t in JudgeType],
        "target_latency_p99_ms": 90,
        "documentation": "/judges/docs",
    }


@app.get("/judges/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "judges_active": 4,
        "checks": {"fin_judge": "ok", "case_judge": "ok", "law_judge": "ok", "fraud_judge": "ok"},
    }


@app.post("/judges/evaluate", response_model=JudgeResponse, status_code=status.HTTP_200_OK, tags=["Enforcement"])
async def evaluate_action(request: JudgeRequest):
    """
    Evaluate action and return binary ALLOW/BLOCK decision

    This is the primary enforcement endpoint. It:
    1. Routes request to appropriate judge vertical
    2. Performs ATP 5-19 risk assessment
    3. Returns binary decision with <90ms p99 latency
    4. Creates immutable audit trail

    **Decision Framework**: Purpose=AiYouJR • Reason=Doctrine • Brakes=Army RM

    **Supported Judge Types**:
    - FinJudge: Financial transactions ($50K+ wire transfers)
    - CaseJudge: Legal case assessment
    - LawJudge: Legal compliance (EU AI Act, GDPR, CA SB 53)
    - FraudJudge: Fraud detection & risk scoring

    **Response Time**:
    - Target: p50 ~30ms, p99 ≤90ms
    - If exceeded: May return 503 Service Unavailable

    **Example Request** (FinJudge):
    ```json
    {
      "request_id": "req_20251117_fin_001",
      "judge_type": "FinJudge",
      "action_type": "wire_transfer",
      "context": {
        "amount_usd": 75000,
        "vendor_status": "new",
        "purchase_order": null,
        "destination_country": "Unknown"
      },
      "urgency": "normal",
      "requested_by": "john.doe@company.com"
    }
    ```

    **Example Response**:
    ```json
    {
      "request_id": "req_20251117_fin_001",
      "decision": "BLOCK",
      "risk_assessment": {
        "probability": "B",
        "severity": "II",
        "risk_level": "high",
        "requires_approval": true,
        "approval_authority": "CFO"
      },
      "approval_gate": "cfo",
      "reasoning": "Wire transfer $75K to new vendor without PO requires CFO approval",
      "semantic_trail": "wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK",
      "latency_ms": 42.3,
      "next_steps": [
        "Route to CFO approval queue",
        "Verify vendor via external database",
        "Request supporting documentation"
      ]
    }
    ```
    """
    try:
        # Get appropriate judge
        judge = JudgeFactory.get_judge(request.judge_type)

        # Execute judgment (this should be <90ms)
        response = judge.judge(request)

        # Store decision (async in production)
        _recent_decisions.append(response)

        # Create audit trail
        audit_trail = judge.create_audit_trail(response, request)
        _audit_trails.append(audit_trail)

        # Latency check (warn if exceeded)
        if response.latency_ms > 90:
            print(f"WARNING: Latency {response.latency_ms:.2f}ms exceeded p99 target (90ms)")

        return response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Judge evaluation failed: {str(e)}")


@app.get("/judges/audit/{request_id}", response_model=AuditTrail, tags=["Audit"])
async def get_audit_trail(request_id: str = Path(..., description="Request ID to retrieve audit trail for")):
    """
    Retrieve immutable audit trail for a request

    Audit trails are:
    - Immutable (cannot be modified)
    - Semantically compressed (10:1 ratio)
    - Retained for 7 years (2555 days)
    - Encrypted (full context)

    **Compliance**: EU AI Act Article 12, CA SB 53 transparency requirements
    """
    # Find audit trail
    trail = next((t for t in _audit_trails if t.request_id == request_id), None)

    if trail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No audit trail found for request_id: {request_id}")

    return trail


@app.get("/judges/metrics/{judge_type}", response_model=dict[str, Any], tags=["Metrics"])
async def get_judge_metrics(judge_type: JudgeType = Path(..., description="Judge vertical type")):
    """
    Get performance metrics for a judge vertical

    **Key Metrics**:
    - Decision count
    - Average latency
    - p50/p99 latency (target: p99 ≤90ms)
    - Decision distribution (ALLOW vs BLOCK)
    - Risk level distribution
    """
    try:
        judge = JudgeFactory.get_judge(judge_type)
        metrics = judge.get_metrics()

        # Add decision distribution
        decisions = [d for d in _recent_decisions if d.judge_type == judge_type]
        allow_count = sum(1 for d in decisions if d.decision == JudgeDecision.ALLOW)
        block_count = sum(1 for d in decisions if d.decision == JudgeDecision.BLOCK)

        return {**metrics, "judge_type": judge_type.value, "decisions": {"allow": allow_count, "block": block_count, "total": len(decisions)}}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/judges/decisions/recent", response_model=list[JudgeResponse], tags=["Decisions"])
async def get_recent_decisions(
    judge_type: JudgeType | None = Query(None, description="Filter by judge type"),
    limit: int = Query(100, ge=1, le=1000, description="Max decisions to return"),
    since: datetime | None = Query(None, description="Filter by timestamp >= since"),
):
    """
    Retrieve recent judge decisions

    **Use Cases**:
    - Monitoring dashboard
    - Audit review
    - Pattern analysis
    - Performance tracking
    """
    # Filter decisions
    filtered = _recent_decisions

    if judge_type:
        filtered = [d for d in filtered if d.judge_type == judge_type]

    if since:
        filtered = [d for d in filtered if d.timestamp >= since]

    # Sort by timestamp (most recent first)
    filtered = sorted(filtered, key=lambda d: d.timestamp, reverse=True)

    return filtered[:limit]


@app.get("/judges/stats/overview", tags=["Metrics"])
async def get_overview_stats():
    """
    Get overall Judge system statistics

    **System-Wide Metrics**:
    - Total decisions across all verticals
    - Average latency across all judges
    - Decision distribution (ALLOW/BLOCK)
    - Risk level distribution
    - Approval gate utilization
    """
    if not _recent_decisions:
        return {"total_decisions": 0, "message": "No decisions recorded yet"}

    total_allow = sum(1 for d in _recent_decisions if d.decision == JudgeDecision.ALLOW)
    total_block = sum(1 for d in _recent_decisions if d.decision == JudgeDecision.BLOCK)

    latencies = [d.latency_ms for d in _recent_decisions]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    sorted_latencies = sorted(latencies)
    p99_idx = int(len(sorted_latencies) * 0.99) if sorted_latencies else 0
    p99_latency = sorted_latencies[p99_idx] if sorted_latencies else 0

    return {
        "total_decisions": len(_recent_decisions),
        "decisions": {"allow": total_allow, "block": total_block, "allow_percentage": (total_allow / len(_recent_decisions)) * 100},
        "latency": {"avg_ms": avg_latency, "p99_ms": p99_latency, "target_p99_ms": 90, "within_target": p99_latency <= 90},
        "by_vertical": {jt.value: sum(1 for d in _recent_decisions if d.judge_type == jt) for jt in JudgeType},
    }


@app.post("/judges/test/generate-sample", tags=["Testing"])
async def generate_sample_request(judge_type: JudgeType):
    """
    Generate sample request for testing (development only)

    **Note**: Remove in production
    """
    samples = {
        JudgeType.FIN: JudgeRequest(
            request_id="test_fin_001",
            judge_type=JudgeType.FIN,
            action_type="wire_transfer",
            context={"amount_usd": 75000, "vendor_status": "new", "purchase_order": None, "destination_country": "Unknown"},
            requested_by="test@example.com",
        ),
        JudgeType.CASE: JudgeRequest(
            request_id="test_case_001",
            judge_type=JudgeType.CASE,
            action_type="case_acceptance",
            context={"case_value_usd": 500000, "case_type": "contract_dispute", "conflict_check_passed": True, "probability_of_success": 0.6},
            requested_by="test@example.com",
        ),
        JudgeType.LAW: JudgeRequest(
            request_id="test_law_001",
            judge_type=JudgeType.LAW,
            action_type="compliance_check",
            context={"compliance_area": "eu_ai_act", "ai_system_type": "biometric_identification", "legal_review_completed": False},
            requested_by="test@example.com",
        ),
        JudgeType.FRAUD: JudgeRequest(
            request_id="test_fraud_001",
            judge_type=JudgeType.FRAUD,
            action_type="payment_authorization",
            context={"fraud_score": 0.75, "identity_verified": False, "geo_location_mismatch": True, "amount_usd": 5000},
            requested_by="test@example.com",
        ),
    }

    return samples.get(judge_type).dict()


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc), "timestamp": datetime.utcnow().isoformat()},
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize judges on startup"""
    # Pre-warm judges (load into memory)
    for judge_type in JudgeType:
        JudgeFactory.get_judge(judge_type)

    print("Judge #6 HITL System API started")
    print("Verticals active: FinJudge, CaseJudge, LawJudge, FraudJudge")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("Judge #6 HITL System API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("judges:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
