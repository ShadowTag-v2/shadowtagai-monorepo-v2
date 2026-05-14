# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Alternative orchestration patterns (for future expansion)."""

import asyncio
from collections.abc import Callable
from typing import Any

from app.kernels.base import Kernel, KernelChainError
from app.models.kernel import KernelInput, KernelOutput


class SynchronousChain:
    """
    Pattern A: Synchronous Chain (currently implemented in KernelChain).

    for kernel in kernel_chain:
      output = kernel(input)
      input = output  # feed forward
      if output.confidence < 0.85:
        return fallback_decision()
    """

    @staticmethod
    async def execute(kernels: list[Kernel], initial_input: KernelInput) -> list[KernelOutput]:
        """Execute kernels sequentially with feed-forward."""
        outputs = []
        current_input = initial_input

        for kernel in kernels:
            output = await kernel(current_input)
            outputs.append(output)

            if not output.success:
                raise KernelChainError(f"Kernel {kernel.name} failed")

            # Feed forward
            current_input = KernelInput(
                data=output.data,
                metadata=current_input.metadata,
                trace_id=current_input.trace_id,
            )

        return outputs


class ParallelMergeChain:
    """
    Pattern B: Parallel + Merge (when kernels are independent).

    results = parallel_map(kernels, input)
    merged = reduce(results)  # consensus or voting
    """

    @staticmethod
    async def execute(
        kernels: list[Kernel],
        input_data: KernelInput,
        merge_fn: Callable[[list[KernelOutput]], Any],
    ) -> Any:
        """
        Execute kernels in parallel and merge results.

        Args:
            kernels: List of independent kernels
            input_data: Shared input for all kernels
            merge_fn: Function to merge outputs (e.g., voting, consensus)

        Returns:
            Merged result
        """
        # Execute all kernels concurrently
        tasks = [kernel(input_data) for kernel in kernels]
        outputs = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        errors = [o for o in outputs if isinstance(o, Exception)]
        if errors:
            raise KernelChainError(f"Parallel execution failed: {errors[0]}")

        # Merge results
        valid_outputs = [o for o in outputs if isinstance(o, KernelOutput)]
        return merge_fn(valid_outputs)


class ConditionalBranchChain:
    """
    Pattern C: Conditional Branch.

    output = kernel_1(input)
    if output.risk_tier > 3:
      kernel_2b(output)  # escalation path
    else:
      kernel_2a(output)  # fast path
    """

    @staticmethod
    async def execute(
        initial_kernel: Kernel,
        condition_fn: Callable[[KernelOutput], bool],
        true_branch: list[Kernel],
        false_branch: list[Kernel],
        input_data: KernelInput,
    ) -> list[KernelOutput]:
        """
        Execute initial kernel, then branch based on condition.

        Args:
            initial_kernel: First kernel to execute
            condition_fn: Function to determine branch (returns True/False)
            true_branch: Kernels to execute if condition is True
            false_branch: Kernels to execute if condition is False
            input_data: Initial input

        Returns:
            List of outputs from executed path
        """
        # Execute initial kernel
        initial_output = await initial_kernel(input_data)
        outputs = [initial_output]

        # Determine branch
        take_true_branch = condition_fn(initial_output)
        branch_kernels = true_branch if take_true_branch else false_branch

        # Execute branch
        current_input = KernelInput(
            data=initial_output.data,
            metadata=input_data.metadata,
            trace_id=input_data.trace_id,
        )

        for kernel in branch_kernels:
            output = await kernel(current_input)
            outputs.append(output)

            current_input = KernelInput(
                data=output.data,
                metadata=current_input.metadata,
                trace_id=current_input.trace_id,
            )

        return outputs
