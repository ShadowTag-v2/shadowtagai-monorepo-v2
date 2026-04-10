"""
Observability layer for agent governance system.

Integrates AgentOps for LLM-specific tracing, Cloud Logging for audit trails,
and custom metrics for cost/performance tracking.
"""

from datetime import datetime
from typing import Any

from google.cloud import logging as cloud_logging
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel

from src.agents.base import GovernanceDecision
from src.gov_config import settings


class AuditLogEntry(BaseModel):
    """
    Structured audit log entry for governance decisions.

    Complies with EU AI Act (6-month retention), GDPR Article 22
    (automated decision transparency), and NIST AI RMF requirements.
    """

    audit_entry_id: str
    timestamp: datetime
    user_id: str | None
    request_type: str

    # Model information
    model_name: str
    model_version: str | None = None

    # Request details
    input_tokens: int
    cache_hit: bool

    # Response details
    decision: str
    confidence_score: float
    output_tokens: int
    reasoning_trace: list[str]
    policy_references: list[dict[str, Any]]

    # Guardrails
    toxicity_check: str = "passed"
    bias_check: str = "passed"

    # Performance
    latency_ms: int
    ttft_ms: int | None = None

    # Cost
    total_cost_usd: float
    cached_savings_usd: float

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ObservabilityManager:
    """
    Manages observability for governance system.

    Integrates:
    - AgentOps for session replay and LLM tracing
    - Google Cloud Logging for audit trails
    - OpenTelemetry for distributed tracing
    - Custom metrics for cost/performance
    """

    def __init__(self):
        """Initialize observability manager."""
        # AgentOps
        self.agentops_enabled = getattr(settings, "agentops_api_key", None) is not None
        if self.agentops_enabled:
            self._initialize_agentops()

        # Cloud Logging
        if getattr(settings, "enable_cloud_logging", False):
            self.logging_client = cloud_logging.Client(project=settings.gcp_project_id)
            self.logger = self.logging_client.logger("governance-decisions")
        else:
            self.logging_client = None
            self.logger = None

        # Cloud Trace
        if getattr(settings, "enable_cloud_trace", False):
            self._initialize_cloud_trace()
        else:
            self.tracer = None

    def _initialize_agentops(self) -> None:
        """Initialize AgentOps for LLM observability."""
        try:
            import agentops

            agentops.init(api_key=settings.agentops_api_key)
            self.agentops = agentops
            print("✅ AgentOps initialized")
        except Exception as e:
            print(f"⚠️  AgentOps initialization failed: {e}")
            self.agentops_enabled = False

    def _initialize_cloud_trace(self) -> None:
        """Initialize Google Cloud Trace."""
        try:
            # Set up tracer provider
            tracer_provider = TracerProvider()

            # Add Cloud Trace exporter
            cloud_trace_exporter = CloudTraceSpanExporter(project_id=settings.gcp_project_id)
            tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))

            # Set as global provider
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)

            print("✅ Cloud Trace initialized")
        except Exception as e:
            print(f"⚠️  Cloud Trace initialization failed: {e}")
            self.tracer = None

    def log_decision(self, decision: GovernanceDecision) -> None:
        """
        Log governance decision to audit trail.

        Args:
            decision: Governance decision to log
        """
        # Build audit log entry
        audit_entry = AuditLogEntry(
            audit_entry_id=decision.decision_id,
            timestamp=decision.timestamp,
            user_id=decision.user_id,
            request_type=decision.action_type,
            model_name=decision.metrics.get("model", "unknown") if decision.metrics else "unknown",
            input_tokens=decision.metrics.get("input_tokens", 0) if decision.metrics else 0,
            cache_hit=decision.metrics.get("cache_hit", False) if decision.metrics else False,
            decision=decision.status.value,
            confidence_score=decision.confidence_score,
            output_tokens=decision.metrics.get("output_tokens", 0) if decision.metrics else 0,
            reasoning_trace=decision.reasoning_trace,
            policy_references=[ref.dict() for ref in decision.policy_references],
            latency_ms=decision.metrics.get("latency_ms", 0) if decision.metrics else 0,
            ttft_ms=decision.metrics.get("ttft_ms") if decision.metrics else None,
            total_cost_usd=decision.metrics.get("cost_usd", 0.0) if decision.metrics else 0.0,
            cached_savings_usd=decision.metrics.get("cached_savings_usd", 0.0)
            if decision.metrics
            else 0.0,
        )

        # Log to Cloud Logging
        if self.logger:
            self.logger.log_struct(
                audit_entry.dict(),
                severity="INFO",
                labels={
                    "decision": decision.status.value,
                    "requires_escalation": str(decision.requires_escalation),
                },
            )

        # Log to AgentOps if enabled
        if self.agentops_enabled:
            self._log_to_agentops(decision, audit_entry)

    def _log_to_agentops(self, decision: GovernanceDecision, audit_entry: AuditLogEntry) -> None:
        """Log decision to AgentOps for session replay."""
        try:
            # AgentOps automatically tracks LLM calls
            # We add custom events for governance-specific data
            self.agentops.record(
                event_type="governance_decision",
                data={
                    "decision_id": decision.decision_id,
                    "decision": decision.status.value,
                    "confidence": decision.confidence_score,
                    "cost_usd": audit_entry.total_cost_usd,
                    "latency_ms": audit_entry.latency_ms,
                },
            )
        except Exception as e:
            print(f"⚠️  AgentOps logging failed: {e}")

    def trace_decision(self, decision: GovernanceDecision) -> None:
        """
        Create distributed trace span for decision.

        Args:
            decision: Governance decision to trace
        """
        if not self.tracer:
            return

        try:
            with self.tracer.start_as_current_span("governance_decision") as span:
                span.set_attribute("decision.id", decision.decision_id)
                span.set_attribute("decision.status", decision.status.value)
                span.set_attribute("decision.confidence", decision.confidence_score)
                span.set_attribute(
                    "decision.latency_ms",
                    decision.metrics.get("latency_ms", 0) if decision.metrics else 0,
                )
                span.set_attribute(
                    "decision.cost_usd",
                    decision.metrics.get("cost_usd", 0.0) if decision.metrics else 0.0,
                )

                if decision.requires_escalation:
                    span.set_attribute("decision.escalated", True)
                    span.set_attribute(
                        "decision.escalation_reason", decision.escalation_reason or ""
                    )

        except Exception as e:
            print(f"⚠️  Tracing failed: {e}")

    def query_audit_logs(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query audit logs for compliance reporting.

        Args:
            start_time: Start of time range
            end_time: End of time range
            filters: Optional filters (user_id, decision, etc.)

        Returns:
            List of audit log entries
        """
        if not self.logging_client:
            return []

        # Build filter string
        filter_parts = [
            'resource.type="global"',
            f'logName="projects/{settings.gcp_project_id}/logs/governance-decisions"',
            f'timestamp >= "{start_time.isoformat()}"',
            f'timestamp <= "{end_time.isoformat()}"',
        ]

        if filters:
            for key, value in filters.items():
                filter_parts.append(f'jsonPayload.{key}="{value}"')

        filter_str = " AND ".join(filter_parts)

        # Query logs
        entries = self.logging_client.list_entries(filter_=filter_str, max_results=1000)

        # Format results
        results = []
        for entry in entries:
            results.append(entry.payload)

        return results


class MetricsCollector:
    """
    Collects and aggregates metrics for cost/performance monitoring.

    Tracks:
    - Cost per decision (target: <$0.01)
    - Latency (p50, p95, p99)
    - Token usage
    - Cache hit rates
    - Error rates
    """

    def __init__(self):
        self.decisions: list[dict[str, Any]] = []

    def record_decision(self, decision: GovernanceDecision) -> None:
        """Record decision metrics."""
        if not decision.metrics:
            return

        self.decisions.append(
            {
                "timestamp": decision.timestamp,
                "latency_ms": decision.metrics.get("latency_ms", 0),
                "cost_usd": decision.metrics.get("cost_usd", 0.0),
                "input_tokens": decision.metrics.get("input_tokens", 0),
                "output_tokens": decision.metrics.get("output_tokens", 0),
                "cached_tokens": decision.metrics.get("cached_tokens", 0),
                "cache_hit": decision.metrics.get("cache_hit", False),
                "confidence": decision.confidence_score,
                "status": decision.status.value,
            }
        )

    def get_summary_metrics(self) -> dict[str, Any]:
        """Get summary metrics for dashboard."""
        if not self.decisions:
            return {
                "total_decisions": 0,
                "error": "No decisions recorded",
            }

        import numpy as np

        latencies = [d["latency_ms"] for d in self.decisions]
        costs = [d["cost_usd"] for d in self.decisions]
        cache_hits = sum(1 for d in self.decisions if d["cache_hit"])

        return {
            "total_decisions": len(self.decisions),
            "latency": {
                "p50_ms": int(np.percentile(latencies, 50)),
                "p95_ms": int(np.percentile(latencies, 95)),
                "p99_ms": int(np.percentile(latencies, 99)),
                "avg_ms": int(np.mean(latencies)),
                "target_p99_ms": settings.latency_target_p99_ms,
                "meets_target": np.percentile(latencies, 99) < settings.latency_target_p99_ms,
            },
            "cost": {
                "avg_per_decision_usd": np.mean(costs),
                "total_usd": sum(costs),
                "target_usd": settings.cost_target_per_decision,
                "meets_target": np.mean(costs) < settings.cost_target_per_decision,
                "margin_pct": (
                    (settings.cost_target_per_decision - np.mean(costs))
                    / settings.cost_target_per_decision
                    * 100
                ),
            },
            "cache": {
                "hit_rate": cache_hits / len(self.decisions),
                "total_hits": cache_hits,
            },
            "decisions": {
                "approved": sum(1 for d in self.decisions if d["status"] == "APPROVED"),
                "denied": sum(1 for d in self.decisions if d["status"] == "DENIED"),
                "escalated": sum(1 for d in self.decisions if d["status"] == "ESCALATED"),
            },
        }


# Global instances
observability = ObservabilityManager()
metrics_collector = MetricsCollector()
