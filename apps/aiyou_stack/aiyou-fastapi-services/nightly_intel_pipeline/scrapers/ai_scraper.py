# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AI-Powered Scraper Client
Unified interface for AI-powered web scraping services
Supports Firecrawl and Browse AI for 95%+ extraction accuracy
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class ScraperProvider(Enum):
    """Supported AI scraper providers"""

    FIRECRAWL = "firecrawl"
    BROWSE_AI = "browse_ai"
    HTTPX = "httpx"  # Fallback


# AI Scraper Configuration
AI_SCRAPER_CONFIG = {
    "firecrawl": {
        "enabled": True,
        "api_key_env": "FIRECRAWL_API_KEY",
        "base_url": "https://api.firecrawl.dev/v0",
        "cost_per_page": 0.005,  # $0.005/page
        "accuracy": 0.94,
        "rate_limit": 3.0,  # 3 seconds between requests
    },
    "browse_ai": {
        "enabled": True,
        "api_key_env": "BROWSE_AI_API_KEY",
        "base_url": "https://api.browse.ai/v2",
        "cost_per_page": 0.01,  # $0.01/page
        "accuracy": 0.95,
        "rate_limit": 5.0,
    },
    "httpx": {
        "enabled": True,  # Always available as fallback
        "cost_per_page": 0.0,
        "accuracy": 0.70,
        "rate_limit": 3.0,
    },
    "default_provider": "firecrawl",
    "fallback_chain": ["firecrawl", "browse_ai", "httpx"],
    "max_retries": 3,
    "timeout": 30.0,
}


@dataclass
class ScrapeResult:
    """Result from AI scraper"""

    url: str
    title: str
    content: str
    markdown: str
    html: str | None = None
    links: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    provider: str = "unknown"
    extraction_time: float = 0.0
    success: bool = True
    error: str | None = None


@dataclass
class StructuredData:
    """Structured data extracted using AI"""

    url: str
    schema_name: str
    data: dict[str, Any]
    confidence: float = 0.0
    provider: str = "unknown"


class AIScraperClient:
    """Unified interface for AI-powered scrapers

    Features:
    - Automatic provider selection based on availability
    - Fallback chain for reliability
    - Structured data extraction
    - Cost tracking
    - Rate limiting

    Usage:
        client = AIScraperClient()
        result = await client.scrape("https://example.com")
        structured = await client.extract_structured(
            "https://news.site.com",
            {"title": "string", "date": "date", "content": "string"}
        )
    """

    def __init__(self, provider: str | None = None, config: dict | None = None):
        """Initialize AI scraper client

        Args:
            provider: Specific provider to use (firecrawl, browse_ai, httpx)
            config: Optional override configuration

        """
        self.config = config or AI_SCRAPER_CONFIG
        self.provider = provider or self.config["default_provider"]
        self.fallback_chain = self.config["fallback_chain"]

        # API keys
        self._api_keys = {
            "firecrawl": os.getenv(self.config["firecrawl"]["api_key_env"], ""),
            "browse_ai": os.getenv(self.config["browse_ai"]["api_key_env"], ""),
        }

        # Cost tracking
        self._total_cost = 0.0
        self._requests_count = 0

        # Determine available providers
        self._available_providers = self._check_available_providers()

        logger.info(
            "ai_scraper_initialized",
            primary_provider=self.provider,
            available_providers=self._available_providers,
        )

    def _check_available_providers(self) -> list[str]:
        """Check which providers are available"""
        available = []

        if self.config["firecrawl"]["enabled"] and self._api_keys.get("firecrawl"):
            available.append("firecrawl")

        if self.config["browse_ai"]["enabled"] and self._api_keys.get("browse_ai"):
            available.append("browse_ai")

        # httpx always available as fallback
        available.append("httpx")

        return available

    def _get_best_provider(self) -> str:
        """Get best available provider from fallback chain"""
        for provider in self.fallback_chain:
            if provider in self._available_providers:
                return provider
        return "httpx"  # Always have httpx

    async def scrape(
        self,
        url: str,
        wait_for: str | None = None,
        include_html: bool = False,
    ) -> ScrapeResult:
        """Scrape URL using AI-powered extraction

        Args:
            url: URL to scrape
            wait_for: Optional CSS selector to wait for (for JS-rendered content)
            include_html: Include raw HTML in result

        Returns:
            ScrapeResult with extracted content

        """
        provider = self._get_best_provider()
        start_time = datetime.now()

        try:
            if provider == "firecrawl":
                result = await self._scrape_firecrawl(url, wait_for, include_html)
            elif provider == "browse_ai":
                result = await self._scrape_browse_ai(url, wait_for, include_html)
            else:
                result = await self._scrape_httpx(url, include_html)

            result.provider = provider
            result.extraction_time = (datetime.now() - start_time).total_seconds()

            # Track cost
            cost = self.config[provider]["cost_per_page"]
            self._total_cost += cost
            self._requests_count += 1

            logger.info(
                "scrape_complete",
                url=url,
                provider=provider,
                time=result.extraction_time,
                cost=cost,
            )

            return result

        except Exception as e:
            logger.error("scrape_error", url=url, provider=provider, error=str(e))

            # Try fallback
            fallback_idx = (
                self.fallback_chain.index(provider) if provider in self.fallback_chain else -1
            )
            for fallback in self.fallback_chain[fallback_idx + 1 :]:
                if fallback in self._available_providers:
                    logger.info("scrape_fallback", url=url, fallback_provider=fallback)
                    try:
                        if fallback == "httpx":
                            return await self._scrape_httpx(url, include_html)
                    except Exception:
                        continue

            # Return error result
            return ScrapeResult(
                url=url,
                title="",
                content="",
                markdown="",
                success=False,
                error=str(e),
            )

    async def _scrape_firecrawl(
        self,
        url: str,
        wait_for: str | None,
        include_html: bool,
    ) -> ScrapeResult:
        """Scrape using Firecrawl API"""
        api_key = self._api_keys["firecrawl"]
        base_url = self.config["firecrawl"]["base_url"]

        # Rate limiting
        await asyncio.sleep(self.config["firecrawl"]["rate_limit"])

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/scrape",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "url": url,
                    "pageOptions": {"waitFor": wait_for, "includeHtml": include_html},
                },
                timeout=self.config["timeout"],
            )

            if response.status_code != 200:
                raise Exception(f"Firecrawl API error: {response.status_code}")

            data = response.json()
            result = data.get("data", {})

            return ScrapeResult(
                url=url,
                title=result.get("metadata", {}).get("title", ""),
                content=result.get("content", ""),
                markdown=result.get("markdown", ""),
                html=result.get("html") if include_html else None,
                links=result.get("links", []),
                images=result.get("metadata", {}).get("images", []),
                metadata=result.get("metadata", {}),
            )

    async def _scrape_browse_ai(
        self,
        url: str,
        wait_for: str | None,
        include_html: bool,
    ) -> ScrapeResult:
        """Scrape using Browse AI API"""
        api_key = self._api_keys["browse_ai"]
        base_url = self.config["browse_ai"]["base_url"]

        # Rate limiting
        await asyncio.sleep(self.config["browse_ai"]["rate_limit"])

        async with httpx.AsyncClient() as client:
            # Browse AI uses robot tasks - create a quick scrape task
            response = await client.post(
                f"{base_url}/robots/quick-scrape",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"url": url, "waitTime": 5000 if wait_for else 0},
                timeout=self.config["timeout"],
            )

            if response.status_code != 200:
                raise Exception(f"Browse AI API error: {response.status_code}")

            data = response.json()

            return ScrapeResult(
                url=url,
                title=data.get("title", ""),
                content=data.get("text", ""),
                markdown=data.get("markdown", data.get("text", "")),
                html=data.get("html") if include_html else None,
                links=data.get("links", []),
                metadata=data.get("metadata", {}),
            )

    async def _scrape_httpx(self, url: str, include_html: bool) -> ScrapeResult:
        """Fallback scraping using httpx"""
        # Rate limiting
        await asyncio.sleep(self.config["httpx"]["rate_limit"])

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": "NightlyIntelBot/1.0 (Research; AI Scraper Fallback)"},
                follow_redirects=True,
                timeout=self.config["timeout"],
            )

            if response.status_code != 200:
                raise Exception(f"HTTP error: {response.status_code}")

            html = response.text

            # Basic HTML to text extraction
            # In production, use BeautifulSoup or similar
            import re

            # Extract title
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""

            # Remove script and style tags
            clean_html = re.sub(r"<script.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
            clean_html = re.sub(
                r"<style.*?</style>",
                "",
                clean_html,
                flags=re.IGNORECASE | re.DOTALL,
            )

            # Extract text content
            content = re.sub(r"<[^>]+>", " ", clean_html)
            content = re.sub(r"\s+", " ", content).strip()

            # Extract links
            links = re.findall(r'href=["\']([^"\']+)["\']', html)

            return ScrapeResult(
                url=url,
                title=title,
                content=content[:10000],  # Limit content size
                markdown=content[:10000],
                html=html if include_html else None,
                links=links[:50],  # Limit links
            )

    async def extract_structured(self, url: str, schema: dict[str, str]) -> StructuredData:
        """Extract structured data using AI

        Args:
            url: URL to extract from
            schema: Schema definition {"field_name": "type", ...}
                   Types: string, number, date, url, list

        Returns:
            StructuredData with extracted fields

        """
        provider = self._get_best_provider()

        if provider == "firecrawl":
            return await self._extract_firecrawl(url, schema)
        # Fall back to basic scrape + heuristic extraction
        result = await self.scrape(url)
        return self._heuristic_extract(result, schema)

    async def _extract_firecrawl(self, url: str, schema: dict[str, str]) -> StructuredData:
        """Use Firecrawl's extraction mode"""
        api_key = self._api_keys["firecrawl"]
        base_url = self.config["firecrawl"]["base_url"]

        await asyncio.sleep(self.config["firecrawl"]["rate_limit"])

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/scrape",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "url": url,
                    "extractorOptions": {"mode": "llm-extraction", "extractionSchema": schema},
                },
                timeout=self.config["timeout"],
            )

            data = response.json()
            extracted = data.get("data", {}).get("llm_extraction", {})

            return StructuredData(
                url=url,
                schema_name="custom",
                data=extracted,
                confidence=0.94,
                provider="firecrawl",
            )

    def _heuristic_extract(self, result: ScrapeResult, schema: dict[str, str]) -> StructuredData:
        """Basic heuristic extraction for fallback"""
        import re

        data = {}
        content = result.content

        for field, field_type in schema.items():  # noqa: F402
            if field_type == "string":
                # Try to find field in content
                if field.lower() in ["title", "headline"]:
                    data[field] = result.title
                else:
                    data[field] = content[:500]

            elif field_type == "date":
                # Try to find date pattern
                date_patterns = [
                    r"\d{4}-\d{2}-\d{2}",
                    r"\d{1,2}/\d{1,2}/\d{4}",
                    r"[A-Z][a-z]+ \d{1,2}, \d{4}",
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, content)
                    if match:
                        data[field] = match.group(0)
                        break

            elif field_type == "url":
                if result.links:
                    data[field] = result.links[0]

            elif field_type == "number":
                numbers = re.findall(r"\d+\.?\d*", content)
                if numbers:
                    data[field] = float(numbers[0])

            elif field_type == "list":
                data[field] = []

        return StructuredData(
            url=result.url,
            schema_name="heuristic",
            data=data,
            confidence=0.5,
            provider=result.provider,
        )

    def get_stats(self) -> dict:
        """Get client statistics"""
        return {
            "total_cost": self._total_cost,
            "requests_count": self._requests_count,
            "average_cost_per_request": self._total_cost / max(self._requests_count, 1),
            "provider": self.provider,
            "available_providers": self._available_providers,
        }


# Convenience functions
async def ai_scrape(url: str, provider: str | None = None) -> ScrapeResult:
    """Quick AI-powered scrape

    Usage:
        result = await ai_scrape("https://example.com")
        print(result.markdown)
    """
    client = AIScraperClient(provider=provider)
    return await client.scrape(url)


async def ai_extract(url: str, schema: dict[str, str]) -> StructuredData:
    """Quick structured extraction

    Usage:
        data = await ai_extract(
            "https://news.site.com/article",
            {"title": "string", "date": "date", "author": "string"}
        )
        print(data.data)
    """
    client = AIScraperClient()
    return await client.extract_structured(url, schema)
