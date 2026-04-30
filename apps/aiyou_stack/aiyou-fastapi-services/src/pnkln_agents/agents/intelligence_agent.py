# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Intelligence Agent: Collection → Enforcement Pipeline

Combines Gemini Ingestion Layer (upstream) with Judge 6 Enforcement (downstream)

Architecture:
┌─────────────────────────────────────────────────────────┐
│                   Intelligence Agent                     │
│                                                          │
│  1. Gemini Ingestion Layer (Collection)                 │
│     ├─ Multi-source data collection                     │
│     ├─ Ethical compliance validation                    │
│     ├─ Tier classification                              │
│     └─ Quality scoring (relevance/timeliness)           │
│                                                          │
│  2. JR Engine Validation (Purpose/Reasons/Brakes)       │
│     └─ Validate collection intent                       │
│                                                          │
│  3. Judge 6 Enforcement (Verification)                 │
│     ├─ GDPR/CAN-SPAM compliance                         │
│     ├─ Content policy enforcement                       │
│     └─ Audit trail generation                           │
│                                                          │
│  4. AM Briefing Delivery                                │
│     └─ Formatted intelligence summary                   │
└─────────────────────────────────────────────────────────┘
"""

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ..config.ingestion_config import DEFAULT_INGESTION_CONFIG, IngestionConfig
from ..core.agent_pattern import AgentStatus, AgentTask, ShadowTagAiAgent
from ..core.Claude_Code_6_lite import VerificationResult
from ..core.gemini_ingestion import (
    GeminiIngestionLayer,
    IngestionResult,
    Source,
)
from ..core.jr_engine import Reason


@dataclass
class IntelligenceTask:
    """Task for intelligence collection and enforcement"""

    query: str
    target_items: int
    customer_id: str
    sources: list[Source] | None = None
    require_enforcement: bool = True
    require_briefing: bool = True
    context: dict[str, Any] = None


@dataclass
class IntelligenceResult:
    """Result of intelligence operation"""

    status: AgentStatus
    ingestion_result: IngestionResult | None = None
    verification_result: VerificationResult | None = None
    briefing: str | None = None
    metrics: dict[str, Any] | None = None
    audit_trail: dict[str, Any] = None
    execution_time_ms: float = 0.0


class IntelligenceAgent(ShadowTagAiAgent):
    """Intelligence agent combining collection and enforcement

    Pipeline:
    1. Collect intelligence from multiple sources (Gemini Ingestion Layer)
    2. Validate collection intent (JR Engine)
    3. Enforce compliance on collected data (Judge 6 Lite)
    4. Generate morning briefing
    5. Export audit trail

    Use cases:
    - Daily intelligence briefing (nightly cron job)
    - On-demand intelligence collection
    - Compliance-verified data gathering
    """

    def __init__(
        self,
        ingestion_layer: GeminiIngestionLayer | None = None,
        ingestion_config: IngestionConfig | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Initialize ingestion layer
        self.ingestion_config = ingestion_config or DEFAULT_INGESTION_CONFIG
        self.ingestion_layer = ingestion_layer or GeminiIngestionLayer(
            config=self.ingestion_config.to_dict(),
        )

    def collect_intelligence(self, task: IntelligenceTask) -> IntelligenceResult:
        """Run intelligence collection and enforcement pipeline

        Args:
            task: IntelligenceTask with query, sources, and requirements

        Returns:
            IntelligenceResult with collected data, verification, and briefing

        """
        start_time = time.perf_counter()
        task.context = task.context or {}

        # Build agent task for JR Engine validation
        agent_task = AgentTask(
            intent=f"Collect intelligence: {task.query}",
            customer_id=task.customer_id,
            context={
                **task.context,
                "query": task.query,
                "target_items": task.target_items,
                "is_intelligence_collection": True,
            },
            cost_estimate_usd=task.target_items * self.ingestion_config.target_cost_per_item,
            business_value=f"Intelligence collection for {task.customer_id}",
            expected_outcome=f"{task.target_items} compliance-verified intelligence items",
        )

        # Execute with enforcement-first pattern
        agent_result = self.execute(agent_task)

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        if agent_result.status == AgentStatus.COMPLETED:
            return agent_result.output
        # Return partial result with error status
        return IntelligenceResult(
            status=agent_result.status,
            audit_trail=agent_result.audit_trail,
            execution_time_ms=execution_time_ms,
        )

    def _build_reasons(self, task: AgentTask) -> list[Reason]:
        """Build reasons specific to intelligence collection"""
        target_items = task.context.get("target_items", 1000)
        query = task.context.get("query", "")

        return [
            Reason(
                justification=f"Intelligence collection query: {query}",
                risk_probability=0.2,  # Low risk for read-only collection
                risk_severity=0.3,  # Medium severity if ethical violations occur
                mitigation_strategy="Ethical compliance validation + Judge 6 enforcement",
            ),
            Reason(
                justification=f"Estimated cost: ${task.cost_estimate_usd:.2f} for {target_items} items",
                risk_probability=0.1,
                risk_severity=0.1,
                mitigation_strategy="Per-item cost tracking and budget enforcement",
            ),
            Reason(
                justification="Multi-source collection with tier classification",
                risk_probability=0.15,
                risk_severity=0.2,
                mitigation_strategy="Tier-based filtering and quality scoring",
            ),
        ]

    def _execute_task(self, task: AgentTask, constraints: dict[str, Any]) -> IntelligenceResult:
        """Execute intelligence collection with enforcement

        Pipeline:
        1. Gemini Ingestion Layer collects data
        2. Judge 6 verifies compliance
        3. Generate AM briefing
        4. Return results
        """
        query = task.context.get("query", "")
        target_items = task.context.get("target_items", 1000)

        # Step 1: Run ingestion layer
        ingestion_result = self.ingestion_layer.ingest(
            sources=None,  # Use all registered sources
            target_items=target_items,
        )

        # Check if ingestion succeeded
        if not ingestion_result.success:
            return IntelligenceResult(
                status=AgentStatus.FAILED,
                ingestion_result=ingestion_result,
                metrics={"errors": ingestion_result.errors},
            )

        # Step 2: Validate quality gates
        quality_gates = self.ingestion_layer.validate_quality_gates(ingestion_result.metrics)
        failed_gates = [gate for gate, passed in quality_gates.items() if not passed]

        if failed_gates:
            # Log warnings but continue
            pass

        # Step 3: Verify with Judge 6 (on sampled items)
        # For large collections, verify a sample
        sample_size = min(len(ingestion_result.items), 100)
        sampled_items = ingestion_result.items[:sample_size]

        # Build verification data
        verification_data = {
            "items_count": len(ingestion_result.items),
            "sampled_items": [
                {
                    "title": item.title,
                    "url": item.url,
                    "source": item.source.name,
                    "tier": item.source.tier.value,
                    "relevance": item.relevance_score,
                }
                for item in sampled_items
            ],
            "metrics": {
                "items_per_day": ingestion_result.metrics.items_per_day,
                "average_cost_per_item": ingestion_result.metrics.average_cost_per_item,
                "average_relevance": ingestion_result.metrics.average_relevance_score,
            },
        }

        # Verify compliance (content policy, attribution, etc.)
        verification_context = {
            **task.context,
            "is_intelligence_collection": True,
            "involves_pii": False,  # Intelligence collection, not personal data
        }

        verification_result = self.Claude_Code_6.verify(
            verification_data, context=verification_context
        )

        # Step 4: Generate AM briefing
        briefing = self.ingestion_layer.export_am_briefing(
            ingestion_result.items,
            format="markdown",
        )

        # Step 5: Calculate combined metrics
        combined_metrics = {
            "ingestion": {
                "items_collected": len(ingestion_result.items),
                "unique_sources": ingestion_result.metrics.unique_sources_count,
                "average_cost_per_item": ingestion_result.metrics.average_cost_per_item,
                "average_relevance": ingestion_result.metrics.average_relevance_score,
                "runtime_minutes": ingestion_result.runtime_minutes,
                "tier_1_percentage": ingestion_result.metrics.tier_1_percentage,
                "tier_2_percentage": ingestion_result.metrics.tier_2_percentage,
                "tier_3_percentage": ingestion_result.metrics.tier_3_percentage,
                "ethical_violations": len(ingestion_result.metrics.ethical_violations),
            },
            "enforcement": {
                "verification_passed": verification_result.passed,
                "violations": len(verification_result.violations),
                "verification_time_ms": verification_result.verification_time_ms,
            },
            "quality_gates": quality_gates,
        }

        return IntelligenceResult(
            status=AgentStatus.COMPLETED,
            ingestion_result=ingestion_result,
            verification_result=verification_result,
            briefing=briefing,
            metrics=combined_metrics,
            audit_trail={
                "timestamp": datetime.now(UTC).isoformat(),
                "query": query,
                "target_items": target_items,
                "actual_items": len(ingestion_result.items),
                "quality_gates": quality_gates,
                "failed_gates": failed_gates,
            },
        )

    def _verify_with_Claude_Code_6(self, result: IntelligenceResult, context: dict[str, Any]):
        """Override to skip redundant verification (already done in _execute_task)"""
        # Verification already performed in _execute_task
        return result.verification_result or super()._verify_with_Claude_Code_6(result, context)

    def register_source(self, source: Source):
        """Register a data source for ingestion"""
        self.ingestion_layer.register_source(source)

    def register_sources(self, sources: list[Source]):
        """Register multiple data sources"""
        for source in sources:
            self.register_source(source)


# Example usage
def example_usage():
    """Example of using Intelligence Agent"""
    from ..config.ingestion_config import DEFAULT_SOURCES

    # Initialize agent
    agent = IntelligenceAgent()

    # Register sources
    agent.register_sources(DEFAULT_SOURCES)

    # Collect intelligence
    result = agent.collect_intelligence(
        IntelligenceTask(
            query="AI agent frameworks and LLM developments",
            target_items=100,
            customer_id="customer_123",
            require_enforcement=True,
            require_briefing=True,
        ),
    )

    print(f"Status: {result.status.value}")

    if result.status == AgentStatus.COMPLETED:
        print("\nIngestion Metrics:")
        print(f"  Items collected: {result.metrics['ingestion']['items_collected']}")
        print(f"  Unique sources: {result.metrics['ingestion']['unique_sources']}")
        print(f"  Average cost: ${result.metrics['ingestion']['average_cost_per_item']:.4f}")
        print(f"  Average relevance: {result.metrics['ingestion']['average_relevance']:.2f}")
        print(f"  Runtime: {result.metrics['ingestion']['runtime_minutes']:.2f} min")

        print("\nTier Distribution:")
        print(f"  Tier 1: {result.metrics['ingestion']['tier_1_percentage']:.1f}%")
        print(f"  Tier 2: {result.metrics['ingestion']['tier_2_percentage']:.1f}%")
        print(f"  Tier 3: {result.metrics['ingestion']['tier_3_percentage']:.1f}%")

        print("\nEnforcement:")
        print(f"  Verification passed: {result.metrics['enforcement']['verification_passed']}")
        print(f"  Violations: {result.metrics['enforcement']['violations']}")

        print("\nBriefing preview:")
        print(result.briefing[:500] + "..." if len(result.briefing) > 500 else result.briefing)


if __name__ == "__main__":
    example_usage()
