"""
Gemini Ingestion Layer Service
Implements PNKLN Core Stack™ Preparation (P) component
Based on docs/cor8-shadowtag_v4-global-edge-fabric/03-technical-architecture/gemini-ingestion-layer.md
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # Graceful degradation if not installed

from app.models.schemas import (
    IngestionSubmitRequest,
    SourceHealth,
    SourceType,
    TierClassification,
)


class EthicalComplianceChecker:
    """
    Ethical web crawling compliance checker
    Enforces robots.txt, rate limiting, PII scrubbing
    """

    USER_AGENT = "PNKLNBot/1.0 (+https://pnkln.ai/bot; compliance@shadowtag_v4.ai)"

    # Rate limits per source type (requests per second)
    RATE_LIMITS = {
        SourceType.YOUTUBE: 10 / 60,  # 10 requests per minute (API quota)
        SourceType.TWITTER: 15 / (15 * 60),  # 15 requests per 15 minutes
        SourceType.NEWS_API: 1,  # 1 request per second
        SourceType.RSS: 1,  # 1 request per second
        SourceType.RESEARCH: 0.5,  # 1 request per 2 seconds
        SourceType.GOVERNMENT: 0.5,  # 1 request per 2 seconds
    }

    # PII scrubbing patterns
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    }

    def __init__(self):
        self.robots_cache: dict[str, dict] = {}
        self.rate_limit_tracker: dict[str, list[float]] = {}

    async def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Check cache
        if domain in self.robots_cache:
            cache_time, rules = self.robots_cache[domain]
            if datetime.now().timestamp() - cache_time < 3600:  # 1-hour cache
                return self._is_allowed(rules, parsed.path)

        # Fetch robots.txt
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    f"{domain}/robots.txt",
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response,
            ):
                if response.status == 200:
                    content = await response.text()
                    rules = self._parse_robots_txt(content)
                    self.robots_cache[domain] = (datetime.now().timestamp(), rules)
                    return self._is_allowed(rules, parsed.path)
        except Exception:
            pass  # If robots.txt unavailable, assume allowed (defensive crawling)

        return True

    def _parse_robots_txt(self, content: str) -> dict[str, list[str]]:
        """Parse robots.txt content (simplified)"""
        rules = {"disallow": [], "allow": []}
        for line in content.split("\n"):
            line = line.strip().lower()
            if line.startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    rules["disallow"].append(path)
            elif line.startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    rules["allow"].append(path)
        return rules

    def _is_allowed(self, rules: dict[str, list[str]], path: str) -> bool:
        """Check if path is allowed by robots.txt rules"""
        # Check explicit allows first
        for allow_path in rules.get("allow", []):
            if path.startswith(allow_path):
                return True

        # Check disallows
        for disallow_path in rules.get("disallow", []):
            if path.startswith(disallow_path):
                return False

        return True  # Default: allow

    async def check_rate_limit(self, source_type: SourceType, domain: str) -> bool:
        """Check if rate limit allows request"""
        rate_limit = self.RATE_LIMITS.get(source_type, 1.0)  # Default: 1 req/sec
        key = f"{source_type}:{domain}"

        now = datetime.now().timestamp()

        # Get recent requests
        if key not in self.rate_limit_tracker:
            self.rate_limit_tracker[key] = []

        recent_requests = self.rate_limit_tracker[key]

        # Remove old requests (>60s ago)
        recent_requests = [t for t in recent_requests if now - t < 60]

        # Calculate requests per second
        if len(recent_requests) > 0:
            time_span = now - recent_requests[0]
            if time_span > 0:
                current_rate = len(recent_requests) / time_span
                if current_rate > rate_limit:
                    return False  # Rate limit exceeded

        # Add current request
        recent_requests.append(now)
        self.rate_limit_tracker[key] = recent_requests

        return True

    def scrub_pii(self, text: str) -> str:
        """Scrub PII from text"""
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", text, flags=re.IGNORECASE)
        return text


class GeminiTierClassifier:
    """
    Gemini 2.0 Pro-powered tier classification
    Classifies intelligence items into Tier 1/2/3
    """

    TIER_PROMPT_TEMPLATE = """You are an intelligence analyst for a geopolitical AI platform.
Classify the following article into Tier 1 (high-value), Tier 2 (medium), or Tier 3 (low).

Tier 1 Criteria:
- Breaking news with strategic implications
- Primary source documents (FOIA, filings, patents)
- Technical specifications for emerging technologies
- Regulatory changes affecting aviation/defense/telecom

Tier 2 Criteria:
- Industry analysis or trend reports
- Expert commentary with novel insights
- Tutorial content for specialized domains

Tier 3 Criteria:
- Social media discussions without primary sources
- Evergreen/timeless reference material
- Duplicate or redundant information

Article Title: {title}
Article Summary: {summary}
Article Tags: {tags}
Source Domain: {domain}

Output JSON (no additional text):
{{
  "tier": 1-3,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation",
  "tags": ["tag1", "tag2", ...]
}}
"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        if genai and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        else:
            self.model = None  # Fallback to rule-based classification

    async def classify(
        self, title: str, summary: str, tags: list[str], domain: str
    ) -> TierClassification:
        """Classify item into Tier 1/2/3"""

        if self.model:
            # Use Gemini 2.0 Pro for classification
            try:
                prompt = self.TIER_PROMPT_TEMPLATE.format(
                    title=title,
                    summary=summary or "N/A",
                    tags=", ".join(tags) if tags else "N/A",
                    domain=domain,
                )

                response = self.model.generate_content(prompt)
                result_text = response.text.strip()

                # Parse JSON response (simplified - production would use proper JSON parsing)
                import json

                result = json.loads(result_text)

                return TierClassification(
                    tier=result["tier"],
                    confidence=result["confidence"],
                    reasoning=result["reasoning"],
                    tags=result["tags"],
                )
            except Exception:
                # Fallback to rule-based on error
                pass

        # Fallback: Rule-based classification
        return self._rule_based_classification(title, summary, tags, domain)

    def _rule_based_classification(
        self, title: str, summary: str, tags: list[str], domain: str
    ) -> TierClassification:
        """Fallback rule-based classification"""

        # Tier 1 indicators
        tier1_keywords = [
            "faa",
            "do-178",
            "regulation",
            "filing",
            "patent",
            "nprm",
            "proposed rule",
            "starlink",
            "gps spoofing",
            "breaking",
            "ransomware",
            "vulnerability",
        ]

        # Government/authoritative domains
        tier1_domains = [
            ".gov",
            "faa.gov",
            "fcc.gov",
            "defense.gov",
            "reuters.com",
            "bloomberg.com",
        ]

        text_lower = f"{title} {summary}".lower()

        # Check for Tier 1
        if any(kw in text_lower for kw in tier1_keywords) or any(
            d in domain for d in tier1_domains
        ):
            return TierClassification(
                tier=1,
                confidence=0.75,
                reasoning="Matches Tier 1 keywords or authoritative domain (rule-based fallback)",
                tags=tags or ["high-value"],
            )

        # Check for Tier 3 (low-value)
        tier3_keywords = ["opinion", "commentary", "social media", "evergreen"]
        if any(kw in text_lower for kw in tier3_keywords):
            return TierClassification(
                tier=3,
                confidence=0.70,
                reasoning="Matches Tier 3 keywords (rule-based fallback)",
                tags=tags or ["low-value"],
            )

        # Default: Tier 2
        return TierClassification(
            tier=2,
            confidence=0.65,
            reasoning="Default medium-value classification (rule-based fallback)",
            tags=tags or ["medium-value"],
        )


class IngestionService:
    """
    Main Gemini Ingestion Layer service
    Coordinates crawling, classification, and ethical compliance
    """

    def __init__(self, gemini_api_key: str | None = None):
        self.ethics_checker = EthicalComplianceChecker()
        self.tier_classifier = GeminiTierClassifier(api_key=gemini_api_key)
        self.storage: dict[
            str, dict
        ] = {}  # In-memory storage (replace with Cloud Storage in production)

    async def submit_item(self, request: IngestionSubmitRequest) -> str:
        """
        Submit an intelligence item for ingestion
        Returns: item_id
        """
        # Generate item ID
        item_id = self._generate_item_id(request)

        # Store item (in production, write to Cloud Storage)
        self.storage[item_id] = {
            "request": request.model_dump(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Trigger async processing (in production, use Cloud Tasks or Pub/Sub)
        asyncio.create_task(self._process_item(item_id, request))

        return item_id

    async def _process_item(self, item_id: str, request: IngestionSubmitRequest):
        """Process intelligence item (classify + validate ethics)"""
        try:
            # Update status
            self.storage[item_id]["status"] = "processing"

            # Check ethical compliance
            url_allowed = await self.ethics_checker.check_robots_txt(str(request.source.url))
            rate_ok = await self.ethics_checker.check_rate_limit(
                request.source.type, request.source.domain
            )

            if not url_allowed or not rate_ok:
                self.storage[item_id]["status"] = "failed"
                self.storage[item_id]["error"] = "Ethical compliance violation"
                return

            # Scrub PII
            clean_text = self.ethics_checker.scrub_pii(request.content.full_text)
            clean_summary = self.ethics_checker.scrub_pii(request.content.summary or "")

            # Classify tier
            classification = await self.tier_classifier.classify(
                title=request.content.title,
                summary=clean_summary,
                tags=request.metadata.tags,
                domain=request.source.domain,
            )

            # Store results
            self.storage[item_id]["status"] = "completed"
            self.storage[item_id]["classification"] = classification.model_dump()
            self.storage[item_id]["processed_at"] = datetime.utcnow().isoformat()

        except Exception as e:
            self.storage[item_id]["status"] = "failed"
            self.storage[item_id]["error"] = str(e)

    def _generate_item_id(self, request: IngestionSubmitRequest) -> str:
        """Generate unique item ID"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        content_hash = hashlib.blake2b(
            request.content.full_text.encode(), digest_size=4
        ).hexdigest()
        return f"ing_{timestamp}_{content_hash}"

    async def get_item(self, item_id: str) -> dict | None:
        """Retrieve item by ID"""
        return self.storage.get(item_id)

    async def get_source_health(self) -> list[SourceHealth]:
        """Get health status of all configured sources"""
        # Mock data (in production, query from database/monitoring)
        return [
            SourceHealth(
                id="youtube-api-v3",
                type=SourceType.YOUTUBE,
                status="healthy",
                daily_quota=10000,
                quota_used=7234,
                last_successful_fetch=datetime.utcnow() - timedelta(minutes=30),
                tier_1_yield=0.18,
            ),
            SourceHealth(
                id="twitter-basic",
                type=SourceType.TWITTER,
                status="rate_limited",
                daily_quota=15000,
                quota_used=15000,
                last_successful_fetch=datetime.utcnow() - timedelta(hours=2),
                tier_1_yield=0.11,
            ),
        ]
