"""Nightly Intel Pipeline - Main Orchestration
Coordinates ingestion, normalization, scoring, and briefing generation

Enhanced with Gemini Normalization Layer (Step 1B) for structured IntelEvent extraction.
"""

import asyncio
import contextlib
from datetime import datetime
from pathlib import Path

import structlog

from app.models.intel_event import IntelEvent, IntelEventBatch

# Import Gemini normalizer for Step 1B
from app.services.gemini_normalizer import GeminiNormalizer

from .engines.jr_engine import JREngine
from .scrapers.arxiv_crawler import ArxivCrawler
from .scrapers.federal_register_crawler import FederalRegisterCrawler
from .scrapers.github_flattener import GitHubFlattener
from .scrapers.industry_crawler import IndustryCrawler
from .storage.briefing import BriefingGenerator
from .storage.database import IntelDatabase
from .utils.logging_setup import setup_logging

logger = structlog.get_logger(__name__)


class NightlyIntelPipeline:
    """Main pipeline orchestrator

    Execution steps:
    1A. Ingestion: Discover GitHub repos, arXiv papers, industry news, Federal Register
    1B. Gemini Normalization: Transform raw docs → structured IntelEvent objects
    2. JR Scoring: Evaluate IntelEvents using Purpose → Reasons → Brakes
    3. Tier Classification: Classify into tiers
    4. Storage: Store raw docs + IntelEvents + scores
    5. Briefing: Generate executive briefing with Gemini summaries
    """

    def __init__(self, enable_gemini_normalization: bool = True):
        setup_logging()

        self.github_flattener = GitHubFlattener()
        self.arxiv_crawler = ArxivCrawler()
        self.industry_crawler = IndustryCrawler()
        self.federal_register_crawler = FederalRegisterCrawler()
        self.jr_engine = JREngine()
        self.database = IntelDatabase()
        self.briefing_generator = BriefingGenerator(db=self.database)

        # Gemini normalization layer (Step 1B)
        self.enable_gemini_normalization = enable_gemini_normalization
        self.gemini_normalizer: GeminiNormalizer | None = None
        self.intel_events: list[IntelEvent] = []

        logger.info("pipeline_initialized", gemini_enabled=enable_gemini_normalization)

    def run_ingestion(
        self,
        github_topics: list[str] | None = None,
        arxiv_days_back: int | None = None,
        industry_days_back: int | None = None,
        federal_register_days_back: int | None = None,
        download_pdfs: bool = False,
        include_industry: bool = True,
        include_federal_register: bool = True,
    ) -> dict[str, list[str]]:
        """Step 1: Ingestion
        Discover and download content from GitHub, arXiv, industry sources, and Federal Register

        Returns:
            Dict with 'repos', 'papers', 'industry', and 'federal_register' file paths

        """
        logger.info("ingestion_started")

        results = {"repos": [], "papers": [], "industry": [], "federal_register": []}

        # GitHub ingestion
        try:
            logger.info("github_ingestion_started")

            # Search for repositories
            repos = self.github_flattener.search_repositories(topics=github_topics)
            logger.info("github_repos_discovered", count=len(repos))

            # Flatten repositories
            flattened_files = []
            for repo in repos:
                flattened_file = self.github_flattener.flatten_repository(repo)
                if flattened_file:
                    flattened_files.append(flattened_file)

            results["repos"] = flattened_files
            logger.info("github_ingestion_complete", count=len(flattened_files))

        except Exception as e:
            logger.error("github_ingestion_error", error=str(e))

        # arXiv ingestion
        try:
            logger.info("arxiv_ingestion_started")

            papers = self.arxiv_crawler.search_papers(days_back=arxiv_days_back)
            logger.info("arxiv_papers_discovered", count=len(papers))

            # Download paper metadata
            metadata_files = []
            for paper in papers:
                metadata_file = self.arxiv_crawler.download_paper(paper, download_pdf=download_pdfs)
                if metadata_file:
                    metadata_files.append(metadata_file)

            results["papers"] = metadata_files
            logger.info("arxiv_ingestion_complete", count=len(metadata_files))

        except Exception as e:
            logger.error("arxiv_ingestion_error", error=str(e))

        # Industry sources ingestion
        if include_industry:
            try:
                logger.info("industry_ingestion_started")
                import asyncio

                # Run async industry crawl
                articles = asyncio.run(
                    self.industry_crawler.crawl_all_verticals(days_back=industry_days_back or 30),
                )
                logger.info("industry_articles_discovered", count=len(articles))

                # Save articles and collect file paths
                article_files = self.industry_crawler.save_articles(articles)
                results["industry"] = article_files
                logger.info("industry_ingestion_complete", count=len(article_files))

            except Exception as e:
                logger.error("industry_ingestion_error", error=str(e))

        # Federal Register ingestion
        if include_federal_register:
            try:
                logger.info("federal_register_ingestion_started")
                import asyncio

                # Run async Federal Register fetch
                documents = asyncio.run(
                    self.federal_register_crawler.fetch_documents(
                        days_back=federal_register_days_back or 30,
                    ),
                )
                logger.info("federal_register_documents_discovered", count=len(documents))

                # Save documents and collect file paths
                document_files = self.federal_register_crawler.save_documents(documents)
                results["federal_register"] = document_files
                logger.info("federal_register_ingestion_complete", count=len(document_files))

            except Exception as e:
                logger.error("federal_register_ingestion_error", error=str(e))

        logger.info(
            "ingestion_complete",
            total_repos=len(results["repos"]),
            total_papers=len(results["papers"]),
            total_industry=len(results["industry"]),
            total_federal_register=len(results["federal_register"]),
        )

        return results

    async def run_normalization(self, ingestion_results: dict[str, list[str]]) -> IntelEventBatch:
        """Step 1B: Gemini Normalization
        Transform raw documents into structured IntelEvent objects

        Args:
            ingestion_results: Dict with file paths from run_ingestion()

        Returns:
            IntelEventBatch containing all extracted events

        """
        if not self.enable_gemini_normalization:
            logger.info("gemini_normalization_skipped", reason="disabled")
            return IntelEventBatch(
                events=[],
                batch_id="normalization_disabled",
                total_raw_documents=0,
                extraction_errors=0,
            )

        logger.info("gemini_normalization_started")

        documents = []

        # Collect all documents for normalization
        for file_path in ingestion_results.get("repos", []):
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                documents.append(
                    {
                        "text": content,
                        "url": f"github://{Path(file_path).stem}",
                        "source_hint": "github_repo",
                    },
                )
            except Exception as e:
                logger.error("doc_read_error", file=file_path, error=str(e))

        for file_path in ingestion_results.get("papers", []):
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                documents.append(
                    {
                        "text": content,
                        "url": f"arxiv://{Path(file_path).stem}",
                        "source_hint": "academic",
                    },
                )
            except Exception as e:
                logger.error("doc_read_error", file=file_path, error=str(e))

        for file_path in ingestion_results.get("industry", []):
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                # Extract URL from content if available
                url = f"industry://{Path(file_path).stem}"
                if "**URL:**" in content:
                    url = content.split("**URL:**")[1].split("\n")[0].strip()
                documents.append({"text": content, "url": url, "source_hint": "news"})
            except Exception as e:
                logger.error("doc_read_error", file=file_path, error=str(e))

        for file_path in ingestion_results.get("federal_register", []):
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                # Extract URL from content if available
                url = f"federal_register://{Path(file_path).stem}"
                if "**HTML URL:**" in content:
                    url = content.split("**HTML URL:**")[1].split("\n")[0].strip()
                documents.append({"text": content, "url": url, "source_hint": "regulation"})
            except Exception as e:
                logger.error("doc_read_error", file=file_path, error=str(e))

        logger.info("documents_collected_for_normalization", count=len(documents))

        if not documents:
            return IntelEventBatch(
                events=[], batch_id="empty_batch", total_raw_documents=0, extraction_errors=0,
            )

        # Run Gemini normalization
        async with GeminiNormalizer() as normalizer:
            batch = await normalizer.extract_batch(documents)

        # Store events for later use
        self.intel_events = batch.events

        logger.info(
            "gemini_normalization_complete",
            total_events=len(batch.events),
            errors=batch.extraction_errors,
            success_rate=f"{batch.success_rate:.1%}",
        )

        return batch

    def run_scoring(self, ingestion_results: dict[str, list[str]]):
        """Steps 2-3: JR Scoring and Tier Classification
        Score all ingested content and classify into tiers
        """
        logger.info("scoring_started")

        # Score GitHub repositories
        for i, repo_file in enumerate(ingestion_results["repos"], 1):
            try:
                logger.info(
                    "scoring_repo", index=i, total=len(ingestion_results["repos"]), file=repo_file,
                )

                # Read flattened content
                content = Path(repo_file).read_text(encoding="utf-8")

                # Extract repo name from file path
                repo_name = Path(repo_file).stem.replace("_flattened", "").replace("_", "/", 1)

                # Score with JR Engine
                score = self.jr_engine.score_github_repo(content, repo_name)

                # Extract metadata from content
                metadata = self._extract_repo_metadata(content)
                metadata["flattened_file_path"] = repo_file

                # Store in database
                self.database.store_repository_score(repo_name, score, metadata)

            except Exception as e:
                logger.error("repo_scoring_error", file=repo_file, error=str(e))

        logger.info("repo_scoring_complete", count=len(ingestion_results["repos"]))

        # Score arXiv papers
        for i, paper_file in enumerate(ingestion_results["papers"], 1):
            try:
                logger.info(
                    "scoring_paper",
                    index=i,
                    total=len(ingestion_results["papers"]),
                    file=paper_file,
                )

                # Read metadata
                content = Path(paper_file).read_text(encoding="utf-8")

                # Extract paper ID from file path
                paper_id = Path(paper_file).stem.replace("_metadata", "").replace("_", ".")

                # Score with JR Engine
                score = self.jr_engine.score_arxiv_paper(content, paper_id)

                # Extract metadata
                metadata = self._extract_paper_metadata(content)
                metadata["metadata_file_path"] = paper_file

                # Store in database
                self.database.store_paper_score(paper_id, score, metadata)

            except Exception as e:
                logger.error("paper_scoring_error", file=paper_file, error=str(e))

        logger.info("paper_scoring_complete", count=len(ingestion_results["papers"]))

        # Score industry articles
        for i, article_file in enumerate(ingestion_results.get("industry", []), 1):
            try:
                logger.info(
                    "scoring_article",
                    index=i,
                    total=len(ingestion_results.get("industry", [])),
                    file=article_file,
                )

                # Read article content
                content = Path(article_file).read_text(encoding="utf-8")

                # Extract article ID from file path
                article_id = Path(article_file).stem

                # Score with JR Engine (use paper scoring for similar content)
                score = self.jr_engine.score_arxiv_paper(content, article_id)

                # Extract metadata
                metadata = self._extract_article_metadata(content)
                metadata["article_file_path"] = article_file

                # Store in database (using paper storage for now)
                self.database.store_paper_score(f"industry:{article_id}", score, metadata)

            except Exception as e:
                logger.error("article_scoring_error", file=article_file, error=str(e))

        logger.info("article_scoring_complete", count=len(ingestion_results.get("industry", [])))

        # Score Federal Register documents
        for i, doc_file in enumerate(ingestion_results.get("federal_register", []), 1):
            try:
                logger.info(
                    "scoring_federal_document",
                    index=i,
                    total=len(ingestion_results.get("federal_register", [])),
                    file=doc_file,
                )

                # Read document content
                content = Path(doc_file).read_text(encoding="utf-8")

                # Extract document number from file path
                doc_id = Path(doc_file).stem

                # Score with JR Engine
                score = self.jr_engine.score_arxiv_paper(content, doc_id)

                # Extract metadata
                metadata = self._extract_federal_register_metadata(content)
                metadata["document_file_path"] = doc_file

                # Store in database
                self.database.store_paper_score(f"federal_register:{doc_id}", score, metadata)

            except Exception as e:
                logger.error("federal_document_scoring_error", file=doc_file, error=str(e))

        logger.info(
            "federal_register_scoring_complete",
            count=len(ingestion_results.get("federal_register", [])),
        )

        logger.info("scoring_complete")

    def run_scoring_with_intel_events(self, batch: IntelEventBatch):
        """Score IntelEvents using JR Engine with pre-extracted hints.

        Enhanced scoring path that uses Gemini-extracted metadata and hints.

        Args:
            batch: IntelEventBatch from run_normalization()

        """
        if not batch.events:
            logger.info("intel_event_scoring_skipped", reason="no_events")
            return

        logger.info("intel_event_scoring_started", count=len(batch.events))

        for i, event in enumerate(batch.events, 1):
            try:
                logger.info(
                    "scoring_intel_event",
                    index=i,
                    total=len(batch.events),
                    event_id=event.id,
                    source_type=event.source_type.value,
                )

                # Score using enhanced IntelEvent method
                score = self.jr_engine.score_intel_event(event)

                # Store in database with event metadata
                metadata = {
                    "intel_event_id": event.id,
                    "source_url": event.source_url,
                    "source_type": event.source_type.value,
                    "jurisdiction": event.jurisdiction,
                    "effective_date": event.effective_date.isoformat()
                    if event.effective_date
                    else None,
                    "topic_tags": event.topic_tags,
                    "risk_tags": [t.value for t in event.risk_tags],
                    "gemini_confidence": event.gemini_confidence,
                    "gemini_suggested_tier": event.jr_hints.suggested_tier,
                    "summary": event.summary,
                }

                # Use paper storage for now (can be extended later)
                self.database.store_paper_score(f"intel_event:{event.id}", score, metadata)

            except Exception as e:
                logger.error("intel_event_scoring_error", event_id=event.id, error=str(e))

        logger.info("intel_event_scoring_complete", count=len(batch.events))

    def run_briefing(self) -> str:
        """Step 5: Briefing Generation
        Generate executive briefing from scored content

        Returns:
            Path to briefing file

        """
        logger.info("briefing_generation_started")

        briefing_file = self.briefing_generator.generate_briefing()

        logger.info("briefing_generation_complete", file=briefing_file)

        return briefing_file

    def run_full_pipeline(
        self,
        github_topics: list[str] | None = None,
        arxiv_days_back: int | None = None,
        download_pdfs: bool = False,
        use_gemini_scoring: bool = True,
    ) -> str:
        """Execute complete pipeline with Gemini normalization

        Args:
            github_topics: Topics to search for GitHub repos
            arxiv_days_back: Number of days to look back for arXiv papers
            download_pdfs: Whether to download PDFs
            use_gemini_scoring: Use IntelEvent-based scoring (vs raw content)

        Returns:
            Path to generated briefing file

        """
        start_time = datetime.now()
        logger.info("pipeline_execution_started", gemini_enabled=self.enable_gemini_normalization)

        # Step 1A: Ingestion
        ingestion_results = self.run_ingestion(
            github_topics=github_topics,
            arxiv_days_back=arxiv_days_back,
            download_pdfs=download_pdfs,
        )

        # Step 1B: Gemini Normalization (if enabled)
        intel_batch = None
        if self.enable_gemini_normalization:
            intel_batch = asyncio.run(self.run_normalization(ingestion_results))

        # Step 2-3: Scoring and Classification
        if use_gemini_scoring and intel_batch and intel_batch.events:
            # Use enhanced IntelEvent scoring path
            self.run_scoring_with_intel_events(intel_batch)
        else:
            # Fallback to legacy raw content scoring
            self.run_scoring(ingestion_results)

        # Step 5: Briefing Generation
        briefing_file = self.run_briefing()

        # Complete
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            "pipeline_execution_complete",
            duration_seconds=duration,
            briefing_file=briefing_file,
            intel_events_processed=len(intel_batch.events) if intel_batch else 0,
            gemini_normalization_used=self.enable_gemini_normalization,
        )

        return briefing_file

    def _extract_repo_metadata(self, content: str) -> dict:
        """Extract metadata from flattened repository content"""
        metadata = {}

        # Parse header lines
        for line in content.split("\n")[:10]:
            if line.startswith("# Stars:"):
                with contextlib.suppress(BaseException):
                    metadata["stars"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("# Description:"):
                metadata["description"] = line.split(":", 1)[1].strip()
            elif line.startswith("# URL:"):
                metadata["url"] = line.split(":", 1)[1].strip()
            elif line.startswith("# Topics:"):
                topics_str = line.split(":", 1)[1].strip()
                metadata["topics"] = [t.strip() for t in topics_str.split(",")]
            elif line.startswith("# Language:"):
                metadata["language"] = line.split(":", 1)[1].strip()
            elif line.startswith("# Last Updated:"):
                metadata["updated_at"] = line.split(":", 1)[1].strip()

        return metadata

    def _extract_paper_metadata(self, content: str) -> dict:
        """Extract metadata from paper markdown content"""
        metadata = {}

        # Parse markdown sections
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("# ") and i == 0:
                metadata["title"] = line[2:].strip()
            elif line.startswith("**Authors:**"):
                authors_str = line.split("**Authors:**")[1].strip()
                metadata["authors"] = [a.strip() for a in authors_str.split(",")]
            elif line.startswith("**Published:**"):
                metadata["published_date"] = line.split("**Published:**")[1].strip()
            elif line.startswith("**Categories:**"):
                categories_str = line.split("**Categories:**")[1].strip()
                metadata["categories"] = [c.strip() for c in categories_str.split(",")]
            elif line.startswith("**arXiv ID:**"):
                metadata["arxiv_id"] = line.split("**arXiv ID:**")[1].strip()
            elif line.startswith("**PDF URL:**"):
                metadata["pdf_url"] = line.split("**PDF URL:**")[1].strip()
            elif line.startswith("## Primary Category") and i + 1 < len(lines):
                metadata["primary_category"] = lines[i + 2].strip()

        # Extract abstract
        if "## Abstract" in content:
            abstract_section = content.split("## Abstract")[1].split("##", maxsplit=1)[0]
            metadata["abstract"] = abstract_section.strip()

        return metadata

    def _extract_article_metadata(self, content: str) -> dict:
        """Extract metadata from industry article markdown content"""
        metadata = {}

        # Parse markdown sections
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("# ") and i == 0:
                metadata["title"] = line[2:].strip()
            elif line.startswith("**Source:**"):
                metadata["source"] = line.split("**Source:**")[1].strip()
            elif line.startswith("**URL:**"):
                metadata["url"] = line.split("**URL:**")[1].strip()
            elif line.startswith("**Published:**"):
                metadata["published_date"] = line.split("**Published:**")[1].strip()
            elif line.startswith("**Vertical:**"):
                metadata["vertical"] = line.split("**Vertical:**")[1].strip()
            elif line.startswith("**Relevance Score:**"):
                with contextlib.suppress(BaseException):
                    metadata["relevance_score"] = float(
                        line.split("**Relevance Score:**")[1].strip(),
                    )

        # Extract summary
        if "## Summary" in content:
            summary_section = content.split("## Summary")[1].split("##", maxsplit=1)[0]
            metadata["summary"] = summary_section.strip()

        return metadata

    def _extract_federal_register_metadata(self, content: str) -> dict:
        """Extract metadata from Federal Register document markdown content"""
        metadata = {}

        # Parse markdown sections
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("# ") and i == 0:
                metadata["title"] = line[2:].strip()
            elif line.startswith("**Document Number:**"):
                metadata["document_number"] = line.split("**Document Number:**")[1].strip()
            elif line.startswith("**Type:**"):
                metadata["document_type"] = line.split("**Type:**")[1].strip()
            elif line.startswith("**Publication Date:**"):
                metadata["publication_date"] = line.split("**Publication Date:**")[1].strip()
            elif line.startswith("**Agency:**"):
                metadata["agency"] = line.split("**Agency:**")[1].strip()
            elif line.startswith("**PNKLN Vertical:**"):
                metadata["vertical"] = line.split("**PNKLN Vertical:**")[1].strip()
            elif line.startswith("**Relevance Score:**"):
                with contextlib.suppress(BaseException):
                    metadata["relevance_score"] = float(
                        line.split("**Relevance Score:**")[1].strip(),
                    )
            elif line.startswith("**Significant:**"):
                metadata["significant"] = line.split("**Significant:**")[1].strip() == "Yes"
            elif line.startswith("**HTML URL:**"):
                metadata["html_url"] = line.split("**HTML URL:**")[1].strip()
            elif line.startswith("**PDF URL:**"):
                metadata["pdf_url"] = line.split("**PDF URL:**")[1].strip()
            elif line.startswith("**Effective Date:**"):
                metadata["effective_date"] = line.split("**Effective Date:**")[1].strip()
            elif line.startswith("**Comment Deadline:**"):
                metadata["comment_deadline"] = line.split("**Comment Deadline:**")[1].strip()
            elif line.startswith("**Docket IDs:**"):
                metadata["docket_ids"] = line.split("**Docket IDs:**")[1].strip()
            elif line.startswith("**CFR References:**"):
                metadata["cfr_references"] = line.split("**CFR References:**")[1].strip()

        # Extract abstract
        if "## Abstract" in content:
            abstract_section = content.split("## Abstract")[1].split("##", maxsplit=1)[0]
            metadata["abstract"] = abstract_section.strip()

        return metadata


def run_pipeline(
    github_topics: list[str] | None = None,
    arxiv_days_back: int | None = None,
    download_pdfs: bool = False,
    enable_gemini_normalization: bool = True,
    use_gemini_scoring: bool = True,
) -> str:
    """Convenience function to run the full pipeline with Gemini normalization

    Usage:
        # Full pipeline with Gemini normalization (default)
        briefing_file = run_pipeline(
            github_topics=["mlops", "kubernetes"],
            arxiv_days_back=7
        )

        # Legacy mode without Gemini
        briefing_file = run_pipeline(
            github_topics=["mlops"],
            enable_gemini_normalization=False
        )
    """
    pipeline = NightlyIntelPipeline(enable_gemini_normalization=enable_gemini_normalization)
    return pipeline.run_full_pipeline(
        github_topics=github_topics,
        arxiv_days_back=arxiv_days_back,
        download_pdfs=download_pdfs,
        use_gemini_scoring=use_gemini_scoring,
    )
