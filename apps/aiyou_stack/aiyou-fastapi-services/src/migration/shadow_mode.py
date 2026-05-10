"""Shadow Mode Framework for safe agent governance migration.

Runs new agent system in parallel with existing Judge 6 without
affecting production decisions, enabling validation before cutover.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from src.gov_config import settings


class AgreementLevel(StrEnum):
    """Agreement between shadow and production systems."""

    EXACT_MATCH = "exact_match"  # Same decision, same reasoning
    DECISION_MATCH = "decision_match"  # Same decision, different reasoning
    PARTIAL_MATCH = "partial_match"  # Similar confidence, different decision
    MISMATCH = "mismatch"  # Completely different


class ShadowDecision(BaseModel):
    """Decision from shadow agent system."""

    decision_id: str
    decision: str  # APPROVED/DENIED/ESCALATED
    confidence: float
    reasoning: list[str]
    latency_ms: int
    cost_usd: float
    timestamp: datetime


class ProductionDecision(BaseModel):
    """Decision from existing Judge 6 system."""

    decision_id: str
    decision: str
    confidence: float
    reasoning: list[str] | None = None
    latency_ms: int
    timestamp: datetime


class ComparisonResult(BaseModel):
    """Comparison between shadow and production decisions."""

    comparison_id: str
    request_id: str
    timestamp: datetime

    shadow_decision: ShadowDecision
    production_decision: ProductionDecision

    agreement_level: AgreementLevel
    decision_matches: bool
    confidence_delta: float

    notes: list[str] = field(default_factory=list)


@dataclass
class ShadowModeMetrics:
    """Aggregated metrics for shadow mode validation."""

    total_comparisons: int = 0
    exact_matches: int = 0
    decision_matches: int = 0
    partial_matches: int = 0
    mismatches: int = 0

    shadow_avg_latency_ms: float = 0.0
    production_avg_latency_ms: float = 0.0

    shadow_avg_cost_usd: float = 0.0
    shadow_total_cost_usd: float = 0.0

    false_positives: int = 0  # Shadow denied, production approved
    false_negatives: int = 0  # Shadow approved, production denied

    @property
    def agreement_rate(self) -> float:
        """Calculate overall agreement rate."""
        if self.total_comparisons == 0:
            return 0.0
        return (self.exact_matches + self.decision_matches) / self.total_comparisons

    @property
    def exact_match_rate(self) -> float:
        """Calculate exact match rate."""
        if self.total_comparisons == 0:
            return 0.0
        return self.exact_matches / self.total_comparisons

    @property
    def latency_ratio(self) -> float:
        """Shadow latency / Production latency."""
        if self.production_avg_latency_ms == 0:
            return 0.0
        return self.shadow_avg_latency_ms / self.production_avg_latency_ms


class ShadowModeOrchestrator:
    """Orchestrates shadow mode deployment and validation.

    Dual-evaluates requests through both systems, compares results,
    tracks metrics, and generates migration readiness reports.
    """

    def __init__(
        self,
        shadow_agent: Any,
        production_client: Any,
        sample_rate: float = None,
        log_mismatches_only: bool = False,
    ):
        """Initialize shadow mode orchestrator.

        Args:
            shadow_agent: New agent-based governance system
            production_client: Existing Judge 6 client
            sample_rate: Fraction of requests to shadow (0.0-1.0)
            log_mismatches_only: Only log disagreements for review

        """
        self.shadow_agent = shadow_agent
        self.production_client = production_client
        self.sample_rate = sample_rate or settings.shadow_mode_sample_rate
        self.log_mismatches_only = log_mismatches_only

        # Metrics tracking
        self.metrics = ShadowModeMetrics()
        self.comparisons: list[ComparisonResult] = []

        # Storage for detailed analysis
        self.mismatch_log: list[ComparisonResult] = []

    async def evaluate_request(
        self,
        request: dict[str, Any],
        use_shadow_decision: bool = False,
    ) -> dict[str, Any]:
        """Evaluate request through both systems.

        Args:
            request: Governance request
            use_shadow_decision: If True, return shadow decision (for A/B testing)

        Returns:
            Production decision (or shadow if use_shadow_decision=True)

        """
        # Sample rate check
        if not self._should_shadow(request):
            # Only production
            return await self._get_production_decision(request)

        request_id = request.get("request_id", str(uuid.uuid4()))

        # Parallel evaluation
        shadow_task = asyncio.create_task(self._get_shadow_decision(request))
        production_task = asyncio.create_task(self._get_production_decision(request))

        # Wait for both
        shadow_result, production_result = await asyncio.gather(
            shadow_task,
            production_task,
            return_exceptions=True,
        )

        # Handle errors
        if isinstance(shadow_result, Exception):
            shadow_result = self._create_error_decision("shadow", str(shadow_result), request_id)

        if isinstance(production_result, Exception):
            # Production error is critical, no comparison possible
            return production_result

        # Compare results
        comparison = self._compare_decisions(
            request_id=request_id,
            shadow=shadow_result,
            production=production_result,
        )

        # Record comparison
        self._record_comparison(comparison)

        # Return appropriate decision
        if use_shadow_decision:
            return self._format_decision(shadow_result)
        return self._format_decision(production_result)

    def _should_shadow(self, request: dict[str, Any]) -> bool:
        """Determine if request should be shadowed based on sample rate."""
        import random

        return random.random() < self.sample_rate

    async def _get_shadow_decision(self, request: dict[str, Any]) -> ShadowDecision:
        """Get decision from shadow agent system."""
        start = time.time()

        # Call shadow agent
        decision = await self.shadow_agent.evaluate(request)

        latency_ms = int((time.time() - start) * 1000)

        return ShadowDecision(
            decision_id=decision.decision_id,
            decision=decision.status.value,
            confidence=decision.confidence_score,
            reasoning=decision.reasoning_trace,
            latency_ms=latency_ms,
            cost_usd=decision.metrics.get("cost_usd", 0.0) if decision.metrics else 0.0,
            timestamp=datetime.utcnow(),
        )

    async def _get_production_decision(self, request: dict[str, Any]) -> ProductionDecision:
        """Get decision from existing Judge 6 system."""
        import httpx

        start = time.time()

        # Call Judge 6 endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.judge6_endpoint,
                json=request,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start) * 1000)

        return ProductionDecision(
            decision_id=data.get("decision_id", str(uuid.uuid4())),
            decision=data.get("decision", "UNKNOWN"),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning"),
            latency_ms=latency_ms,
            timestamp=datetime.utcnow(),
        )

    def _compare_decisions(
        self,
        request_id: str,
        shadow: ShadowDecision,
        production: ProductionDecision,
    ) -> ComparisonResult:
        """Compare shadow and production decisions."""
        # Determine agreement level
        decision_matches = shadow.decision == production.decision
        confidence_delta = abs(shadow.confidence - production.confidence)

        if decision_matches and confidence_delta < 0.1:
            agreement_level = AgreementLevel.EXACT_MATCH
        elif decision_matches:
            agreement_level = AgreementLevel.DECISION_MATCH
        elif confidence_delta < 0.2:
            agreement_level = AgreementLevel.PARTIAL_MATCH
        else:
            agreement_level = AgreementLevel.MISMATCH

        # Collect notes
        notes = []
        if shadow.latency_ms > production.latency_ms * 2:
            notes.append(f"Shadow 2x slower: {shadow.latency_ms}ms vs {production.latency_ms}ms")

        if not decision_matches:
            notes.append(
                f"Decision mismatch: Shadow={shadow.decision}, Production={production.decision}",
            )

        return ComparisonResult(
            comparison_id=str(uuid.uuid4()),
            request_id=request_id,
            timestamp=datetime.utcnow(),
            shadow_decision=shadow,
            production_decision=production,
            agreement_level=agreement_level,
            decision_matches=decision_matches,
            confidence_delta=confidence_delta,
            notes=notes,
        )

    def _record_comparison(self, comparison: ComparisonResult) -> None:
        """Record comparison and update metrics."""
        # Update counts
        self.metrics.total_comparisons += 1

        if comparison.agreement_level == AgreementLevel.EXACT_MATCH:
            self.metrics.exact_matches += 1
        elif comparison.agreement_level == AgreementLevel.DECISION_MATCH:
            self.metrics.decision_matches += 1
        elif comparison.agreement_level == AgreementLevel.PARTIAL_MATCH:
            self.metrics.partial_matches += 1
        else:
            self.metrics.mismatches += 1

        # False positive/negative tracking
        shadow_decision = comparison.shadow_decision.decision
        prod_decision = comparison.production_decision.decision

        if shadow_decision == "DENIED" and prod_decision == "APPROVED":
            self.metrics.false_positives += 1
        elif shadow_decision == "APPROVED" and prod_decision == "DENIED":
            self.metrics.false_negatives += 1

        # Update latency averages
        n = self.metrics.total_comparisons
        self.metrics.shadow_avg_latency_ms = (
            self.metrics.shadow_avg_latency_ms * (n - 1) + comparison.shadow_decision.latency_ms
        ) / n

        self.metrics.production_avg_latency_ms = (
            self.metrics.production_avg_latency_ms * (n - 1)
            + comparison.production_decision.latency_ms
        ) / n

        # Update cost
        self.metrics.shadow_total_cost_usd += comparison.shadow_decision.cost_usd
        self.metrics.shadow_avg_cost_usd = self.metrics.shadow_total_cost_usd / n

        # Store comparison
        if not self.log_mismatches_only or not comparison.decision_matches:
            self.comparisons.append(comparison)

        # Store mismatches separately
        if not comparison.decision_matches:
            self.mismatch_log.append(comparison)

    def _create_error_decision(self, system: str, error: str, request_id: str) -> ShadowDecision:
        """Create error decision for failed evaluation."""
        return ShadowDecision(
            decision_id=f"{system}_error_{request_id[:8]}",
            decision="ERROR",
            confidence=0.0,
            reasoning=[f"System error: {error}"],
            latency_ms=0,
            cost_usd=0.0,
            timestamp=datetime.utcnow(),
        )

    def _format_decision(self, decision: Any) -> dict[str, Any]:
        """Format decision for return to caller."""
        if isinstance(decision, ShadowDecision):
            return {
                "decision_id": decision.decision_id,
                "decision": decision.decision,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
            }
        return {
            "decision_id": decision.decision_id,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning or [],
        }

    def get_migration_readiness_report(self) -> dict[str, Any]:
        """Generate migration readiness report.

        Success criteria:
        - Agreement rate >95%
        - Latency <5s p95
        - False positive rate <10%
        - No system stability issues
        """
        report = {
            "summary": {
                "total_comparisons": self.metrics.total_comparisons,
                "agreement_rate": f"{self.metrics.agreement_rate:.1%}",
                "exact_match_rate": f"{self.metrics.exact_match_rate:.1%}",
            },
            "latency": {
                "shadow_avg_ms": self.metrics.shadow_avg_latency_ms,
                "production_avg_ms": self.metrics.production_avg_latency_ms,
                "ratio": f"{self.metrics.latency_ratio:.2f}x",
            },
            "cost": {
                "avg_per_decision_usd": f"${self.metrics.shadow_avg_cost_usd:.6f}",
                "total_usd": f"${self.metrics.shadow_total_cost_usd:.2f}",
                "within_target": self.metrics.shadow_avg_cost_usd
                < settings.cost_target_per_decision,
            },
            "accuracy": {
                "false_positives": self.metrics.false_positives,
                "false_negatives": self.metrics.false_negatives,
                "false_positive_rate": f"{(self.metrics.false_positives / max(1, self.metrics.total_comparisons)):.1%}",
            },
            "readiness": self._assess_readiness(),
            "mismatches_sample": [
                {
                    "request_id": c.request_id,
                    "shadow": c.shadow_decision.decision,
                    "production": c.production_decision.decision,
                    "notes": c.notes,
                }
                for c in self.mismatch_log[:10]  # First 10 mismatches
            ],
        }

        return report

    def _assess_readiness(self) -> dict[str, Any]:
        """Assess readiness for production migration."""
        criteria = {
            "agreement_rate_ok": self.metrics.agreement_rate >= 0.95,
            "latency_ok": self.metrics.shadow_avg_latency_ms < 5000,  # <5s
            "cost_ok": self.metrics.shadow_avg_cost_usd < settings.cost_target_per_decision,
            "false_positive_rate_ok": (
                self.metrics.false_positives / max(1, self.metrics.total_comparisons)
            )
            < 0.10,
        }

        all_ok = all(criteria.values())

        return {
            "ready_for_migration": all_ok,
            "criteria": criteria,
            "recommendation": (
                "✅ READY: Proceed to Phase 2 (Low-risk rollout)"
                if all_ok
                else "⚠️  NOT READY: Address failing criteria before migration"
            ),
        }
