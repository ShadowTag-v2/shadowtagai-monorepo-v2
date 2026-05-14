# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Core kernel chain orchestration."""

import time
import uuid
from typing import Any

from app.config import settings
from app.kernels.base import Kernel, KernelChainError
from app.models.decision import (
    AuditTrail,
    DecisionContext,
    DecisionResult,
    JudgeSixClassification,
    ViolationsScanOutput,
)
from app.models.kernel import KernelInput, KernelOutput


class KernelChain:
    """
    Sequential kernel chain orchestrator.

    Implements Pattern A: Synchronous Chain
    - Kernels execute in sequence
    - Output of kernel_n becomes input of kernel_n+1
    - Fail fast on errors or confidence threshold violations
    - Full audit trail maintained
    """

    def __init__(self, kernels: list[Kernel]):
        """
        Initialize chain with ordered kernels.

        Args:
            kernels: List of kernels in execution order
        """
        self.kernels = kernels
        self.kernel_names = [k.name for k in kernels]

    async def execute(
        self,
        initial_input: Any,
        trace_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[KernelOutput]:
        """
        Execute the full kernel chain.

        Args:
            initial_input: Initial input data (DecisionContext)
            trace_id: Optional trace ID for tracking
            metadata: Optional metadata to pass through chain

        Returns:
            List of KernelOutputs from each kernel

        Raises:
            KernelChainError: If any kernel fails or violates constraints
        """
        trace_id = trace_id or str(uuid.uuid4())
        metadata = metadata or {}

        outputs: list[KernelOutput] = []
        current_input = KernelInput(
            data=initial_input,
            metadata=metadata,
            trace_id=trace_id,
        )

        for kernel in self.kernels:
            # Execute kernel
            output = await kernel(current_input)
            outputs.append(output)

            # Check success
            if not output.success:
                raise KernelChainError(f"Kernel {kernel.name} failed: {output.error}")

            # Check confidence threshold (if applicable)
            if output.metrics and output.metrics.confidence is not None:
                if output.metrics.confidence < settings.confidence_threshold:
                    raise KernelChainError(
                        f"Kernel {kernel.name} confidence {output.metrics.confidence:.2%} below threshold {settings.confidence_threshold:.2%}"
                    )

            # Prepare input for next kernel (feed forward)
            current_input = KernelInput(
                data=output.data,
                metadata={**metadata, **output.metadata},
                trace_id=trace_id,
            )

        return outputs


class ChainExecutor:
    """
    High-level executor for the SHADOWTAGAI kernel chain.

    Orchestrates the 3-kernel decision pipeline:
    1. ATP519ScanKernel: Extract violations
    2. JudgeSixClassifyKernel: Binary classification
    3. AuditCompressKernel: Compress audit trail
    """

    def __init__(self, chain: KernelChain):
        self.chain = chain

    async def execute_decision(
        self,
        decision_context: DecisionContext,
    ) -> DecisionResult:
        """
        Execute full decision pipeline and return structured result.

        Args:
            decision_context: Raw decision context to evaluate

        Returns:
            DecisionResult with full audit trail and metrics

        Raises:
            KernelChainError: If chain execution fails
        """
        start_time = time.perf_counter()

        try:
            # Execute kernel chain
            outputs = await self.chain.execute(
                initial_input=decision_context,
                trace_id=decision_context.trace_id,
                metadata=decision_context.metadata,
            )

            # Extract outputs from each kernel
            violations_output: ViolationsScanOutput = outputs[0].data
            classification: JudgeSixClassification = outputs[1].data
            audit_trail: AuditTrail = outputs[2].data

            # Calculate total metrics
            total_latency_ms = (time.perf_counter() - start_time) * 1000
            total_cost_usd = sum(o.metrics.cost_usd for o in outputs if o.metrics and o.metrics.cost_usd)

            # Check SLA compliance
            if total_latency_ms > settings.max_latency_p99_ms:
                raise KernelChainError(f"Chain exceeded p99 latency SLA: {total_latency_ms:.2f}ms > {settings.max_latency_p99_ms}ms")

            if total_cost_usd > settings.max_cost_per_decision:
                raise KernelChainError(f"Chain exceeded cost SLA: ${total_cost_usd:.6f} > ${settings.max_cost_per_decision}")

            # Build kernel metrics summary
            kernel_metrics = {
                output.kernel_name: {
                    "latency_ms": output.metrics.latency_ms,
                    "cost_usd": output.metrics.cost_usd,
                    "token_count_input": output.metrics.token_count_input,
                    "token_count_output": output.metrics.token_count_output,
                }
                for output in outputs
                if output.metrics
            }

            # Create final decision result
            result = DecisionResult(
                decision=classification.decision,
                confidence=classification.confidence,
                risk_tier=classification.risk_tier,
                violations=violations_output.violations,
                audit_trail=audit_trail,
                total_latency_ms=total_latency_ms,
                total_cost_usd=total_cost_usd,
                trace_id=decision_context.trace_id or outputs[0].trace_id,
                kernel_metrics=kernel_metrics,
            )

            return result

        except KernelChainError:
            raise
        except Exception as e:
            total_latency_ms = (time.perf_counter() - start_time) * 1000
            raise KernelChainError(f"Chain execution failed after {total_latency_ms:.2f}ms: {str(e)}") from e
