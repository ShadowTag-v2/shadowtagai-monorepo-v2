from .source import Source
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class IngestedItem:
    """Represents an ingested data item"""

    item_id: str
    source: Source
    title: str
    content: str
    url: str
    ingested_at: datetime
    relevance_score: float
    timeliness_score: float
    completeness_score: float
    cost_usd: float
    metadata: dict[str, Any]
