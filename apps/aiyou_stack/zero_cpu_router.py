"""
Zero CPU Router — Intelligent Workload Distribution
Routes workloads to minimize CPU usage by leveraging ANE/GPU accelerators.
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from .ane_bridge import HardwareTier, InferenceResult, detect_hardware, route_inference


@dataclass
class WorkloadMetrics:
    """Metrics for a workload execution."""
    total_requests: int = 0
    ane_requests: int = 0
    gpu_requests: int = 0
    cloud_requests: int = 0
    cpu_requests: int = 0
    total_latency_ms: float = 0.0
    errors: int = 0

    @property
    def avg_latency_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_latency_ms / self.total_requests

    @property
    def cpu_offload_ratio(self) -> float:
        """Ratio of requests offloaded from CPU (higher is better)."""
        if self.total_requests == 0:
            return 0.0
        offloaded = self.ane_requests + self.gpu_requests + self.cloud_requests
        return offloaded / self.total_requests


@dataclass
class ZeroCPURouter:
    """
    Routes inference workloads to minimize CPU usage.

    Strategy:
    1. Prefer ANE for small/medium models (< 2B params)
    2. Use GPU for large models
    3. Cloud fallback for models too large for local hardware
    4. CPU only as last resort
    """
    metrics: WorkloadMetrics = field(default_factory=WorkloadMetrics)
    _hardware_tier: Optional[HardwareTier] = field(default=None, init=False)

    def __post_init__(self):
        self._hardware_tier = detect_hardware()

    def route(
        self,
        model_name: str,
        input_data: dict,
        model_params_billions: float = 0.5,
    ) -> InferenceResult:
        """Route a workload to the optimal hardware tier."""
        start = time.monotonic()

        # Routing logic based on model size and available hardware
        if self._hardware_tier == HardwareTier.ANE and model_params_billions <= 2.0:
            preferred = HardwareTier.ANE
        elif self._hardware_tier in (HardwareTier.ANE, HardwareTier.GPU_LOCAL) and model_params_billions <= 7.0:
            preferred = HardwareTier.GPU_LOCAL
        elif model_params_billions > 7.0:
            preferred = HardwareTier.GPU_CLOUD
        else:
            preferred = self._hardware_tier or HardwareTier.CPU

        result = route_inference(model_name, input_data, preferred_tier=preferred)

        elapsed_ms = (time.monotonic() - start) * 1000
        result.latency_ms = elapsed_ms

        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.total_latency_ms += elapsed_ms

        if result.tier == HardwareTier.ANE:
            self.metrics.ane_requests += 1
        elif result.tier == HardwareTier.GPU_LOCAL:
            self.metrics.gpu_requests += 1
        elif result.tier == HardwareTier.GPU_CLOUD:
            self.metrics.cloud_requests += 1
        else:
            self.metrics.cpu_requests += 1

        if result.error:
            self.metrics.errors += 1

        return result

    def get_metrics(self) -> dict:
        """Return current routing metrics."""
        return {
            "total_requests": self.metrics.total_requests,
            "cpu_offload_ratio": f"{self.metrics.cpu_offload_ratio:.1%}",
            "avg_latency_ms": f"{self.metrics.avg_latency_ms:.2f}",
            "tier_distribution": {
                "ane": self.metrics.ane_requests,
                "gpu": self.metrics.gpu_requests,
                "cloud": self.metrics.cloud_requests,
                "cpu": self.metrics.cpu_requests,
            },
            "errors": self.metrics.errors,
        }


if __name__ == "__main__":
    router = ZeroCPURouter()

    # Simulate workloads
    for i in range(10):
        result = router.route(
            model_name=f"test-model-{i}",
            input_data={"prompt": f"test prompt {i}"},
            model_params_billions=0.5 if i < 7 else 13.0,
        )
        print(f"Request {i}: tier={result.tier.value}, latency={result.latency_ms:.2f}ms")

    import json
    print(f"\nMetrics: {json.dumps(router.get_metrics(), indent=2)}")
