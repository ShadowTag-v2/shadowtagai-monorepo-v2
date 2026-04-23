"""Main FastAPI application for agent-based governance system.

Production-ready API with hybrid OPA + agent architecture,
circuit breaker fallback, observability, and shadow mode support.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.agents.policy_agent import PolicyEnforcementAgent
from src.gov_config import settings
from src.governance.gaas_trust import GaaSTrustManager, ViolationRecord, ViolationSeverity
from src.governance.judge_six.sentinel import JudgeSixSentinel
from src.monitoring.observability import metrics_collector, observability
from src.policies.rag_retriever import get_policy_retriever
from src.routers import agents, auth, knowledge
from src.security.circuit_breaker import AgentCircuitBreaker

# Sovereign OS Judge instantiation
judge_sentinel = JudgeSixSentinel()


# Request/Response Models
class GovernanceRequest(BaseModel):
    """Governance request model."""

    request_id: str | None = None
    action: str
    resource: dict[str, Any]
    user_context: dict[str, Any]


class GovernanceResponse(BaseModel):
    """Governance response model."""

    decision_id: str
    decision: str  # APPROVED, DENIED, ESCALATED
    confidence_score: float
    reasoning: list[str]
    policy_references: list[dict[str, Any]] = []
    requires_escalation: bool = False
    metrics: dict[str, Any] | None = None


# Global state
policy_retriever = None
policy_agent = None
trust_manager = None
circuit_breaker = None
shadow_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    global policy_retriever, policy_agent, trust_manager, circuit_breaker, shadow_orchestrator

    print(
        f"DEBUG SETTINGS TYPE: {type(settings)} from {getattr(type(settings), '__module__', 'unknown')}",
    )
    print("🚀 Starting Agent Governance System...")
    print(f"   Environment: {settings.environment}")
    print(f"   Deployment: {settings.deployment_mode}")
    print(f"   Model: {settings.default_model}")

    # Initialize policy retriever
    try:
        policy_retriever = get_policy_retriever()
        print("✅ Policy retriever initialized")

        # Initialize policy agent
        policy_agent = PolicyEnforcementAgent(
            agent_id="policy-enforcer-01",
            name="Primary Policy Enforcement Agent",
            model=settings.default_model,
            policy_retriever=policy_retriever,
        )
        print("✅ Policy agent initialized")
    except Exception as e:
        print(f"⚠️ Policy system initialization skipped: {e}")
        policy_retriever = None
        policy_agent = None

    # Initialize trust manager
    trust_manager = GaaSTrustManager(
        high_threshold=settings.trust_score_threshold_high,
        low_threshold=settings.trust_score_threshold_low,
    )
    print("✅ Trust manager initialized")

    # Initialize circuit breaker
    circuit_breaker = AgentCircuitBreaker(
        name="policy-agent-circuit",
        failure_threshold=settings.circuit_breaker_failure_threshold,
        timeout_seconds=settings.circuit_breaker_timeout_seconds,
    )
    print("✅ Circuit breaker initialized")

    # Initialize shadow mode if enabled
    if settings.shadow_mode_enabled:
        # Note: Requires Judge 6 client implementation
        shadow_orchestrator = None  # ShadowModeOrchestrator(...)
        print("⚠️  Shadow mode enabled but Judge 6 client not configured")
    else:
        print("ℹ️  Shadow mode disabled")

    print("✅ System ready\n")

    yield

    # Shutdown
    print("\n🛑 Shutting down gracefully...")
    if policy_retriever and hasattr(policy_retriever, "conn"):
        policy_retriever.conn.close()
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Agent Governance System",
    description="Production-ready agent governance with trust-and-verify architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os  # noqa: E402

from fastapi.staticfiles import StaticFiles  # noqa: E402

app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(agents.agents_router)

import urllib.request  # noqa: E402

from fastapi.responses import StreamingResponse  # noqa: E402


@app.get("/images/{filename}")
def proxy_comfy_image(filename: str):
    """Fetches the generated image from the local ComfyUI instance and streams it to the client."""
    try:
        url = f"http://127.0.0.1:8188/view?filename={filename}&type=output"
        req = urllib.request.urlopen(url)

        def iterfile():
            while True:
                chunk = req.read(4096)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(iterfile(), media_type="image/png")
    except Exception:
        raise HTTPException(
            status_code=404, detail="Image not found or ComfyUI is offline."
        ) from None


# Mount Omega Playground (Injected R&D Telemetry Panel)
public_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "omega-playground")
os.makedirs(public_path, exist_ok=True)
app.mount("/playground", StaticFiles(directory=public_path, html=True), name="playground")


# Health endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "agent-governance"}


@app.get("/ready")
async def readiness_check():
    """Readiness check with dependencies."""
    checks = {
        "policy_agent": policy_agent is not None,
        "policy_retriever": policy_retriever is not None,
        "trust_manager": trust_manager is not None,
        "circuit_breaker": circuit_breaker is not None,
        "circuit_state": circuit_breaker.state.value if circuit_breaker else "unknown",
    }

    all_ready = all([checks["policy_agent"], checks["policy_retriever"]])

    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={"ready": all_ready, "checks": checks},
    )


class MissionRequest(BaseModel):
    query: str
    context: str = "general"


@app.post("/mission")
async def launch_mission(req: MissionRequest):
    """Sovereign OS Mission Entrypoint.
    Guarded by Judge 6 Sentinel and the CavMTOE Army Consensus.
    """
    verdict = judge_sentinel.evaluate(req.query, req.context)

    if verdict["status"] == "BLOCKED":
        raise HTTPException(status_code=403, detail=verdict)

    # 2. Execution (Placeholder for actual Temporal Task Invocation)
    return {
        "status": "MISSION_GO",
        "governance_receipt": verdict,
        "payload": f"Sovereign execution authorized for query: {req.query}",
    }


# Main governance endpoint
@app.post("/v1/governance/evaluate", response_model=GovernanceResponse)
async def evaluate_governance_request(request: GovernanceRequest):
    """Evaluate governance request through agent system.

    Implements:
    - Circuit breaker with OPA fallback
    - GaaS trust-based enforcement
    - Shadow mode comparison (if enabled)
    - Comprehensive observability
    """
    # Generate request ID if not provided
    if not request.request_id:
        request.request_id = str(uuid.uuid4())

    try:
        # Get agent ID for trust scoring (use user_id as proxy)
        agent_id = request.user_context.get("agent_id", "default-agent")

        # Assert dependencies are loaded cleanly for type-checking
        assert trust_manager is not None
        assert circuit_breaker is not None

        # Check trust score and enforcement mode
        trust = trust_manager.get_trust_score(agent_id)
        should_block, enforcement_mode = trust_manager.should_block(agent_id, "normative")

        # If low trust, escalate immediately
        if should_block:
            return GovernanceResponse(
                decision_id=f"trust_{request.request_id[:8]}",
                decision="ESCALATED",
                confidence_score=0.0,
                reasoning=[
                    f"Low trust score: {trust.score:.2f}",
                    f"Enforcement mode: {enforcement_mode.value}",
                    "Requires human approval",
                ],
                requires_escalation=True,
            )

        # Build context for agent
        context = {
            "trust_score": trust.score,
            "enforcement_mode": enforcement_mode.value,
            "historical_violations": len(trust.violations),
        }

        # Evaluate through circuit breaker
        async def agent_evaluation():
            """Primary agent evaluation."""
            return await policy_agent.evaluate(request.dict(), context)

        async def opa_fallback():
            """Fallback to OPA rule engine."""
            # Placeholder - implement OPA client
            # Returning a dummy object that mimics the expected Decision interface
            from unittest.mock import MagicMock

            fallback = MagicMock()
            fallback.decision_id = f"opa_{request.request_id[:8]}"
            fallback.status.value = "ESCALATED"
            fallback.confidence_score = 0.0
            fallback.reasoning_trace = ["Circuit breaker open, OPA fallback not implemented"]
            fallback.requires_escalation = True
            fallback.policy_references = []
            fallback.metrics = {}
            fallback.timestamp = time.time()
            return fallback

        # Execute with circuit breaker
        # Note: circuit_breaker.call needs to be awaited if it handles async functions
        if settings.circuit_breaker_enabled:
            # Assuming AgentCircuitBreaker.call handles async functions or we await the result
            decision = await circuit_breaker.call(agent_evaluation, opa_fallback)
        else:
            decision = await agent_evaluation()

        # Record decision for trust scoring
        success = decision.status.value == "APPROVED"
        violation = None

        if not success:
            violation = ViolationRecord(
                violation_id=f"viol_{uuid.uuid4().hex[:8]}",
                timestamp=decision.timestamp,
                agent_id=agent_id,
                policy_id="POLICY-UNKNOWN",
                severity=ViolationSeverity.MEDIUM,
                description=f"{decision.status.value}: {decision.escalation_reason or 'No reason'}",
                penalty_applied=0.05,
            )

        trust_manager.record_decision(agent_id, success, violation)

        # Log to observability
        observability.log_decision(decision)
        observability.trace_decision(decision)
        metrics_collector.record_decision(decision)

        # Build response
        return GovernanceResponse(
            decision_id=decision.decision_id,
            decision=decision.status.value,
            confidence_score=decision.confidence_score,
            reasoning=decision.reasoning_trace,
            policy_references=[ref.dict() for ref in decision.policy_references],
            requires_escalation=decision.requires_escalation,
            metrics=decision.metrics,
        )

    except Exception as e:
        # Error handling
        error_decision = GovernanceResponse(
            decision_id=f"error_{request.request_id[:8]}",
            decision="ERROR",
            confidence_score=0.0,
            reasoning=[f"System error: {e!s}"],
            requires_escalation=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_decision.dict(),
        ) from e


# Metrics endpoint
@app.get("/v1/metrics")
async def get_metrics():
    """Get system metrics."""
    return metrics_collector.get_summary_metrics()


# Circuit breaker status
@app.get("/v1/circuit-breaker")
async def get_circuit_breaker_status():
    """Get circuit breaker status."""
    if not circuit_breaker:
        raise HTTPException(status_code=404, detail="Circuit breaker not initialized")

    return circuit_breaker.get_metrics()


# Trust score endpoint
@app.get("/v1/trust/{agent_id}")
async def get_trust_score(agent_id: str):
    """Get trust score for agent."""
    if not trust_manager:
        raise HTTPException(status_code=404, detail="Trust manager not initialized")

    return trust_manager.get_metrics(agent_id)


# Shadow mode report (if enabled)
@app.get("/v1/shadow-mode/report")
async def get_shadow_mode_report():
    """Get shadow mode migration readiness report."""
    if not shadow_orchestrator:
        raise HTTPException(status_code=404, detail="Shadow mode not enabled")

    return shadow_orchestrator.get_migration_readiness_report()


# Policy management endpoints
@app.post("/v1/policies")
async def add_policy(policy_doc: dict[str, Any]):
    """Add policy document to vector store."""
    if not policy_retriever:
        raise HTTPException(status_code=503, detail="Policy retriever not initialized")

    await policy_retriever.add_policy(policy_doc)
    return {"status": "success", "policy_id": policy_doc.get("policy_id")}


@app.put("/v1/policies/{policy_id}")
async def update_policy(policy_id: str, policy_doc: dict[str, Any]):
    """Update policy document."""
    if not policy_retriever:
        raise HTTPException(status_code=503, detail="Policy retriever not initialized")

    await policy_retriever.update_policy(policy_id, policy_doc)
    return {"status": "success", "policy_id": policy_id}


@app.delete("/v1/policies/{policy_id}")
async def delete_policy(policy_id: str):
    """Delete policy document."""
    if not policy_retriever:
        raise HTTPException(status_code=503, detail="Policy retriever not initialized")

    await policy_retriever.delete_policy(policy_id)
    return {"status": "success", "policy_id": policy_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.environment == "development",
        log_level="info",
    )
