from dataclasses import dataclass
from datetime import datetime


@dataclass
class Source:
    """Represents a data source"""

    url: str
    source_type: SourceType
    tier: SourceTier
    name: str
    enabled: bool = True
    rate_limit_per_hour: int = 60
    last_accessed: datetime | None = None
    robots_txt_checked: bool = False
    robots_txt_compliant: bool = True
