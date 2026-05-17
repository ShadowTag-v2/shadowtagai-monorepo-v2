# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
arXiv Paper Crawler
Discovers and downloads relevant AI/MLOps research papers
"""

import asyncio
from pathlib import Path
from datetime import datetime, timedelta

import arxiv
import structlog

from ..config import ARXIV_CONFIG, STORAGE_CONFIG
from .ethical_scraper import EthicalScraper

logger = structlog.get_logger(__name__)


class ArxivCrawler:
  """
  Ethical arXiv paper discovery and download

  Features:
  - Category-based search (cs.AI, cs.LG, etc.)
  - Keyword filtering for MLOps relevance
  - Time-based filtering (recent papers)
  - PDF and metadata download
  - Rate-limited API access
  """

  def __init__(self):
    self.config = ARXIV_CONFIG
    self.storage_path = Path(STORAGE_CONFIG["arxiv_papers"]["path"])
    self.storage_path.mkdir(parents=True, exist_ok=True)
    self.scraper = EthicalScraper()

    logger.info(
      "arxiv_crawler_initialized",
      categories=self.config["categories"],
      storage_path=str(self.storage_path),
    )

  def search_papers(
    self,
    categories: list[str] | None = None,
    search_terms: list[str] | None = None,
    max_results: int | None = None,
    days_back: int | None = None,
  ) -> list[arxiv.Result]:
    """
    Search for papers on arXiv

    Args:
        categories: arXiv categories (e.g., ["cs.AI", "cs.LG"])
        search_terms: Keywords to search for
        max_results: Maximum results per category
        days_back: Only include papers from last N days

    Returns:
        List of arxiv.Result objects
    """
    categories = categories or self.config["categories"]
    search_terms = search_terms or self.config["search_terms"]
    max_results = max_results or self.config["max_results_per_category"]
    days_back = days_back or self.config["days_back"]

    cutoff_date = datetime.now() - timedelta(days=days_back)
    all_papers: dict[str, arxiv.Result] = {}  # Dedupe by entry_id

    for category in categories:
      for search_term in search_terms:
        try:
          # Build query: category AND keywords
          query = f"cat:{category} AND all:{search_term}"

          logger.info(
            "searching_arxiv", category=category, search_term=search_term, query=query
          )

          # Search arXiv
          search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
          )

          for result in search.results():
            # Filter by date
            if result.published < cutoff_date:
              continue

            # Deduplicate
            if result.entry_id not in all_papers:
              all_papers[result.entry_id] = result
              logger.debug(
                "paper_found",
                title=result.title,
                authors=result.authors[0].name if result.authors else "N/A",
                published=result.published.isoformat(),
                category=category,
              )

          # Rate limiting - be nice to arXiv
          asyncio.run(asyncio.sleep(3))

        except Exception as e:
          logger.error(
            "arxiv_search_error",
            category=category,
            search_term=search_term,
            error=str(e),
          )
          continue

    logger.info(
      "arxiv_search_complete",
      total_papers=len(all_papers),
      categories=categories,
      days_back=days_back,
    )

    return list(all_papers.values())

  def format_paper_metadata(self, paper: arxiv.Result) -> str:
    """
    Format paper metadata as markdown

    Returns a structured text representation of the paper
    """
    authors = ", ".join([author.name for author in paper.authors[:5]])
    if len(paper.authors) > 5:
      authors += " et al."

    categories = ", ".join(paper.categories)

    metadata = f"""
# {paper.title}

**Authors:** {authors}
**Published:** {paper.published.strftime("%Y-%m-%d")}
**Updated:** {paper.updated.strftime("%Y-%m-%d")}
**Categories:** {categories}
**arXiv ID:** {paper.entry_id.split("/")[-1]}
**PDF URL:** {paper.pdf_url}
**Abstract URL:** {paper.entry_id}

## Abstract

{paper.summary}

## Links

- [PDF]({paper.pdf_url})
- [Abstract]({paper.entry_id})
- [Comments]({paper.comment if paper.comment else "N/A"})

## Primary Category

{paper.primary_category}

## All Categories

{categories}

---
"""
    return metadata

  def download_paper(
    self, paper: arxiv.Result, download_pdf: bool = True
  ) -> str | None:
    """
    Download paper metadata and optionally PDF

    Args:
        paper: arXiv Result object
        download_pdf: Whether to download PDF file

    Returns:
        Path to metadata file, or None if failed
    """
    try:
      # Create safe filename from arxiv ID
      arxiv_id = paper.entry_id.split("/")[-1]
      safe_id = arxiv_id.replace(".", "_").replace(":", "_")

      # Save metadata
      metadata_file = self.storage_path / f"{safe_id}_metadata.md"
      metadata = self.format_paper_metadata(paper)
      metadata_file.write_text(metadata, encoding="utf-8")

      logger.info(
        "paper_metadata_saved",
        arxiv_id=arxiv_id,
        title=paper.title,
        file=str(metadata_file),
      )

      # Download PDF if requested
      if download_pdf:
        pdf_file = self.storage_path / f"{safe_id}.pdf"

        # Use arXiv's download method (handles rate limiting)
        try:
          paper.download_pdf(dirpath=str(self.storage_path), filename=f"{safe_id}.pdf")
          logger.info("paper_pdf_downloaded", arxiv_id=arxiv_id, file=str(pdf_file))
        except Exception as pdf_error:
          logger.warning("pdf_download_error", arxiv_id=arxiv_id, error=str(pdf_error))

      return str(metadata_file)

    except Exception as e:
      logger.error("paper_download_error", arxiv_id=paper.entry_id, error=str(e))
      return None

  def download_papers(
    self,
    papers: list[arxiv.Result] | None = None,
    download_pdfs: bool = False,
    **search_kwargs,
  ) -> list[str]:
    """
    Download multiple papers

    Args:
        papers: List of arxiv.Result objects (if None, will search)
        download_pdfs: Whether to download PDF files
        **search_kwargs: Arguments to pass to search_papers()

    Returns:
        List of paths to metadata files
    """
    if papers is None:
      papers = self.search_papers(**search_kwargs)

    downloaded_files = []

    for i, paper in enumerate(papers, 1):
      logger.info("downloading_paper", index=i, total=len(papers), title=paper.title)

      # Rate limiting - arXiv requests 3 seconds between requests
      if i > 1:
        asyncio.run(asyncio.sleep(3))

      metadata_file = self.download_paper(paper, download_pdf=download_pdfs)
      if metadata_file:
        downloaded_files.append(metadata_file)

    logger.info(
      "papers_download_complete",
      total_papers=len(papers),
      successful=len(downloaded_files),
    )

    return downloaded_files

  def get_recent_papers(
    self, days_back: int | None = None, download_pdfs: bool = False
  ) -> list[str]:
    """
    Convenience method to get recent papers across all configured categories

    Args:
        days_back: Number of days to look back
        download_pdfs: Whether to download PDF files

    Returns:
        List of paths to downloaded metadata files
    """
    return self.download_papers(days_back=days_back, download_pdfs=download_pdfs)

  def search_by_keywords(
    self,
    keywords: list[str],
    max_results: int = 50,
    days_back: int = 30,
    download_pdfs: bool = False,
  ) -> list[str]:
    """
    Search for papers by specific keywords

    Args:
        keywords: List of search terms
        max_results: Maximum results per keyword
        days_back: Only include papers from last N days
        download_pdfs: Whether to download PDF files

    Returns:
        List of paths to downloaded metadata files
    """
    return self.download_papers(
      search_terms=keywords,
      max_results=max_results,
      days_back=days_back,
      download_pdfs=download_pdfs,
    )

  def generate_summary(self, papers: list[arxiv.Result]) -> str:
    """
    Generate a summary of discovered papers

    Returns:
        Markdown-formatted summary
    """
    summary_parts = [
      "# arXiv Paper Discovery Summary",
      f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      f"**Total Papers:** {len(papers)}",
      "\n## Papers by Category\n",
    ]

    # Group by primary category
    by_category: dict[str, list[arxiv.Result]] = {}
    for paper in papers:
      cat = paper.primary_category
      if cat not in by_category:
        by_category[cat] = []
      by_category[cat].append(paper)

    for category, cat_papers in sorted(by_category.items()):
      summary_parts.append(f"### {category} ({len(cat_papers)} papers)\n")
      for paper in cat_papers[:10]:  # Top 10 per category
        authors = paper.authors[0].name if paper.authors else "N/A"
        summary_parts.append(
          f"- **{paper.title}** - {authors} et al. ({paper.published.strftime('%Y-%m-%d')})"
        )
      if len(cat_papers) > 10:
        summary_parts.append(f"- ... and {len(cat_papers) - 10} more\n")
      summary_parts.append("")

    return "\n".join(summary_parts)


# Convenience functions
def crawl_recent_papers(days_back: int = 7, download_pdfs: bool = False) -> list[str]:
  """
  Crawl arXiv for recent papers

  Usage:
      metadata_files = crawl_recent_papers(days_back=7)
  """
  crawler = ArxivCrawler()
  return crawler.get_recent_papers(days_back=days_back, download_pdfs=download_pdfs)


def search_arxiv(keywords: list[str], days_back: int = 30) -> list[str]:
  """
  Search arXiv by keywords

  Usage:
      files = search_arxiv(["MLOps", "LLM serving"], days_back=30)
  """
  crawler = ArxivCrawler()
  return crawler.search_by_keywords(keywords, days_back=days_back)
