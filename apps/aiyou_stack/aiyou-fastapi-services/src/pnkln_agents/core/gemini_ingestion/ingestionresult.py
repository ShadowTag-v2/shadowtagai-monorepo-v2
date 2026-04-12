from dataclasses import dataclass


@dataclass
class IngestionResult:
    """Result of ingestion operation"""

    items: list[IngestedItem]
    metrics: IngestionMetrics
    violations: list[EthicalViolation]
    runtime_minutes: float
    success: bool
    errors: list[str]
