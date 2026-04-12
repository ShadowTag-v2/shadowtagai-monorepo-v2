"""Model registry for managing multiple LLM models."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model loading status."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


@dataclass
class ModelMetrics:
    """Metrics for a loaded model."""

    total_requests: int = 0
    active_requests: int = 0
    total_tokens: int = 0
    active_tokens: int = 0
    avg_latency_ms: float = 0.0
    last_request_time: datetime | None = None
    error_count: int = 0

    # GPU metrics
    gpu_memory_used: float = 0.0  # GB
    gpu_utilization: float = 0.0  # 0-1


@dataclass
class RegisteredModel:
    """Registered model with metadata."""

    name: str
    model_path: str
    status: ModelStatus = ModelStatus.UNLOADED
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    backend: any | None = None  # vLLM engine instance
    gpu_id: int | None = None
    load_time: datetime | None = None
    error_message: str | None = None


class ModelRegistry:
    """
    Central registry for managing multiple LLM models.

    Inspired by Alibaba's Aegaeon, this registry handles:
    - Model lifecycle (load/unload)
    - Multi-model GPU pooling
    - Request routing based on load
    """

    def __init__(self, max_models_per_gpu: int = 7):
        self.models: dict[str, RegisteredModel] = {}
        self.max_models_per_gpu = max_models_per_gpu
        self._lock = asyncio.Lock()

    async def register_model(
        self,
        name: str,
        model_path: str,
        config: dict = None,
    ) -> RegisteredModel:
        """Register a new model in the registry."""
        async with self._lock:
            if name in self.models:
                logger.warning(f"Model {name} already registered, updating config")

            model = RegisteredModel(
                name=name,
                model_path=model_path,
                status=ModelStatus.UNLOADED,
            )

            self.models[name] = model
            logger.info(f"Registered model: {name} at {model_path}")
            return model

    async def unregister_model(self, name: str) -> bool:
        """Unregister a model from the registry."""
        async with self._lock:
            if name not in self.models:
                logger.warning(f"Model {name} not found in registry")
                return False

            model = self.models[name]
            if model.status == ModelStatus.READY and model.backend:
                # Cleanup backend resources
                logger.info(f"Unloading model {name} before unregistering")
                # Backend cleanup would happen here

            del self.models[name]
            logger.info(f"Unregistered model: {name}")
            return True

    async def mark_ready(self, name: str, backend: any, gpu_id: int = None):
        """Mark a model as ready after successful loading."""
        async with self._lock:
            if name not in self.models:
                raise ValueError(f"Model {name} not registered")

            model = self.models[name]
            model.status = ModelStatus.READY
            model.backend = backend
            model.gpu_id = gpu_id
            model.load_time = datetime.now()
            logger.info(f"Model {name} is now READY on GPU {gpu_id}")

    async def mark_error(self, name: str, error: str):
        """Mark a model as having an error."""
        async with self._lock:
            if name not in self.models:
                return

            model = self.models[name]
            model.status = ModelStatus.ERROR
            model.error_message = error
            model.metrics.error_count += 1
            logger.error(f"Model {name} error: {error}")

    def get_model(self, name: str) -> RegisteredModel | None:
        """Get a model by name."""
        return self.models.get(name)

    def list_models(self, status: ModelStatus | None = None) -> list[RegisteredModel]:
        """List all models, optionally filtered by status."""
        if status:
            return [m for m in self.models.values() if m.status == status]
        return list(self.models.values())

    def get_ready_models(self) -> list[RegisteredModel]:
        """Get all models that are ready to serve."""
        return self.list_models(ModelStatus.READY)

    async def update_metrics(
        self,
        name: str,
        tokens: int = 0,
        latency_ms: float = 0,
        active_change: int = 0,
    ):
        """Update model metrics."""
        model = self.get_model(name)
        if not model:
            return

        metrics = model.metrics
        metrics.total_requests += 1 if active_change > 0 else 0
        metrics.active_requests = max(0, metrics.active_requests + active_change)
        metrics.total_tokens += tokens
        metrics.active_tokens = max(
            0, metrics.active_tokens + (tokens if active_change > 0 else -tokens)
        )
        metrics.last_request_time = datetime.now()

        # Update rolling average latency
        if latency_ms > 0:
            if metrics.avg_latency_ms == 0:
                metrics.avg_latency_ms = latency_ms
            else:
                # Exponential moving average
                alpha = 0.1
                metrics.avg_latency_ms = alpha * latency_ms + (1 - alpha) * metrics.avg_latency_ms

    def get_least_loaded_model(self) -> RegisteredModel | None:
        """Get the model with the least active requests."""
        ready_models = self.get_ready_models()
        if not ready_models:
            return None

        return min(ready_models, key=lambda m: m.metrics.active_requests)

    def get_total_gpu_utilization(self) -> float:
        """Calculate average GPU utilization across all models."""
        ready_models = self.get_ready_models()
        if not ready_models:
            return 0.0

        total_util = sum(m.metrics.gpu_utilization for m in ready_models)
        return total_util / len(ready_models)

    def get_stats(self) -> dict:
        """Get overall registry statistics."""
        ready_models = self.get_ready_models()

        return {
            "total_models": len(self.models),
            "ready_models": len(ready_models),
            "total_requests": sum(m.metrics.total_requests for m in self.models.values()),
            "active_requests": sum(m.metrics.active_requests for m in self.models.values()),
            "total_tokens_processed": sum(m.metrics.total_tokens for m in self.models.values()),
            "avg_gpu_utilization": self.get_total_gpu_utilization(),
            "models": {
                name: {
                    "status": model.status.value,
                    "active_requests": model.metrics.active_requests,
                    "total_requests": model.metrics.total_requests,
                    "avg_latency_ms": model.metrics.avg_latency_ms,
                    "gpu_id": model.gpu_id,
                }
                for name, model in self.models.items()
            },
        }
