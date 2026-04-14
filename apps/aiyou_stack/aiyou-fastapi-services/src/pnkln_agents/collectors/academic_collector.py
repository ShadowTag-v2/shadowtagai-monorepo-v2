"""Academic arXiv Collector
Collects research papers from arXiv.org
"""

from datetime import datetime
from typing import Any

try:
    import arxiv

    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

from ..core.gemini_ingestion import IngestedItem, Source
from .base import BaseCollector


class AcademicCollector(BaseCollector):
    """arXiv.org academic paper collector

    Pricing: FREE
    Rate Limits: 1 request per 3 seconds (to be respectful)
    """

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        super().__init__(api_key, config)

        if not ARXIV_AVAILABLE:
            raise ImportError("arxiv not installed. Run: pip install arxiv")

        self.rate_limit_delay = 3.0  # 3 seconds between requests
        self.cost_per_request = 0.0  # arXiv is free

    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """Collect research papers from arXiv

        Searches for AI/ML papers from past 30 days
        """
        items = []

        try:
            query = self.config.get(
                "search_query", "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV",
            )
            max_results = min(target_count, 100)

            # Search arXiv
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            for paper in search.results():
                # Calculate relevance based on categories and keywords
                relevance = self._calculate_relevance(paper)

                item = IngestedItem(
                    item_id=f"arxiv_{paper.entry_id.split('/')[-1]}",
                    source=source,
                    title=paper.title,
                    content=paper.summary[:500],  # First 500 chars of abstract
                    url=paper.entry_id,
                    ingested_at=datetime.utcnow(),
                    relevance_score=relevance,
                    timeliness_score=self._calculate_timeliness(paper.published),
                    completeness_score=1.0,  # Academic papers have full metadata
                    cost_usd=self.cost_per_request,
                    metadata={
                        "source_url": source.url,
                        "source_type": source.source_type.value,
                        "tier": source.tier.value,
                        "arxiv_id": paper.entry_id.split("/")[-1],
                        "authors": [str(author) for author in paper.authors],
                        "categories": paper.categories,
                        "published": paper.published.isoformat(),
                        "updated": paper.updated.isoformat() if paper.updated else None,
                        "pdf_url": paper.pdf_url,
                    },
                )
                items.append(item)

            self._respect_rate_limit()

        except Exception as e:
            print(f"arXiv API error: {e}")

        return items

    def _calculate_relevance(self, paper) -> float:
        """Calculate relevance based on categories and title/abstract"""
        relevance = 0.7  # Base for arXiv papers (high quality)

        # Boost for AI-specific categories
        ai_categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]
        if any(cat in paper.categories for cat in ai_categories):
            relevance += 0.15

        # Boost for agent/LLM keywords in title
        title_lower = paper.title.lower()
        agent_keywords = ["agent", "llm", "language model", "transformer", "gpt"]
        if any(kw in title_lower for kw in agent_keywords):
            relevance += 0.15

        return min(relevance, 1.0)

    def _calculate_timeliness(self, published: datetime) -> float:
        """Calculate timeliness score"""
        age_days = (datetime.utcnow() - published.replace(tzinfo=None)).days

        if age_days <= 7:
            return 1.0
        if age_days <= 14:
            return 0.9
        if age_days <= 30:
            return 0.7
        return 0.5
