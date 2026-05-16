# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Base kernel interface for the chain."""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any

from app.models.kernel import KernelInput, KernelMetrics, KernelOutput


class KernelChainError(Exception):
    """Base exception for kernel chain errors."""

    pass


class Kernel(ABC):
    """
    Base class for all kernels in the chain.

    Each kernel follows single responsibility principle:
    - Receives structured input
    - Performs one specific transformation
    - Returns structured output with metrics
    - Fails fast and isolates errors
    """

    def __init__(self, name: str, max_latency_ms: float | None = None):
        self.name = name
        self.max_latency_ms = max_latency_ms

    @abstractmethod
    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """
        Execute the kernel transformation.

        Args:
            kernel_input: Structured input data

        Returns:
            KernelOutput with transformed data and metrics

        Raises:
            KernelChainError: If execution fails
        """
        pass

    async def __call__(self, kernel_input: KernelInput) -> KernelOutput:
        """
        Execute kernel with timing and error handling.

        This wrapper provides:
        - Latency measurement
        - Input/output hashing for audit trail
        - Error isolation
        - Metrics collection
        """
        start_time = time.perf_counter()

        try:
            # Hash input for audit trail
            input_hash = self._hash_data(kernel_input.data)

            # Execute the kernel
            output = await self.execute(kernel_input)

            # Calculate metrics
            latency_ms = (time.perf_counter() - start_time) * 1000
            output_hash = self._hash_data(output.data)

            # Check latency SLA
            if self.max_latency_ms and latency_ms > self.max_latency_ms:
                raise KernelChainError(f"{self.name} exceeded max latency: {latency_ms:.2f}ms > {self.max_latency_ms}ms")

            # Attach metrics
            if not output.metrics:
                output.metrics = KernelMetrics(
                    latency_ms=latency_ms,
                    input_hash=input_hash,
                    output_hash=output_hash,
                )
            else:
                output.metrics.latency_ms = latency_ms
                output.metrics.input_hash = input_hash
                output.metrics.output_hash = output_hash

            output.kernel_name = self.name
            output.trace_id = kernel_input.trace_id

            return output

        except KernelChainError:
            raise
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            raise KernelChainError(f"{self.name} failed after {latency_ms:.2f}ms: {str(e)}") from e

    @staticmethod
    def _hash_data(data: Any) -> str:
        """Generate SHA256 hash of data for audit trail."""
        if isinstance(data, (str, bytes)):
            content = data if isinstance(data, bytes) else data.encode()
        else:
            content = json.dumps(data, sort_keys=True, default=str).encode()
        return hashlib.sha256(content).hexdigest()[:16]  # First 16 chars for compactness
