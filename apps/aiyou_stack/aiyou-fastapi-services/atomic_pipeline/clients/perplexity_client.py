# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Perplexity Sonar API Client
============================
Deep research and citation-backed responses.

Specs:
- Model: sonar-pro (200K context)
- Pricing: $5/1K searches, $3/M input, $15/M output
- Strengths: Web search, citations, research synthesis
"""

import logging
import os
from enum import StrEnum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SonarModel(StrEnum):
    """Available Perplexity Sonar models"""

    SONAR_PRO = "sonar-pro"
    SONAR = "sonar"
    SONAR_REASONING_PRO = "sonar-reasoning-pro"
    SONAR_REASONING = "sonar-reasoning"


class PerplexityConfig(BaseModel):
    """Configuration for Perplexity API client"""

    api_key: str = Field(default_factory=lambda: os.getenv("PERPLEXITY_API_KEY", ""))
    base_url: str = "https://api.perplexity.ai"
    model: SonarModel = SonarModel.SONAR_PRO
    max_tokens: int = 4096
    temperature: float = 0.2  # Lower for factual accuracy
    timeout: float = 120.0

    # Search settings
    search_domain_filter: list[str] = Field(default_factory=list)
    search_recency_filter: str | None = None  # "day", "week", "month", "year"
    return_citations: bool = True
    return_images: bool = False


class Citation(BaseModel):
    """Citation from Perplexity search"""

    url: str
    title: str | None = None
    snippet: str | None = None


class PerplexityResponse(BaseModel):
    """Structured response from Perplexity"""

    content: str
    model: str
    usage: dict[str, int]
    citations: list[Citation] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    finish_reason: str = "stop"


class PerplexityClient:
    """Perplexity Sonar API Client.

    Used in the atomic pipeline for:
    - Deep research with citations
    - Technical documentation lookup
    - API reference gathering
    - Best practices research
    """

    def __init__(self, config: PerplexityConfig | None = None):
        self.config = config or PerplexityConfig()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.config.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    async def search(
        self,
        query: str,
        system_prompt: str | None = None,
        recency_filter: str | None = None,
        domain_filter: list[str] | None = None,
    ) -> PerplexityResponse:
        """Perform a search query with Perplexity.

        Args:
            query: Search query
            system_prompt: Optional system instructions
            recency_filter: Time filter ("day", "week", "month", "year")
            domain_filter: Limit search to specific domains

        Returns:
            PerplexityResponse with content and citations

        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": query})

        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "return_citations": self.config.return_citations,
            "return_images": self.config.return_images,
        }

        if recency_filter or self.config.search_recency_filter:
            payload["search_recency_filter"] = recency_filter or self.config.search_recency_filter

        if domain_filter or self.config.search_domain_filter:
            payload["search_domain_filter"] = domain_filter or self.config.search_domain_filter

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]

        # Parse citations
        citations = []
        if "citations" in data:
            for url in data["citations"]:
                citations.append(Citation(url=url))

        return PerplexityResponse(
            content=choice["message"]["content"],
            model=data["model"],
            usage=data.get("usage", {}),
            citations=citations,
            images=data.get("images", []),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def research_topic(
        self,
        topic: str,
        depth: str = "comprehensive",
        focus_areas: list[str] | None = None,
    ) -> PerplexityResponse:
        """Deep research on a topic with structured output.

        Args:
            topic: Topic to research
            depth: Research depth ("quick", "standard", "comprehensive")
            focus_areas: Specific areas to focus on

        Returns:
            PerplexityResponse with research findings

        """
        depth_instructions = {
            "quick": "Provide a brief overview with key points.",
            "standard": "Provide a balanced analysis with examples.",
            "comprehensive": "Provide in-depth analysis with multiple perspectives, examples, and citations.",
        }

        system_prompt = f"""You are a technical research assistant.
{depth_instructions.get(depth, depth_instructions["standard"])}
Always cite sources and provide actionable insights."""

        focus_text = ""
        if focus_areas:
            focus_text = "\n\nFocus areas:\n" + "\n".join(f"- {area}" for area in focus_areas)

        query = f"""Research topic: {topic}{focus_text}

Provide:
1. Overview and current state
2. Key technologies/approaches
3. Best practices
4. Common pitfalls
5. Recommendations"""

        return await self.search(query, system_prompt=system_prompt)

    async def find_documentation(
        self,
        technology: str,
        specific_feature: str | None = None,
    ) -> PerplexityResponse:
        """Find official documentation for a technology.

        Args:
            technology: Technology to find docs for
            specific_feature: Specific feature or API to look up

        Returns:
            PerplexityResponse with documentation links and summaries

        """
        query = f"Official documentation for {technology}"
        if specific_feature:
            query += f" specifically for {specific_feature}"

        query += "\n\nProvide:\n- Official documentation links\n- Key API references\n- Code examples\n- Version-specific notes"

        return await self.search(
            query,
            domain_filter=[
                "docs.python.org",
                "developer.mozilla.org",
                "github.com",
                "readthedocs.io",
            ],
            recency_filter="month",
        )

    async def compare_technologies(
        self,
        technologies: list[str],
        use_case: str,
    ) -> PerplexityResponse:
        """Compare multiple technologies for a specific use case.

        Args:
            technologies: List of technologies to compare
            use_case: The use case for comparison

        Returns:
            PerplexityResponse with comparison analysis

        """
        tech_list = ", ".join(technologies)

        system_prompt = """You are a technical analyst specializing in technology comparisons.
Provide objective, data-driven comparisons with real benchmarks where available."""

        query = f"""Compare {tech_list} for use case: {use_case}

Comparison criteria:
1. Performance benchmarks
2. Learning curve
3. Community and ecosystem
4. Production readiness
5. Cost considerations
6. Specific strengths/weaknesses for this use case

Recommendation with justification."""

        return await self.search(query, system_prompt=system_prompt)
