# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Repository Flattener
Integrates with Repomix and Gitingest to flatten GitHub repositories for LLM consumption
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import tempfile
import httpx

from pnkln_intelligence.config import IngestionSettings

logger = logging.getLogger(__name__)


@dataclass
class FlattenedRepository:
    """Represents a flattened repository"""

    repo_name: str
    repo_url: str
    content: str
    format: str
    metadata: dict[str, Any]
    file_count: int
    total_lines: int
    token_count: int | None = None
    compression_ratio: float | None = None


class RepositoryFlattener:
    """
    Flattens GitHub repositories using Repomix or Gitingest

    Supports:
    - Repomix: XML, Markdown, JSON, Plain text with tree-sitter compression
    - Gitingest: Python API and URL-based conversion
    - Security scanning via Secretlint
    - Token counting for multiple encoders
    - Remote repository access without local clones
    """

    def __init__(self, settings: IngestionSettings | None = None):
        self.settings = settings or IngestionSettings()
        self.http_client = httpx.AsyncClient(timeout=300.0)

    async def flatten_with_repomix(
        self, repo_url: str, output_format: str = "xml", enable_compression: bool = True, run_security_scan: bool = True
    ) -> FlattenedRepository:
        """
        Flatten repository using Repomix (npx repomix)

        Args:
            repo_url: GitHub repository URL
            output_format: Output format (xml, markdown, json, plain)
            enable_compression: Enable tree-sitter compression
            run_security_scan: Run security scanning

        Returns:
            FlattenedRepository object
        """
        # Extract repo name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1]

        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"{repo_name}.{output_format}"

            # Build Repomix command
            cmd = ["npx", "repomix@latest", "--remote", repo_url, "--output", str(output_path), "--style", output_format]

            if not enable_compression:
                cmd.append("--no-compress")

            if not run_security_scan:
                cmd.append("--no-security-check")

            try:
                logger.info(f"Running Repomix for {repo_url}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

                if result.returncode != 0:
                    logger.error(f"Repomix failed: {result.stderr}")
                    raise RuntimeError(f"Repomix failed: {result.stderr}")

                # Read output file
                if not output_path.exists():
                    raise FileNotFoundError(f"Output file not found: {output_path}")

                content = output_path.read_text(encoding="utf-8")

                # Parse metadata from Repomix output (if available in stdout)
                metadata = self._parse_repomix_metadata(result.stdout)

                flattened = FlattenedRepository(
                    repo_name=repo_name,
                    repo_url=repo_url,
                    content=content,
                    format=output_format,
                    metadata=metadata,
                    file_count=metadata.get("file_count", 0),
                    total_lines=metadata.get("total_lines", 0),
                    token_count=metadata.get("token_count"),
                    compression_ratio=metadata.get("compression_ratio"),
                )

                logger.info(f"Successfully flattened {repo_name} with Repomix")
                return flattened

            except subprocess.TimeoutExpired:
                logger.error(f"Repomix timeout for {repo_url}")
                raise
            except Exception as e:
                logger.error(f"Error flattening {repo_url} with Repomix: {e}", exc_info=True)
                raise

    async def flatten_with_gitingest(self, repo_url: str, access_token: str | None = None) -> FlattenedRepository:
        """
        Flatten repository using Gitingest API

        Args:
            repo_url: GitHub repository URL
            access_token: GitHub personal access token for private repos

        Returns:
            FlattenedRepository object
        """
        # Extract repo name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1]

        # Convert github.com to gitingest.com
        gitingest_url = repo_url.replace("github.com", "gitingest.com")

        try:
            logger.info(f"Fetching from Gitingest: {gitingest_url}")

            headers = {}
            if access_token:
                headers["Authorization"] = f"token {access_token}"

            response = await self.http_client.get(gitingest_url, headers=headers)
            response.raise_for_status()

            content = response.text

            # Parse metadata from content
            metadata = {"source": "gitingest", "fetched_at": response.headers.get("date"), "content_length": len(content)}

            # Count lines
            total_lines = len(content.splitlines())

            flattened = FlattenedRepository(
                repo_name=repo_name,
                repo_url=repo_url,
                content=content,
                format="text",
                metadata=metadata,
                file_count=0,  # Gitingest doesn't provide file count
                total_lines=total_lines,
            )

            logger.info(f"Successfully flattened {repo_name} with Gitingest")
            return flattened

        except Exception as e:
            logger.error(f"Error flattening {repo_url} with Gitingest: {e}", exc_info=True)
            raise

    async def flatten_repository(self, repo_url: str, tool: str | None = None, **kwargs) -> FlattenedRepository:
        """
        Flatten repository using configured or specified tool

        Args:
            repo_url: GitHub repository URL
            tool: Flattening tool (repomix, gitingest) - defaults to settings
            **kwargs: Additional arguments passed to tool-specific method

        Returns:
            FlattenedRepository object
        """
        tool = tool or self.settings.flattening_tool

        if tool == "repomix":
            return await self.flatten_with_repomix(
                repo_url,
                output_format=kwargs.get("output_format", self.settings.output_format),
                enable_compression=kwargs.get("enable_compression", self.settings.repomix_compression),
                run_security_scan=kwargs.get("run_security_scan", self.settings.include_security_scan),
            )
        elif tool == "gitingest":
            return await self.flatten_with_gitingest(repo_url, access_token=kwargs.get("access_token"))
        else:
            raise ValueError(f"Unknown flattening tool: {tool}")

    async def flatten_multiple_repositories(self, repo_urls: list[str], concurrency: int = 3) -> list[FlattenedRepository]:
        """
        Flatten multiple repositories concurrently

        Args:
            repo_urls: List of repository URLs
            concurrency: Number of concurrent operations

        Returns:
            List of FlattenedRepository objects
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def flatten_with_semaphore(url: str) -> FlattenedRepository | None:
            async with semaphore:
                try:
                    return await self.flatten_repository(url)
                except Exception as e:
                    logger.error(f"Failed to flatten {url}: {e}")
                    return None

        tasks = [flatten_with_semaphore(url) for url in repo_urls]
        results = await asyncio.gather(*tasks)

        # Filter out None values (failed operations)
        successful_results = [r for r in results if r is not None]

        logger.info(f"Successfully flattened {len(successful_results)}/{len(repo_urls)} repositories")
        return successful_results

    def _parse_repomix_metadata(self, stdout: str) -> dict[str, Any]:
        """Parse metadata from Repomix stdout output"""
        metadata = {"source": "repomix", "file_count": 0, "total_lines": 0}

        # Parse stdout for statistics
        for line in stdout.splitlines():
            if "files processed" in line.lower():
                try:
                    metadata["file_count"] = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif "total lines" in line.lower():
                try:
                    metadata["total_lines"] = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif "token count" in line.lower():
                try:
                    metadata["token_count"] = int(line.split()[-1])
                except (ValueError, IndexError):
                    pass

        return metadata

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Example usage
if __name__ == "__main__":

    async def main():
        flattener = RepositoryFlattener()

        try:
            # Flatten a repository with Repomix
            repo = await flattener.flatten_repository("https://github.com/anthropics/anthropic-sdk-python", tool="repomix")

            print(f"\nFlattened: {repo.repo_name}")
            print(f"Format: {repo.format}")
            print(f"Files: {repo.file_count}")
            print(f"Lines: {repo.total_lines}")
            print(f"Content length: {len(repo.content)} characters")

        finally:
            await flattener.close()

    asyncio.run(main())
