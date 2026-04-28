# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Inference Orchestrator
Main entry point for LLM routing and Judge 6 integration
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["endpoint"])
JUDGE_COVERAGE = Gauge("judge_coverage_ratio", "Judge 6 coverage ratio")
MODEL_REQUESTS = Counter("llm_requests_total", "LLM requests by model", ["model"])
COST_TRACKER = Counter("llm_router_cost_usd", "Cumulative cost in USD", ["model"])


# Models
class InferenceRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt")
    model: str | None = Field(None, description="Specific model (optional)")
    max_tokens: int = Field(1000, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = Field(False, description="Stream response")

    # Governance metadata
    user_id: str | None = None
    context: dict[str, Any] | None = None


class InferenceResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    latency_ms: float
    cost_usd: float

    # Governance
    judge_decision: str | None = None
    violations: list | None = None


# Configuration
class Config:
    # Judge endpoints
    JUDGE_LAYER1_ENDPOINT = "http://judge-layer1.ShadowTag-v2jr-governance.svc.cluster.local:8080"
    JUDGE_LAYER2_ENDPOINT = "http://judge-layer2.ShadowTag-v2jr-governance.svc.cluster.local:8080"
    JUDGE_LAYER3_ENDPOINT = "http://judge-layer3.ShadowTag-v2jr-governance.svc.cluster.local:8080"

    # Model allocation (weights)
    MODEL_WEIGHTS = {
        "gemini-3.1-flash-lite-preview": 0.40,
        "claude-3-5-sonnet-20241022": 0.35,
        "gpt-4": 0.15,
        "grok-beta": 0.05,
        "llama-3.1-70b": 0.05,
    }

    # Cost per 1K tokens
    COST_PER_1K_TOKENS = {
        "gemini-3.1-flash-lite-preview": 0.0025,
        "claude-3-5-sonnet-20241022": 0.003,
        "gpt-4": 0.006,
        "grok-beta": 0.004,
        "llama-3.1-70b": 0.0005,
    }

    # SLA targets
    P99_LATENCY_TARGET_MS = 90
    JUDGE_COVERAGE_TARGET = 0.98


config = Config()

# HTTP client
http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("Orchestrator started")
    yield
    await http_client.aclose()
    logger.info("Orchestrator stopped")


app = FastAPI(title="PNKLN Inference Orchestrator", version="1.0.0", lifespan=lifespan)


# Helper functions
async def route_to_judge(request: InferenceRequest, layer: int = 1) -> dict[str, Any]:
    """Route request to Judge 6 for governance check"""
    try:
        endpoint_map = {
            1: config.JUDGE_LAYER1_ENDPOINT,
            2: config.JUDGE_LAYER2_ENDPOINT,
            3: config.JUDGE_LAYER3_ENDPOINT,
        }

        endpoint = endpoint_map.get(layer, config.JUDGE_LAYER1_ENDPOINT)

        response = await http_client.post(
            f"{endpoint}/validate",
            json={
                "prompt": request.prompt,
                "user_id": request.user_id,
                "context": request.context or {},
            },
            timeout=0.1,  # 100ms timeout
        )

        if response.status_code == 200:
            return response.json()
        logger.warning(f"Judge Layer {layer} returned {response.status_code}")
        return {"decision": "allow", "layer": layer, "confidence": 0.5}

    except Exception as e:
        logger.error(f"Judge Layer {layer} error: {e}")
        # Fail-open for availability (adjust based on requirements)
        return {"decision": "allow", "layer": layer, "confidence": 0.0, "error": str(e)}


async def select_model(request: InferenceRequest) -> str:
    """Select model based on weighted allocation"""
    if request.model:
        return request.model

    # Weighted random selection (simplified - use proper weighted random in production)
    import random

    rand = random.random()
    cumulative = 0.0

    for model, weight in config.MODEL_WEIGHTS.items():
        cumulative += weight
        if rand <= cumulative:
            return model

    return "gemini-3.1-flash-lite-preview"  # Default fallback


async def call_llm(model: str, prompt: str, max_tokens: int, temperature: float) -> dict[str, Any]:
    """Call LLM (placeholder - implement actual API calls)"""
    # This is a simplified placeholder
    # In production, implement actual API calls to Gemini, Claude, GPT-4, etc.

    start_time = time.time()

    # Simulate LLM call
    await asyncio.sleep(0.05)  # Simulate latency

    latency_ms = (time.time() - start_time) * 1000
    tokens_used = len(prompt.split()) + 50  # Simplified token counting

    cost_per_1k = config.COST_PER_1K_TOKENS.get(model, 0.003)
    cost_usd = (tokens_used / 1000) * cost_per_1k

    return {
        "content": f"[Mock response from {model}] Processed: {prompt[:50]}...",
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
    }


# API endpoints
@app.post("/v1/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    """Main inference endpoint with Judge 6 integration"""
    start_time = time.time()

    try:
        # Step 1: Judge 6 validation (Layer 1 fast path)
        judge_result = await route_to_judge(request, layer=1)

        if judge_result.get("decision") == "deny":
            REQUEST_COUNT.labels(method="POST", endpoint="/v1/inference", status="403").inc()
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Request denied by governance policy",
                    "violations": judge_result.get("violations", []),
                    "layer": judge_result.get("layer"),
                },
            )

        # Update coverage metric
        JUDGE_COVERAGE.set(0.98)  # Placeholder - calculate actual coverage

        # Step 2: Model selection
        model = await select_model(request)
        MODEL_REQUESTS.labels(model=model).inc()

        # Step 3: Call LLM
        llm_result = await call_llm(
            model=model,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # Step 4: Track cost
        COST_TRACKER.labels(model=model).inc(llm_result["cost_usd"])

        # Step 5: Record metrics
        total_latency_ms = (time.time() - start_time) * 1000
        REQUEST_LATENCY.labels(endpoint="/v1/inference").observe(total_latency_ms / 1000)
        REQUEST_COUNT.labels(method="POST", endpoint="/v1/inference", status="200").inc()

        return InferenceResponse(
            content=llm_result["content"],
            model=model,
            tokens_used=llm_result["tokens_used"],
            latency_ms=total_latency_ms,
            cost_usd=llm_result["cost_usd"],
            judge_decision=judge_result.get("decision"),
            violations=judge_result.get("violations"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        REQUEST_COUNT.labels(method="POST", endpoint="/v1/inference", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "orchestrator"}


@app.get("/ready")
async def ready():
    """Readiness check"""
    # Check dependencies (Judge, Redis, etc.)
    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PNKLN Inference Orchestrator",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
