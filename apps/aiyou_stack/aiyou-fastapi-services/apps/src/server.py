"""Main FastAPI server for multi-model LLM serving.

Implements Aegaeon-inspired architecture:
- Token-level auto-scaling
- Multi-model GPU pooling (7+ models/GPU)
- vLLM for 2-4x throughput
- Ray Serve for distributed orchestration
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from .config import ModelConfig, get_settings
from .models import GPUPool, ModelRegistry, TokenLevelRouter
from .monitoring import MetricsCollector, setup_logging
from .serving import RayOrchestrator, VLLMBackend

# Initialize logging
settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Global instances
registry = ModelRegistry(max_models_per_gpu=settings.pooling.max_models_per_gpu)
router = TokenLevelRouter(
    registry=registry,
    token_budget_per_gpu=settings.pooling.token_budget_per_gpu,
    enable_preemption=settings.pooling.preemption_mode != "none",
)
gpu_pool = GPUPool(
    registry=registry,
    max_models_per_gpu=settings.pooling.max_models_per_gpu,
    auto_scale=settings.pooling.enable_auto_scaling,
    scale_up_threshold=settings.pooling.scale_up_threshold,
    scale_down_threshold=settings.pooling.scale_down_threshold,
)
ray_orchestrator = RayOrchestrator(
    ray_address=settings.ray_address,
    namespace=settings.ray_namespace,
)
metrics = MetricsCollector() if settings.enable_metrics else None


# Request/Response models
class CompletionRequest(BaseModel):
    """Request for text completion."""

    prompt: str = Field(..., description="Input prompt for the model")
    model: str | None = Field(None, description="Specific model to use (optional)")
    max_tokens: int = Field(512, ge=1, le=32000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling probability")
    stream: bool = Field(False, description="Enable streaming response")
    stop: list[str] | None = Field(None, description="Stop sequences")
    routing_strategy: str = Field(
        "token_aware",
        description="Routing strategy: least_loaded, round_robin, token_aware",
    )


class CompletionResponse(BaseModel):
    """Response from text completion."""

    text: str
    model: str
    tokens: int
    finish_reason: str
    latency_ms: float
    routing: dict


class ModelInfo(BaseModel):
    """Model information."""

    name: str
    status: str
    total_requests: int
    active_requests: int
    avg_latency_ms: float
    gpu_id: int | None


# Startup/Shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting ShadowTag-v2 FastAPI Services")

    # Start GPU pool
    await gpu_pool.start()

    # Initialize Ray (optional)
    if settings.ray_address:
        try:
            await ray_orchestrator.initialize()
        except Exception as e:
            logger.warning(f"Ray initialization failed: {e}, continuing without Ray")

    # Load configured models
    logger.info(f"Loading {len(settings.models)} model(s)...")
    load_tasks = []

    for model_name, model_config in settings.models.items():
        load_tasks.append(load_model_async(model_name, model_config))

    # Load models concurrently
    results = await asyncio.gather(*load_tasks, return_exceptions=True)

    loaded_count = sum(1 for r in results if not isinstance(r, Exception))
    logger.info(f"✓ Loaded {loaded_count}/{len(settings.models)} models")

    if metrics:
        metrics.update_model_count(loaded_count)

    logger.info(f"✅ Server ready on http://{settings.host}:{settings.port}")
    logger.info(f"📊 Metrics available on http://{settings.host}:{settings.metrics_port}/metrics")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await gpu_pool.stop()
    await ray_orchestrator.shutdown()


async def load_model_async(model_name: str, model_config: ModelConfig):
    """Load a model asynchronously."""
    try:
        # Register model
        await registry.register_model(
            name=model_name,
            model_path=model_config.model_path,
        )

        # Determine GPU placement
        # Estimate memory requirement (simplified)
        # In production, use actual model size
        estimated_memory_gb = 4.0  # Default estimate

        gpu_id = gpu_pool.get_best_gpu_for_model(model_name, estimated_memory_gb)

        # Create vLLM backend
        backend = VLLMBackend(
            model_name=model_name,
            model_path=model_config.model_path,
            gpu_id=gpu_id,
            max_model_len=model_config.max_model_len,
            gpu_memory_utilization=model_config.gpu_memory_utilization,
            tensor_parallel_size=model_config.tensor_parallel_size,
            enable_prefix_caching=model_config.enable_prefix_caching,
            enable_chunked_prefill=model_config.enable_chunked_prefill,
            trust_remote_code=model_config.trust_remote_code,
            dtype=model_config.dtype,
        )

        # Load backend
        await backend.load()

        # Allocate GPU resources
        await gpu_pool.allocate_model(model_name, gpu_id, estimated_memory_gb)

        # Mark as ready
        await registry.mark_ready(model_name, backend, gpu_id)

        logger.info(f"✓ Loaded {model_name} on GPU {gpu_id}")

    except Exception as e:
        logger.error(f"✗ Failed to load {model_name}: {e}")
        await registry.mark_error(model_name, str(e))
        raise


# Create app
app = FastAPI(
    title="ShadowTag-v2 FastAPI Services",
    description="Multi-model LLM serving with Aegaeon-inspired GPU pooling",
    version="0.1.0",
    lifespan=lifespan,
)


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ShadowTag-v2 FastAPI Services",
        "version": "0.1.0",
        "status": "running",
        "models": len(registry.get_ready_models()),
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    ready_models = registry.get_ready_models()

    return {
        "status": "healthy" if ready_models else "degraded",
        "models_ready": len(ready_models),
        "models_total": len(registry.models),
    }


@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Create a text completion.

    This endpoint implements Aegaeon-style token-level routing across multiple models.
    """
    start_time = time.time()

    try:
        # Route request
        decision = await router.route_request(
            prompt=request.prompt,
            model_name=request.model,
            max_tokens=request.max_tokens,
            strategy=request.routing_strategy,
        )

        logger.info(f"Routing to {decision.model_name}: {decision.reason}")

        # Allocate tokens
        await router.allocate_tokens(decision)

        # Get model backend
        model = registry.get_model(decision.model_name)
        if not model or not model.backend:
            raise HTTPException(
                status_code=503,
                detail=f"Model {decision.model_name} not available",
            )

        # Update metrics
        await registry.update_metrics(decision.model_name, active_change=1)
        if metrics:
            metrics.update_active_requests(
                decision.model_name,
                model.metrics.active_requests,
            )
            metrics.record_routing(request.routing_strategy, decision.model_name)

        # Generate
        from .serving.vllm_backend import GenerationRequest

        gen_request = GenerationRequest(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=request.stream,
            stop=request.stop,
        )

        response = await model.backend.generate(gen_request)

        # Release tokens
        await router.release_tokens(decision)

        # Update metrics
        await registry.update_metrics(
            decision.model_name,
            tokens=response.tokens,
            latency_ms=response.latency_ms,
            active_change=-1,
        )

        if metrics:
            metrics.record_request(
                model=decision.model_name,
                duration_seconds=(time.time() - start_time),
                tokens=response.tokens,
                status="success",
            )
            metrics.update_active_requests(
                decision.model_name,
                model.metrics.active_requests,
            )

        return CompletionResponse(
            text=response.text,
            model=decision.model_name,
            tokens=response.tokens,
            finish_reason=response.finish_reason,
            latency_ms=response.latency_ms,
            routing={
                "strategy": request.routing_strategy,
                "reason": decision.reason,
                "gpu_id": decision.gpu_id,
            },
        )

    except Exception as e:
        logger.error(f"Completion error: {e}")

        if metrics:
            metrics.requests_total.labels(
                model=request.model or "unknown",
                status="error",
            ).inc()

        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/models")
async def list_models():
    """List all available models."""
    models = []

    for model in registry.models.values():
        models.append(
            ModelInfo(
                name=model.name,
                status=model.status.value,
                total_requests=model.metrics.total_requests,
                active_requests=model.metrics.active_requests,
                avg_latency_ms=model.metrics.avg_latency_ms,
                gpu_id=model.gpu_id,
            ),
        )

    return {"models": models}


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "registry": registry.get_stats(),
        "gpu_pool": gpu_pool.get_pool_stats(),
        "routing": router.get_routing_stats(),
        "ray": ray_orchestrator.get_cluster_info() if ray_orchestrator.is_initialized() else None,
    }


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    if not metrics:
        return Response(content="Metrics disabled", media_type="text/plain")

    return Response(content=metrics.get_metrics(), media_type="text/plain")


# For running directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
