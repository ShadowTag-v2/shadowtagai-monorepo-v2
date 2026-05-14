# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GitHub Repository Flattener
Downloads and flattens GitHub repositories for AI/MLOps technologies
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import structlog
from github import Github, Repository
from github.GithubException import GithubException

from ..config import GITHUB_CONFIG, STORAGE_CONFIG

logger = structlog.get_logger(__name__)


class GitHubFlattener:
    """
    Discovers and flattens relevant GitHub repositories

    Features:
    - Topic-based repository discovery
    - Star threshold filtering
    - Intelligent file extraction (code, config, docs)
    - Deduplication and size limits
    - Local storage management
    """

    def __init__(self, token: str | None = None):
        self.token = token or GITHUB_CONFIG["token"]
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")

        self.github = Github(self.token)
        self.config = GITHUB_CONFIG
        self.storage_path = Path(STORAGE_CONFIG["flattened_repos"]["path"])
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info("github_flattener_initialized", storage_path=str(self.storage_path))

    def search_repositories(
        self, topics: list[str] | None = None, min_stars: int | None = None, max_results_per_topic: int | None = None
    ) -> list[Repository.Repository]:
        """
        Search for repositories by topics with star filtering

        Args:
            topics: List of GitHub topics to search
            min_stars: Minimum star count threshold
            max_results_per_topic: Maximum repositories per topic

        Returns:
            List of Repository objects
        """
        topics = topics or self.config["target_topics"]
        min_stars = min_stars or self.config["min_stars"]
        max_results = max_results_per_topic or self.config["max_repos_per_topic"]

        all_repos: dict[str, Repository.Repository] = {}  # Dedupe by full_name

        for topic in topics:
            try:
                query = f"topic:{topic} stars:>={min_stars}"
                logger.info("searching_repositories", topic=topic, query=query)

                repositories = self.github.search_repositories(query=query, sort="stars", order="desc")

                count = 0
                for repo in repositories:
                    if count >= max_results:
                        break

                    # Deduplicate across topics
                    if repo.full_name not in all_repos:
                        all_repos[repo.full_name] = repo
                        logger.debug("repository_found", name=repo.full_name, stars=repo.stargazers_count, topic=topic)
                    count += 1

            except GithubException as e:
                logger.error("search_error", topic=topic, error=str(e))
                continue

        logger.info("repository_search_complete", total_repos=len(all_repos), topics=topics)
        return list(all_repos.values())

    def should_include_file(self, file_path: str) -> bool:
        """
        Determine if file should be included in flattened output

        Filters by:
        - File extension (code, config, docs)
        - Directory exclusions (node_modules, venv, etc.)
        - Size limits
        """
        flatten_config = self.config["flatten_config"]
        path = Path(file_path)

        # Check excluded directories
        for excluded_dir in flatten_config["exclude_dirs"]:
            if excluded_dir in path.parts:
                return False

        # Check file extension
        if path.suffix:
            return path.suffix in flatten_config["include_extensions"]

        # Include certain extensionless files
        if path.name in ["Dockerfile", "Makefile", "LICENSE", "README"]:
            return True

        return False

    def flatten_repository(self, repo: Repository.Repository) -> str | None:
        """
        Flatten a repository into a single text file

        Format:
        ```
        # Repository: owner/name
        # Stars: 1234
        # Description: ...
        # URL: https://github.com/owner/name
        # Topics: topic1, topic2

        ## File: path/to/file.py
        [file content]

        ## File: path/to/another.yaml
        [file content]
        ```

        Returns:
            Path to flattened file, or None if failed
        """
        try:
            logger.info("flattening_repository", name=repo.full_name, stars=repo.stargazers_count)

            # Create output file
            safe_name = repo.full_name.replace("/", "_")
            output_file = self.storage_path / f"{safe_name}_flattened.txt"

            # Start building flattened content
            content_parts = [
                f"# Repository: {repo.full_name}",
                f"# Stars: {repo.stargazers_count}",
                f"# Description: {repo.description or 'N/A'}",
                f"# URL: {repo.html_url}",
                f"# Topics: {', '.join(repo.get_topics())}",
                f"# Language: {repo.language or 'N/A'}",
                f"# Last Updated: {repo.updated_at.isoformat()}",
                f"# Flattened: {datetime.now().isoformat()}",
                "\n" + "=" * 80 + "\n",
            ]

            # Get repository contents recursively
            files_processed = 0
            total_size = 0
            max_size_bytes = self.config["flatten_config"]["max_file_size_mb"] * 1024 * 1024

            def process_contents(contents, current_path=""):
                nonlocal files_processed, total_size

                for content_file in contents:
                    try:
                        if content_file.type == "dir":
                            # Recursively process directory
                            new_contents = repo.get_contents(content_file.path)
                            process_contents(new_contents, content_file.path)

                        elif content_file.type == "file":
                            # Check if we should include this file
                            if not self.should_include_file(content_file.path):
                                continue

                            # Check size limit
                            if content_file.size > max_size_bytes:
                                logger.warning(
                                    "file_too_large", repo=repo.full_name, file=content_file.path, size_mb=content_file.size / (1024 * 1024)
                                )
                                continue

                            # Download file content
                            try:
                                file_content = content_file.decoded_content.decode("utf-8", errors="ignore")
                            except Exception as decode_error:
                                logger.warning("file_decode_error", repo=repo.full_name, file=content_file.path, error=str(decode_error))
                                continue

                            # Add to flattened content
                            content_parts.append(f"\n## File: {content_file.path}\n")
                            content_parts.append(f"```{Path(content_file.path).suffix[1:]}\n")
                            content_parts.append(file_content)
                            content_parts.append("\n```\n")

                            files_processed += 1
                            total_size += content_file.size

                            if files_processed % 10 == 0:
                                logger.debug("flattening_progress", repo=repo.full_name, files=files_processed)

                    except Exception as e:
                        logger.warning("content_processing_error", repo=repo.full_name, path=content_file.path, error=str(e))
                        continue

            # Start processing from root
            root_contents = repo.get_contents("")
            process_contents(root_contents)

            # Write flattened content to file
            final_content = "\n".join(content_parts)
            output_file.write_text(final_content, encoding="utf-8")

            logger.info(
                "repository_flattened",
                repo=repo.full_name,
                files_processed=files_processed,
                output_size_kb=len(final_content) / 1024,
                output_file=str(output_file),
            )

            return str(output_file)

        except GithubException as e:
            logger.error("github_api_error", repo=repo.full_name, error=str(e), status=e.status)
            return None
        except Exception as e:
            logger.error("flatten_error", repo=repo.full_name, error=str(e))
            return None

    def flatten_repositories(self, repos: list[Repository.Repository] | None = None, topics: list[str] | None = None) -> list[str]:
        """
        Flatten multiple repositories

        Args:
            repos: List of Repository objects (if None, will search)
            topics: Topics to search for (if repos is None)

        Returns:
            List of paths to flattened files
        """
        if repos is None:
            repos = self.search_repositories(topics=topics)

        flattened_files = []

        for i, repo in enumerate(repos, 1):
            logger.info("processing_repository", index=i, total=len(repos), repo=repo.full_name)

            # Rate limiting: GitHub API has limits
            if i > 1:
                asyncio.run(asyncio.sleep(2))  # 2 second delay between repos

            flattened_file = self.flatten_repository(repo)
            if flattened_file:
                flattened_files.append(flattened_file)

        logger.info("flattening_complete", total_repos=len(repos), successful=len(flattened_files))

        return flattened_files

    def get_recent_updates(self, days_back: int = 7) -> list[Repository.Repository]:
        """
        Find recently updated repositories in target topics

        Args:
            days_back: Number of days to look back

        Returns:
            List of recently updated repositories
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        all_repos: dict[str, Repository.Repository] = {}

        for topic in self.config["target_topics"]:
            try:
                query = f"topic:{topic} stars:>={self.config['min_stars']} pushed:>={cutoff_str}"

                repositories = self.github.search_repositories(query=query, sort="updated", order="desc")

                count = 0
                max_results = self.config["max_repos_per_topic"]

                for repo in repositories:
                    if count >= max_results:
                        break

                    if repo.full_name not in all_repos:
                        all_repos[repo.full_name] = repo
                        logger.debug("recent_repo_found", name=repo.full_name, updated=repo.updated_at, topic=topic)
                    count += 1

            except GithubException as e:
                logger.error("recent_search_error", topic=topic, error=str(e))
                continue

        logger.info("recent_updates_found", count=len(all_repos), days_back=days_back)
        return list(all_repos.values())


def flatten_top_repos(topics: list[str] | None = None) -> list[str]:
    """
    Convenience function to flatten top repositories

    Usage:
        flattened_files = flatten_top_repos(["mlops", "kubernetes"])
    """
    flattener = GitHubFlattener()
    return flattener.flatten_repositories(topics=topics)


def flatten_recent_updates(days_back: int = 7) -> list[str]:
    """
    Convenience function to flatten recently updated repositories

    Usage:
        flattened_files = flatten_recent_updates(days_back=7)
    """
    flattener = GitHubFlattener()
    recent_repos = flattener.get_recent_updates(days_back=days_back)
    return flattener.flatten_repositories(repos=recent_repos)
