# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
arXiv Paper Aggregator
Discovers and downloads research papers from arXiv across targeted categories
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import arxiv
from dataclasses import dataclass

from pnkln_intelligence.config import ArxivSettings

logger = logging.getLogger(__name__)


@dataclass
class ArxivPaper:
    """Represents an arXiv paper with metadata"""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: datetime
    updated: datetime
    pdf_url: str
    entry_id: str
    doi: str | None = None
    journal_ref: str | None = None
    primary_category: str | None = None
    comment: str | None = None


class ArxivAggregator:
    """
    Aggregates research papers from arXiv using the arxiv.py library

    Supports:
    - Multi-category searches (cs.AI, cs.LG, cs.CL, cs.DC, cs.SE)
    - Date-range filtering
    - Keyword-based queries
    - PDF downloads
    - Rate limiting (3-second delay between requests)
    """

    def __init__(self, settings: ArxivSettings | None = None):
        self.settings = settings or ArxivSettings()
        self.client = arxiv.Client(
            page_size=self.settings.max_results_per_query, delay_seconds=self.settings.delay_seconds, num_retries=self.settings.num_retries
        )
        self.papers_dir = Path(self.settings.papers_directory)
        self.papers_dir.mkdir(parents=True, exist_ok=True)

    def build_query(
        self,
        categories: list[str] | None = None,
        keywords: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> str:
        """
        Build arXiv API query string

        Args:
            categories: List of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
            keywords: List of keywords to search in title/abstract
            start_date: Start date for filtering papers
            end_date: End date for filtering papers

        Returns:
            Query string for arXiv API
        """
        query_parts = []

        # Category query
        categories = categories or self.settings.categories
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query_parts.append(f"({cat_query})")

        # Keyword query
        if keywords:
            keyword_query = " OR ".join([f'(ti:"{kw}" OR abs:"{kw}")' for kw in keywords])
            query_parts.append(f"({keyword_query})")

        # Combine with AND
        query = " AND ".join(query_parts)

        # Date filtering (handled separately in arXiv API v1)
        # Note: arxiv.py doesn't directly support date filtering in query string
        # We'll filter results post-retrieval

        logger.info(f"Built arXiv query: {query}")
        return query

    async def search_papers(
        self,
        categories: list[str] | None = None,
        keywords: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_results: int = 100,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate,
        sort_order: arxiv.SortOrder = arxiv.SortOrder.Descending,
    ) -> list[ArxivPaper]:
        """
        Search for papers matching criteria

        Args:
            categories: arXiv categories to search
            keywords: Keywords to search for
            start_date: Filter papers after this date
            end_date: Filter papers before this date
            max_results: Maximum number of results
            sort_by: Sort criterion
            sort_order: Sort order

        Returns:
            List of ArxivPaper objects
        """
        query = self.build_query(categories, keywords, start_date, end_date)

        search = arxiv.Search(query=query, max_results=max_results, sort_by=sort_by, sort_order=sort_order)

        papers = []
        try:
            for result in self.client.results(search):
                # Apply date filtering if specified
                if start_date and result.published < start_date:
                    continue
                if end_date and result.published > end_date:
                    continue

                paper = ArxivPaper(
                    arxiv_id=result.get_short_id(),
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published=result.published,
                    updated=result.updated,
                    pdf_url=result.pdf_url,
                    entry_id=result.entry_id,
                    doi=result.doi,
                    journal_ref=result.journal_ref,
                    primary_category=result.primary_category,
                    comment=result.comment,
                )
                papers.append(paper)

                logger.debug(f"Found paper: {paper.arxiv_id} - {paper.title}")

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}", exc_info=True)
            raise

        logger.info(f"Retrieved {len(papers)} papers from arXiv")
        return papers

    async def download_pdf(self, paper: ArxivPaper, output_dir: Path | None = None) -> Path | None:
        """
        Download PDF for a paper

        Args:
            paper: ArxivPaper object
            output_dir: Output directory (defaults to self.papers_dir)

        Returns:
            Path to downloaded PDF or None if failed
        """
        if not self.settings.download_pdf:
            return None

        output_dir = output_dir or self.papers_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Organize by year/month
        year_month_dir = output_dir / str(paper.published.year) / f"{paper.published.month:02d}"
        year_month_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = year_month_dir / f"{paper.arxiv_id}.pdf"

        if pdf_path.exists():
            logger.debug(f"PDF already exists: {pdf_path}")
            return pdf_path

        try:
            # Create a search to get the result object
            search = arxiv.Search(id_list=[paper.arxiv_id])
            result = next(self.client.results(search))

            # Download PDF
            result.download_pdf(dirpath=str(year_month_dir), filename=f"{paper.arxiv_id}.pdf")
            logger.info(f"Downloaded PDF: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"Error downloading PDF for {paper.arxiv_id}: {e}", exc_info=True)
            return None

    async def aggregate_recent_papers(
        self, days_back: int = 7, categories: list[str] | None = None, keywords: list[str] | None = None, download_pdfs: bool = True
    ) -> list[dict[str, Any]]:
        """
        Aggregate recent papers from the last N days

        Args:
            days_back: Number of days to look back
            categories: Categories to search
            keywords: Keywords to search for
            download_pdfs: Whether to download PDFs

        Returns:
            List of paper metadata dictionaries
        """
        start_date = datetime.now() - timedelta(days=days_back)
        papers = await self.search_papers(
            categories=categories, keywords=keywords, start_date=start_date, max_results=self.settings.max_results_per_query
        )

        results = []
        for paper in papers:
            paper_dict = {
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "categories": paper.categories,
                "published": paper.published.isoformat(),
                "updated": paper.updated.isoformat(),
                "pdf_url": paper.pdf_url,
                "entry_id": paper.entry_id,
                "doi": paper.doi,
                "journal_ref": paper.journal_ref,
                "primary_category": paper.primary_category,
                "comment": paper.comment,
                "pdf_path": None,
            }

            if download_pdfs:
                pdf_path = await self.download_pdf(paper)
                if pdf_path:
                    paper_dict["pdf_path"] = str(pdf_path)

            results.append(paper_dict)

        return results

    async def aggregate_by_category(self, category: str, max_results: int = 100) -> list[ArxivPaper]:
        """
        Aggregate papers for a specific category

        Args:
            category: arXiv category (e.g., 'cs.AI')
            max_results: Maximum results to retrieve

        Returns:
            List of ArxivPaper objects
        """
        return await self.search_papers(categories=[category], max_results=max_results)

    async def aggregate_llm_papers(self, days_back: int = 30) -> list[ArxivPaper]:
        """
        Aggregate LLM-related papers across relevant categories

        Args:
            days_back: Number of days to look back

        Returns:
            List of ArxivPaper objects
        """
        keywords = ["LLM", "large language model", "GPT", "BERT", "transformer", "inference optimization", "model serving", "efficient inference"]

        start_date = datetime.now() - timedelta(days=days_back)

        return await self.search_papers(categories=["cs.AI", "cs.LG", "cs.CL"], keywords=keywords, start_date=start_date, max_results=500)

    async def aggregate_ml_systems_papers(self, days_back: int = 30) -> list[ArxivPaper]:
        """
        Aggregate ML systems and infrastructure papers

        Args:
            days_back: Number of days to look back

        Returns:
            List of ArxivPaper objects
        """
        keywords = ["distributed training", "GPU optimization", "edge computing", "kubernetes", "MLOps", "model deployment", "inference serving"]

        start_date = datetime.now() - timedelta(days=days_back)

        return await self.search_papers(categories=["cs.DC", "cs.SE", "cs.LG"], keywords=keywords, start_date=start_date, max_results=500)


# Example usage
if __name__ == "__main__":

    async def main():
        aggregator = ArxivAggregator()

        # Get recent LLM papers
        papers = await aggregator.aggregate_llm_papers(days_back=7)
        print(f"Found {len(papers)} LLM papers from the last 7 days")

        for paper in papers[:5]:
            print(f"\n{paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Published: {paper.published}")
            print(f"Categories: {', '.join(paper.categories)}")

    asyncio.run(main())
