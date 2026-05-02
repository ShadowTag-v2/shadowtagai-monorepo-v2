# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""JudgeSixClassifyKernel — kernel wrapper for the Judge 6 pipeline."""

from __future__ import annotations

from typing import Any

from app.kernels.base import Kernel


class JudgeSixClassifyKernel(Kernel):
    """Kernel that wraps Judge 6 classification for chain orchestration."""

    name = "judge_six_classify"

    async def execute(self, context: Any) -> Any:
        """Execute Judge 6 classification on the decision context.

        Args:
            context: DecisionContext or dict with input payload.

        Returns:
            Updated context with classification results.
        """
        # Delegate to the pipeline for actual validation
        from pnkln.core.judge_six_pipeline import JudgeSixPipeline

        pipeline = JudgeSixPipeline()
        text = ""
        if hasattr(context, "raw_input"):
            text = context.raw_input
        elif isinstance(context, dict):
            text = context.get("text", "")

        result = await pipeline.validate(
            request={"text": text},
            request_id=getattr(context, "request_id", "kernel_run"),
        )

        if hasattr(context, "classification"):
            context.classification = {
                "decision": result.decision,
                "confidence": result.confidence,
                "risk_level": str(result.risk_level),
            }

        return context


__all__ = ["JudgeSixClassifyKernel"]
