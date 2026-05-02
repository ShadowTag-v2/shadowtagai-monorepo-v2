# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Judge 6 validation pipeline — p99≤90ms SLA.

Implements the hybrid validation pipeline that combines deterministic
JR Engine scans with optional Gemini semantic checks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from shadowtagai.core.jr_engine import JREngine, RiskLevel


@dataclass
class ValidationResult:
    """Result of a Judge 6 validation pass."""

    decision: str = "APPROVE"
    confidence: float = 0.95
    risk_level: RiskLevel = RiskLevel.LOW
    latency_ms: float = 0.0
    stage_latencies: dict[str, float] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def meets_sla(self, sla_ms: float = 90.0) -> bool:
        """Check if this result meets the target SLA."""
        return self.latency_ms <= sla_ms


class JudgeSixPipeline:
    """Hybrid validation pipeline.

    Stage 1: Deterministic JR Engine scan (<500μs)
    Stage 2: Optional Gemini semantic check (only for ambiguous cases)
    """

    def __init__(self) -> None:
        self._jr_engine = JREngine()

    async def validate(
        self,
        request: dict[str, Any],
        request_id: str,
    ) -> ValidationResult:
        """Run the validation pipeline.

        Args:
            request: Input payload containing 'text' key.
            request_id: Correlation ID for tracing.

        Returns:
            ValidationResult with decision, confidence and latency data.
        """
        start = time.perf_counter()
        text = request.get("text", "")

        # Stage 1: JR Engine deterministic scan
        jr_start = time.perf_counter()
        jr_decision = self._jr_engine.quick_scan({"text": text})
        jr_ms = (time.perf_counter() - jr_start) * 1000

        stage_latencies: dict[str, float] = {"jr_engine_scan": jr_ms}

        # Fast-path: deterministic result with high confidence
        risk_level = jr_decision.risk_level
        fast_path = risk_level == RiskLevel.LOW

        if not fast_path:
            # Stage 2: Gemini semantic check (simulated)
            gemini_start = time.perf_counter()
            # In production this calls the Gemini API
            gemini_ms = (time.perf_counter() - gemini_start) * 1000
            stage_latencies["gemini_semantic_check"] = gemini_ms

        total_ms = (time.perf_counter() - start) * 1000

        decision = "APPROVE"
        confidence = 0.95
        reasons: list[str] = []

        if risk_level in (RiskLevel.EXTREMELY_HIGH, RiskLevel.HIGH):
            decision = "REJECT"
            confidence = 0.90
            reasons.append("High risk content detected by JR Engine")
        elif risk_level == RiskLevel.MODERATE:
            decision = "ESCALATE"
            confidence = 0.75
            reasons.append("Ambiguous content requires human review")

        return ValidationResult(
            decision=decision,
            confidence=confidence,
            risk_level=risk_level,
            latency_ms=total_ms,
            stage_latencies=stage_latencies,
            reasons=reasons,
            metadata={
                "request_id": request_id,
                "fast_path": fast_path,
            },
        )


__all__ = ["JudgeSixPipeline", "ValidationResult"]
