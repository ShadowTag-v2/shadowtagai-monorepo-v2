# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Nightly Intel Pipeline - Main Orchestration
Coordinates ingestion, scoring, and briefing generation
"""

from pathlib import Path
from datetime import datetime

import structlog

from .scrapers.github_flattener import GitHubFlattener
from .scrapers.arxiv_crawler import ArxivCrawler
from .engines.jr_engine import JREngine
from .storage.database import IntelDatabase
from .storage.briefing import BriefingGenerator
from .utils.logging_setup import setup_logging

logger = structlog.get_logger(__name__)


class NightlyIntelPipeline:
    """
    Main pipeline orchestrator

    Execution steps:
    1. Ingestion: Discover GitHub repos and arXiv papers
    2. JR Scoring: Evaluate content using Purpose → Reasons → Brakes
    3. Tier Classification: Classify into tiers
    4. Storage: Store in local database
    5. Briefing: Generate executive briefing
    """

    def __init__(self):
        setup_logging()

        self.github_flattener = GitHubFlattener()
        self.arxiv_crawler = ArxivCrawler()
        self.jr_engine = JREngine()
        self.database = IntelDatabase()
        self.briefing_generator = BriefingGenerator(db=self.database)

        logger.info("pipeline_initialized")

    def run_ingestion(
        self, github_topics: list[str] | None = None, arxiv_days_back: int | None = None, download_pdfs: bool = False
    ) -> dict[str, list[str]]:
        """
        Step 1: Ingestion
        Discover and download content from GitHub and arXiv

        Returns:
            Dict with 'repos' and 'papers' file paths
        """
        logger.info("ingestion_started")

        results = {"repos": [], "papers": []}

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

        logger.info("ingestion_complete", total_repos=len(results["repos"]), total_papers=len(results["papers"]))

        return results

    def run_scoring(self, ingestion_results: dict[str, list[str]]):
        """
        Steps 2-3: JR Scoring and Tier Classification
        Score all ingested content and classify into tiers
        """
        logger.info("scoring_started")

        # Score GitHub repositories
        for i, repo_file in enumerate(ingestion_results["repos"], 1):
            try:
                logger.info("scoring_repo", index=i, total=len(ingestion_results["repos"]), file=repo_file)

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
                logger.info("scoring_paper", index=i, total=len(ingestion_results["papers"]), file=paper_file)

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

        logger.info("scoring_complete")

    def run_briefing(self) -> str:
        """
        Step 5: Briefing Generation
        Generate executive briefing from scored content

        Returns:
            Path to briefing file
        """
        logger.info("briefing_generation_started")

        briefing_file = self.briefing_generator.generate_briefing()

        logger.info("briefing_generation_complete", file=briefing_file)

        return briefing_file

    def run_full_pipeline(self, github_topics: list[str] | None = None, arxiv_days_back: int | None = None, download_pdfs: bool = False) -> str:
        """
        Execute complete pipeline

        Returns:
            Path to generated briefing file
        """
        start_time = datetime.now()
        logger.info("pipeline_execution_started")

        # Step 1: Ingestion
        ingestion_results = self.run_ingestion(github_topics=github_topics, arxiv_days_back=arxiv_days_back, download_pdfs=download_pdfs)

        # Step 2-3: Scoring and Classification
        self.run_scoring(ingestion_results)

        # Step 5: Briefing Generation
        briefing_file = self.run_briefing()

        # Complete
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("pipeline_execution_complete", duration_seconds=duration, briefing_file=briefing_file)

        return briefing_file

    def _extract_repo_metadata(self, content: str) -> dict:
        """Extract metadata from flattened repository content"""
        metadata = {}

        # Parse header lines
        for line in content.split("\n")[:10]:
            if line.startswith("# Stars:"):
                try:
                    metadata["stars"] = int(line.split(":", 1)[1].strip())
                except:
                    pass
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
            elif line.startswith("## Primary Category"):
                if i + 1 < len(lines):
                    metadata["primary_category"] = lines[i + 2].strip()

        # Extract abstract
        if "## Abstract" in content:
            abstract_section = content.split("## Abstract")[1].split("##")[0]
            metadata["abstract"] = abstract_section.strip()

        return metadata


def run_pipeline(github_topics: list[str] | None = None, arxiv_days_back: int | None = None, download_pdfs: bool = False) -> str:
    """
    Convenience function to run the full pipeline

    Usage:
        briefing_file = run_pipeline(
            github_topics=["mlops", "kubernetes"],
            arxiv_days_back=7
        )
    """
    pipeline = NightlyIntelPipeline()
    return pipeline.run_full_pipeline(github_topics=github_topics, arxiv_days_back=arxiv_days_back, download_pdfs=download_pdfs)
