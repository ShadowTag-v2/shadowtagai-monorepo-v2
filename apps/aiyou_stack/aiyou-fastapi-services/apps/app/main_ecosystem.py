# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FastAPI application for SHADOWTAGAI Ultrathink Ecosystem.

Evolution from kernel chain to Jobs-inspired multi-agent platform with:
- Glicko-2 rated kernels/agents
- Multi-agent debates (PanelGPT/MAD)
- DTE self-evolution
- Cheat sheet fusion
- GRPO training
- Wealth planning model
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from prometheus_client import make_asgi_app

from app.agents import AgentConfig, DebateAgent, DebateOrchestrator
from app.config import settings
from app.evolution import CHEAT_SHEET_DTE_TEST, DTESystem, EvolutionStrategy
from app.kernels import ATP519ScanKernel, AuditCompressKernel, JudgeSixClassifyKernel
from app.kernels.base import KernelChainError
from app.models.decision import DecisionContext, DecisionResult
from app.monitoring import get_logger, metrics_collector, setup_logging
from app.orchestration import ChainExecutor, KernelChain
from app.prompts import (
    CHEAT_SHEET_VERSIONS,
    create_kernel_cheat_sheet,
    create_wealth_planning_cheat_sheet,
)

# Ecosystem imports
from app.ratings import Glicko2System, compare_rating_systems
from app.training import GRPOConfig, GRPOSimulator, compare_grpo_ppo
from app.validation import JREngine
from app.wealth import WealthAccelerator

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info(
        "Starting SHADOWTAGAI Ultrathink Ecosystem",
        extra={
            "service_name": settings.service_name,
            "version": "2.0.0-ecosystem",
        },
    )

    # Validate kernel chain with JR Engine
    jr_engine = JREngine()
    validation = jr_engine.validate_kernel_chain(
        [
            "ATP519ScanKernel",
            "JudgeSixClassifyKernel",
            "AuditCompressKernel",
        ],
    )

    if not validation.passed:
        logger.error(
            "Kernel chain failed JR Engine validation",
            extra={"validation": validation.dict()},
        )
        raise RuntimeError("Kernel chain validation failed")

    logger.info(
        "Pinkln ecosystem initialized",
        extra={
            "approved_kernels": validation.approved_kernels,
            "ecosystem_features": [
                "glicko2_ratings",
                "multi_agent_debates",
                "dte_evolution",
                "cheat_sheet_fusion",
                "grpo_training",
                "wealth_planning",
            ],
        },
    )

    yield

    logger.info("Shutting down Pinkln ecosystem")


# Create FastAPI app
app = FastAPI(
    title="Pinkln Ultrathink Ecosystem",
    description="Jobs-inspired multi-agent platform with kernel chaining, debates, and self-evolution",
    version="2.0.0",
    lifespan=lifespan,
)

# Mount Prometheus metrics endpoint
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Initialize kernel chain
def create_kernel_chain() -> ChainExecutor:
    """Create and configure the kernel chain."""
    kernels = [
        ATP519ScanKernel(),
        JudgeSixClassifyKernel(),
        AuditCompressKernel(),
    ]
    chain = KernelChain(kernels)
    return ChainExecutor(chain)


# Global instances
chain_executor = create_kernel_chain()
glicko_system = Glicko2System(tau=0.5, tol=1e-6)
grpo_simulator = GRPOSimulator(GRPOConfig())
dte_system = DTESystem()
wealth_accelerator = WealthAccelerator()


# =============================================================================
# CORE KERNEL CHAIN ENDPOINTS (original functionality)
# =============================================================================


@app.get("/")
async def root():
    """Root endpoint with ecosystem information."""
    return {
        "service": "Pinkln Ultrathink Ecosystem",
        "version": "2.0.0",
        "description": "Jobs-inspired multi-agent platform: beautiful, scalable AI",
        "core_concept": "Sequential specialized prompts >> monolithic complex prompt",
        "ecosystem_features": {
            "kernel_chain": "3-kernel decision pipeline (ATP scan → Judge → Audit compress)",
            "glicko2_ratings": "Performance tracking with uncertainty + volatility",
            "multi_agent_debates": "PanelGPT/MAD framework for collaborative reasoning",
            "dte_evolution": "Self-evolution via RCR-MAD + GRPO",
            "cheat_sheet_fusion": "10 essentials (evolved from 21, +3.7% accuracy)",
            "grpo_training": "Group Relative Policy Optimization vs PPO",
            "wealth_planning": "Spot leaks, redesign funnels, leverage viral/conversion",
        },
        "endpoints": {
            "POST /decision": "Execute kernel chain decision",
            "POST /debate": "Run multi-agent debate",
            "POST /evolve": "Evolve prompt via DTE",
            "POST /wealth/analyze": "Analyze business for wealth planning",
            "GET /ratings": "Compare rating systems (Glicko-2, Elo, PPO)",
            "GET /training/compare": "Compare GRPO vs PPO",
            "GET /cheat-sheet": "Get evolved cheat sheet",
            "GET /validation": "JR Engine validation report",
            "GET /ecosystem/status": "Full ecosystem status",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Pinkln Ultrathink Ecosystem",
        "version": "2.0.0",
    }


@app.post("/decision", response_model=DecisionResult)
async def execute_decision(context: DecisionContext):
    """Execute the full kernel chain decision pipeline (original endpoint)."""
    start_time = time.perf_counter()

    try:
        result = await chain_executor.execute_decision(context)

        if metrics_collector:
            metrics_collector.record_decision(
                latency_ms=result.total_latency_ms,
                cost_usd=result.total_cost_usd,
                confidence=result.confidence,
                risk_tier=result.risk_tier,
                violations_count=len(result.violations),
                success=True,
            )

        logger.info(
            "Decision executed successfully",
            extra={
                "trace_id": result.trace_id,
                "decision": result.decision,
                "confidence": result.confidence,
            },
        )

        return result

    except KernelChainError as e:
        (time.perf_counter() - start_time) * 1000

        if metrics_collector:
            metrics_collector.decisions_total.labels(status="failure").inc()

        logger.error(
            "Decision execution failed",
            extra={
                "trace_id": context.trace_id,
                "error": str(e),
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "trace_id": context.trace_id},
        ) from e


@app.get("/validation")
async def get_validation_report():
    """Get JR Engine validation report for the kernel chain."""
    jr_engine = JREngine()
    validation = jr_engine.validate_kernel_chain(
        [
            "ATP519ScanKernel",
            "JudgeSixClassifyKernel",
            "AuditCompressKernel",
        ],
    )

    return validation.dict()


# =============================================================================
# ECOSYSTEM ENDPOINTS (new functionality)
# =============================================================================


@app.post("/debate")
async def run_debate(question: str, num_agents: int = 3, max_rounds: int = 3):
    """Run multi-agent debate using PanelGPT/MAD framework.

    Args:
        question: Question to debate
        num_agents: Number of agents to participate
        max_rounds: Maximum debate rounds

    Returns:
        DebateResult with rounds and consensus

    """
    # Create debate agents
    agents = [
        DebateAgent(
            config=AgentConfig(
                name=f"DebateAgent_{i + 1}",
                description=f"Agent {i + 1} for multi-agent debate",
            ),
            persona=f"Critical thinker #{i + 1}",
        )
        for i in range(num_agents)
    ]

    # Run debate
    orchestrator = DebateOrchestrator(agents, max_rounds=max_rounds)
    result = await orchestrator.run_debate(question)

    return result.dict()


@app.post("/evolve")
async def evolve_prompt(
    prompt: str,
    strategy: EvolutionStrategy = EvolutionStrategy.RCR_MAD,
):
    """Evolve a prompt using DTE (Dynamic Test Evolution).

    Args:
        prompt: Current prompt to evolve
        strategy: Evolution strategy (RCR_MAD, GRPO, BENCHMARK)

    Returns:
        EvolutionResult with improvement metrics

    """
    test_cases = [
        {"input": "Sample input 1", "expected": "Output 1"},
        {"input": "Sample input 2", "expected": "Output 2"},
    ]

    result = await dte_system.evolve_prompt(prompt, test_cases, strategy)

    return result.dict()


@app.post("/wealth/analyze")
async def analyze_wealth(
    revenue_monthly: float,
    cac: float,
    ltv: float,
    churn_rate: float,
    conversion_rates: dict[str, float] = None,
):
    """Analyze business and generate wealth plan.

    Args:
        revenue_monthly: Monthly recurring revenue
        cac: Customer acquisition cost
        ltv: Lifetime value
        churn_rate: Monthly churn rate (%)
        conversion_rates: Conversion rates by funnel stage

    Returns:
        WealthPlan with leaks, plan, and challenge

    """
    if conversion_rates is None:
        conversion_rates = {}
    plan = wealth_accelerator.analyze_business(
        revenue_monthly=revenue_monthly,
        cac=cac,
        ltv=ltv,
        churn_rate=churn_rate,
        conversion_rates=conversion_rates or {},
    )

    return plan.dict()


@app.get("/ratings")
async def get_rating_systems():
    """Compare Glicko-2 vs Elo vs PPO rating approaches."""
    comparisons = compare_rating_systems()
    return {"systems": [c.dict() for c in comparisons]}


@app.get("/training/compare")
async def compare_training_systems():
    """Compare GRPO vs PPO training approaches."""
    comparisons = compare_grpo_ppo()
    return {"comparisons": [c.dict() for c in comparisons]}


@app.get("/cheat-sheet")
async def get_cheat_sheet(sheet_type: str = "kernel"):
    """Get evolved cheat sheet for prompt engineering.

    Args:
        sheet_type: Type of sheet (kernel, wealth)

    Returns:
        Cheat sheet with evolved 10 essentials

    """
    if sheet_type == "kernel":
        sheet = create_kernel_cheat_sheet()
    elif sheet_type == "wealth":
        sheet = create_wealth_planning_cheat_sheet()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sheet_type: {sheet_type}. Use 'kernel' or 'wealth'",
        )

    return {
        "cheat_sheet": sheet.dict(),
        "system_prompt": sheet.to_system_prompt(),
        "evolution_history": [v.dict() for v in CHEAT_SHEET_VERSIONS],
        "dte_test_result": CHEAT_SHEET_DTE_TEST.dict(),
    }


@app.get("/ecosystem/status")
async def ecosystem_status():
    """Get comprehensive ecosystem status."""
    return {
        "service": "Pinkln Ultrathink Ecosystem",
        "version": "2.0.0",
        "kernel_chain": {
            "kernels": 3,
            "target_latency_p99_ms": settings.max_latency_p99_ms,
            "target_cost_per_decision": settings.max_cost_per_decision,
        },
        "evolution": dte_system.get_evolution_summary(),
        "cheat_sheet": {
            "current_version": "v2.0",
            "elements": 10,
            "improvement_vs_baseline": 3.7,
        },
        "features_enabled": {
            "glicko2_ratings": True,
            "multi_agent_debates": True,
            "dte_evolution": True,
            "grpo_training": True,
            "wealth_planning": True,
            "prometheus_metrics": settings.enable_metrics,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main_ecosystem:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
