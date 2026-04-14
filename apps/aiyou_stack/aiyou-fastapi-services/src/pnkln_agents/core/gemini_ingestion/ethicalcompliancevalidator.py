from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from .source import EthicalViolation, EthicalViolationType, IngestedItem, Source


class EthicalComplianceValidator:
    """
    Validates ethical compliance for web crawling and data collection

    Checks:
    - robots.txt compliance
    - Rate limiting adherence
    - Terms of Service compliance
    - Attribution requirements
    - Privacy considerations
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.max_requests_per_hour = self.config.get("max_requests_per_hour", 60)
        self.respect_robots_txt = self.config.get("respect_robots_txt", True)
        self.user_agent = self.config.get(
            "user_agent", "SHADOWTAGAIBot/1.0 (+https://shadowtagai.ai/bot)"
        )
        self.request_history: dict[str, list[datetime]] = {}

    def validate_robots_txt(self, url: str, source: Source) -> EthicalViolation | None:
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots_txt:
            return None
        if not source.robots_txt_checked:
            return EthicalViolation(
                violation_type=EthicalViolationType.ROBOTS_TXT,
                source=source.url,
                description="robots.txt not checked before accessing source",
                severity="medium",
                timestamp=datetime.utcnow(),
                remediation="Check and cache robots.txt before scraping",
            )
        if not source.robots_txt_compliant:
            return EthicalViolation(
                violation_type=EthicalViolationType.ROBOTS_TXT,
                source=source.url,
                description="Source disallows bot access in robots.txt",
                severity="high",
                timestamp=datetime.utcnow(),
                remediation="Skip this source or request permission",
            )
        return None

    def validate_rate_limit(self, source: Source) -> EthicalViolation | None:
        """Check if rate limit would be exceeded"""
        domain = urlparse(source.url).netloc
        now = datetime.utcnow()
        if domain not in self.request_history:
            self.request_history[domain] = []
        cutoff = datetime.utcnow().timestamp() - 3600
        self.request_history[domain] = [
            req for req in self.request_history[domain] if req.timestamp() > cutoff
        ]
        requests_last_hour = len(self.request_history[domain])
        if requests_last_hour >= source.rate_limit_per_hour:
            return EthicalViolation(
                violation_type=EthicalViolationType.RATE_LIMIT,
                source=source.url,
                description=f"Rate limit exceeded: {requests_last_hour}/{source.rate_limit_per_hour} requests/hour",
                severity="high",
                timestamp=now,
                remediation="Wait before next request or reduce rate",
            )
        return None

    def validate_attribution(self, item: IngestedItem) -> EthicalViolation | None:
        """Check if proper attribution is included"""
        if not item.metadata.get("source_url") and (not item.url):
            return EthicalViolation(
                violation_type=EthicalViolationType.ATTRIBUTION,
                source=item.source.url,
                description="Missing source attribution in ingested item",
                severity="medium",
                timestamp=datetime.utcnow(),
                remediation="Add source_url to metadata",
            )
        return None

    def record_request(self, source: Source):
        """Record a request for rate limiting"""
        domain = urlparse(source.url).netloc
        if domain not in self.request_history:
            self.request_history[domain] = []
        self.request_history[domain].append(datetime.utcnow())
