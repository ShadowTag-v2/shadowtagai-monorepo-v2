# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .source import Source


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
