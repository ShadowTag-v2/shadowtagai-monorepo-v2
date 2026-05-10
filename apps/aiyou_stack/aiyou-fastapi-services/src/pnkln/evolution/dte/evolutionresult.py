from dataclasses import dataclass, field
from datetime import datetime

from .elegancemetrics import EleganceMetrics
from .evolutionstrategy import EvolutionStrategy


@dataclass
class EvolutionResult:
    """Result from evolution iteration"""

    strategy: EvolutionStrategy
    original_version: str
    evolved_version: str
    improvement_metric: float = field(metadata={"description": "% improvement"})
    test_cases_passed: int
    test_cases_total: int
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""
    grpo_metrics: dict[str, float] | None = None
    elegance_metrics: EleganceMetrics | None = None
