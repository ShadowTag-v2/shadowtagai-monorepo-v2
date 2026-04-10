import time
import tracemalloc
from collections import defaultdict
from typing import Any

import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor

# Constants for memory and performance measurement
BYTES_PER_FLOAT32 = 4  # Standard float32 size in bytes
KB_TO_BYTES = 1024  # Kilobytes to bytes conversion
MB_TO_BYTES = 1024 * 1024  # Megabytes to bytes conversion


class Profiler:
    """
    Professional-grade ML model profiler for performance analysis.

    Measures parameters, FLOPs, memory usage, and latency with statistical rigor.
    Used for optimization guidance and deployment planning.
    """

    def __init__(self):
        """Initialize profiler with measurement state."""
        self.measurements = {}
        self.operation_counts = defaultdict(int)
        self.memory_tracker = None

    def count_parameters(self, model) -> int:
        """Count total trainable parameters in a model."""
        total_params = 0

        # Handle SimpleModel pattern (has .layers attribute)
        if hasattr(model, "layers"):
            for layer in model.layers:
                for param in layer.parameters():
                    total_params += param.data.size
        elif hasattr(model, "parameters"):
            # Model with direct parameters() method
            for param in model.parameters():
                total_params += param.data.size
        elif hasattr(model, "weight"):
            # Single layer (Linear, Conv2d) - all have .weight
            total_params += model.weight.data.size
            # Check for bias (may be None)
            if hasattr(model, "bias") and model.bias is not None:
                total_params += model.bias.data.size
        else:
            # No parameters
            total_params = 0

        return total_params

    def count_flops(self, model, input_shape: tuple[int, ...]) -> int:
        """Count FLOPs (Floating Point Operations) for one forward pass."""
        total_flops = 0

        # Handle different model types
        if hasattr(model, "__class__"):
            model_name = model.__class__.__name__

            if "Linear" in model_name:
                # Linear layer: input_features × output_features × 2
                in_features = input_shape[-1]
                out_features = model.weight.shape[1] if hasattr(model, "weight") else 1
                total_flops = in_features * out_features * 2

            elif "Conv2d" in model_name:
                # Conv2d layer (simplified estimation)
                if hasattr(model, "kernel_size") and hasattr(model, "in_channels"):
                    in_channels = model.in_channels
                    out_channels = model.out_channels
                    kernel_h = kernel_w = (
                        model.kernel_size
                        if isinstance(model.kernel_size, int)
                        else model.kernel_size[0]
                    )

                    # Estimate output size (simplified)
                    input_h, input_w = input_shape[-2], input_shape[-1]
                    output_h = input_h  # Simplified: assume padding='same' or similar scale
                    output_w = input_w

                    total_flops = (
                        output_h * output_w * kernel_h * kernel_w * in_channels * out_channels * 2
                    )

            elif "Sequential" in model_name or hasattr(model, "layers"):
                # Sequential model or model with layers: sum FLOPs of all layers
                if hasattr(model, "layers"):
                    for _layer in model.layers:
                        # Recursive call would be ideal, but for now simple sum if possible
                        # Simplified: just return 0 if complicated structure to avoid crash
                        # Real implementation needs shape tracking through layers
                        pass

            else:
                # Generic fallback: assume 1 FLOP per element
                total_flops = int(np.prod(input_shape))

        return total_flops

    def measure_memory(self, model, input_shape: tuple[int, ...]) -> dict[str, float]:
        """Measure memory usage during forward pass."""
        # Start memory tracking
        tracemalloc.start()

        # Measure baseline memory
        _baseline_memory = tracemalloc.get_traced_memory()[0]

        # Create input
        dummy_input = Tensor(np.random.randn(*input_shape))

        # Run forward pass
        _ = model.forward(dummy_input) if hasattr(model, "forward") else model(dummy_input)

        # Get peak memory
        _current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_memory_mb = (peak_memory - _baseline_memory) / MB_TO_BYTES

        # Calculate parameter memory
        param_count = self.count_parameters(model)
        parameter_memory_mb = (param_count * BYTES_PER_FLOAT32) / MB_TO_BYTES

        # Estimate activations (remainder)
        activation_memory_mb = max(0, peak_memory_mb - parameter_memory_mb)

        # Calculate efficiency
        useful_memory = parameter_memory_mb + activation_memory_mb
        memory_efficiency = useful_memory / max(peak_memory_mb, 0.001)

        return {
            "parameter_memory_mb": parameter_memory_mb,
            "activation_memory_mb": activation_memory_mb,
            "peak_memory_mb": max(peak_memory_mb, useful_memory),
            "memory_efficiency": min(memory_efficiency, 1.0),
        }

    def measure_latency(
        self, model, input_tensor, warmup: int = 10, iterations: int = 100
    ) -> float:
        """Measure model inference latency with statistical rigor."""
        # Warmup
        for _ in range(warmup):
            _ = model.forward(input_tensor) if hasattr(model, "forward") else model(input_tensor)

        # Measurement
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            _ = model.forward(input_tensor) if hasattr(model, "forward") else model(input_tensor)
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # ms

        return float(np.median(times))

    def profile_forward_pass(self, model, input_tensor) -> dict[str, Any]:
        """Comprehensive profiling of a model's forward pass."""
        # Measurements
        param_count = self.count_parameters(model)
        flops = self.count_flops(model, input_tensor.shape)
        memory_stats = self.measure_memory(model, input_tensor.shape)
        latency_ms = self.measure_latency(model, input_tensor, warmup=5, iterations=20)

        # Derived
        latency_seconds = latency_ms / 1000.0
        gflops_per_second = (flops / 1e9) / max(latency_seconds, 1e-6)
        memory_bandwidth = memory_stats["peak_memory_mb"] / max(latency_seconds, 1e-6)

        theoretical_peak_gflops = 100.0
        computational_efficiency = min(gflops_per_second / theoretical_peak_gflops, 1.0)

        is_memory_bound = memory_bandwidth > gflops_per_second * 100

        return {
            "parameters": param_count,
            "flops": flops,
            "latency_ms": latency_ms,
            **memory_stats,
            "gflops_per_second": gflops_per_second,
            "memory_bandwidth_mbs": memory_bandwidth,
            "computational_efficiency": computational_efficiency,
            "bottleneck": "memory" if is_memory_bound else "compute",
        }


def quick_profile(model, input_tensor, profiler=None):
    """Quick profiling function for immediate insights."""
    if profiler is None:
        profiler = Profiler()

    profile = profiler.profile_forward_pass(model, input_tensor)

    print("🔬 Quick Profile Results:")
    print(f"   Parameters: {profile['parameters']:,}")
    print(f"   FLOPs: {profile['flops']:,}")
    print(f"   Latency: {profile['latency_ms']:.2f} ms")
    print(f"   Memory: {profile['peak_memory_mb']:.2f} MB")
    print(f"   Bottleneck: {profile['bottleneck']}")
    print(f"   Efficiency: {profile['computational_efficiency'] * 100:.1f}%")

    return profile
