# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JudgeAdapter — Bridges the CoreOrchestrator to the src/judges HITL system.

Wraps JudgeFactory and the four judge verticals (FinJudge, CaseJudge,
LawJudge, FraudJudge) into an async adapter that the orchestrator can
invoke via ``review(payload)`` for JUDGE_REVIEW operations.

All high-risk operations flow through this adapter before execution,
enforcing binary ALLOW/BLOCK decisions with ATP 5-19 risk assessment.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class JudgeAdapter:
    """
    Async adapter wrapping the synchronous JudgeFactory/BaseJudge system.

    The existing ``src/judges`` uses synchronous ``BaseJudge.judge()`` calls.
    This adapter:
    1. Accepts a dict payload from the orchestrator
    2. Marshals it into a JudgeRequest
    3. Routes to the correct judge vertical via JudgeFactory
    4. Executes the synchronous judge in a thread executor
    5. Returns a structured dict result

    Security: HITL enforcement is mandatory for all operations routed
    through OperationType.JUDGE_REVIEW.
    """

    def __init__(self, judge_factory: Any | None = None):
        """
        Initialize the judge adapter.

        Args:
            judge_factory: An instance or class with a ``get_judge(type)`` method.
                           If None, will attempt to import from src/judges.
        """
        self._factory = judge_factory
        self._review_count = 0

    def _get_factory(self) -> Any:
        """Lazy-load the JudgeFactory if not provided."""
        if self._factory is None:
            try:
                from src.judges import JudgeFactory

                self._factory = JudgeFactory
            except ImportError:
                raise RuntimeError("JudgeFactory not available. Ensure src/judges is on the Python path.")
        return self._factory

    async def review(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Submit an operation for HITL judge review.

        Args:
            payload: Must contain:
                - judge_type: str ("FinJudge", "CaseJudge", "LawJudge", "FraudJudge")
                - request_id: str
                - action_type: str
                - context: dict
                - requested_by: str
                Optional:
                - urgency: str (default: "normal")

        Returns:
            Dict with decision, risk_assessment, approval_gate, reasoning,
            semantic_trail, latency_ms, and next_steps.
        """
        start = time.perf_counter()
        self._review_count += 1

        judge_type_str = payload.get("judge_type", "")
        request_id = payload.get("request_id", f"req-{self._review_count}")
        action_type = payload.get("action_type", "unknown")
        context = payload.get("context", {})
        urgency = payload.get("urgency", "normal")
        requested_by = payload.get("requested_by", "system")

        logger.info(
            "judge_adapter.review",
            judge_type=judge_type_str,
            request_id=request_id,
            action_type=action_type,
        )

        try:
            # Import models and build request.
            from src.judges.models import JudgeRequest, JudgeType

            # Resolve judge type.
            judge_type = JudgeType(judge_type_str)

            # Build the JudgeRequest.
            request = JudgeRequest(
                request_id=request_id,
                judge_type=judge_type,
                action_type=action_type,
                context=context,
                urgency=urgency,
                requested_by=requested_by,
            )

            # Get the judge instance.
            factory = self._get_factory()
            judge = factory.get_judge(judge_type)

            # Execute synchronous judge in executor.
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, judge.judge, request)

            latency_ms = (time.perf_counter() - start) * 1000

            return {
                "decision": response.decision.value,
                "risk_assessment": {
                    "risk_level": response.risk_assessment.risk_level.value,
                    "probability": response.risk_assessment.probability.value,
                    "severity": response.risk_assessment.severity.value,
                    "requires_approval": response.risk_assessment.requires_approval,
                    "approval_authority": response.risk_assessment.approval_authority,
                },
                "approval_gate": response.approval_gate.value,
                "reasoning": response.reasoning,
                "semantic_trail": response.semantic_trail,
                "latency_ms": latency_ms,
                "judge_type": response.judge_type.value,
                "next_steps": response.next_steps,
                "metadata": response.metadata,
            }

        except (ImportError, ValueError) as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "judge_adapter.error",
                error=str(e),
                judge_type=judge_type_str,
            )
            return {
                "decision": "BLOCK",
                "error": str(e),
                "latency_ms": latency_ms,
                "reasoning": f"Judge adapter error: {e}",
            }

    @property
    def review_count(self) -> int:
        """Total reviews performed since init."""
        return self._review_count
