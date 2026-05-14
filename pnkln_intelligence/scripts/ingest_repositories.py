# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Repository Ingestion Script
Ingests all configured repositories using Repomix/Gitingest
"""

import asyncio
import logging
import yaml
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from google.cloud import storage, bigquery
import json

from pnkln_intelligence.config import get_settings
from pnkln_intelligence.ingestion import RepositoryFlattener

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RepositoryIngestionPipeline:
    """Pipeline for ingesting multiple repositories"""

    def __init__(self):
        self.settings = get_settings()
        self.flattener = RepositoryFlattener(self.settings.ingestion)
        self.gcs_client = storage.Client(project=self.settings.gcp.project_id)
        self.bq_client = bigquery.Client(project=self.settings.gcp.project_id)
        self.bucket = self.gcs_client.bucket(self.settings.gcp.gcs_bucket_raw)

    def load_repository_config(self) -> list[dict[str, Any]]:
        """Load repository configuration from YAML"""
        config_path = Path(self.settings.ingestion.repositories_config)

        if not config_path.exists():
            raise FileNotFoundError(f"Repository config not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Flatten nested structure
        all_repos = []
        for category, repos in config.items():
            for repo in repos:
                repo["category_group"] = category
                all_repos.append(repo)

        logger.info(f"Loaded {len(all_repos)} repositories from config")
        return all_repos

    async def ingest_repository(self, repo_config: dict[str, Any]) -> bool:
        """
        Ingest a single repository

        Args:
            repo_config: Repository configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        repo_url = repo_config["url"]
        repo_name = repo_config["name"]

        logger.info(f"Ingesting repository: {repo_name} ({repo_url})")

        try:
            # Flatten repository
            flattened = await self.flattener.flatten_repository(repo_url)

            # Upload to GCS
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            blob_path = f"raw/repositories/{repo_name}/snapshot_{timestamp}.xml"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(flattened.content, content_type="application/xml")

            logger.info(f"Uploaded to GCS: gs://{self.bucket.name}/{blob_path}")

            # Store metadata in BigQuery
            await self.store_repository_metadata(repo_config, flattened, blob_path)

            logger.info(f"Successfully ingested: {repo_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest {repo_name}: {e}", exc_info=True)
            await self.log_ingestion_error(repo_name, str(e))
            return False

    async def store_repository_metadata(self, repo_config: dict[str, Any], flattened, gcs_path: str):
        """Store repository metadata in BigQuery"""
        table_id = f"{self.settings.gcp.project_id}.{self.settings.gcp.bigquery_dataset}.repositories"

        rows = [
            {
                "repo_id": repo_config["name"].replace("/", "_"),
                "repo_name": repo_config["name"],
                "repo_url": repo_config["url"],
                "organization": repo_config["name"].split("/")[0],
                "primary_language": "python",  # TODO: Detect from repo
                "category": repo_config.get("category", ""),
                "priority": repo_config.get("priority", "medium"),
                "stars": repo_config.get("stars", 0),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": json.dumps(
                    {
                        "gcs_path": gcs_path,
                        "category_group": repo_config.get("category_group", ""),
                        "file_count": flattened.file_count,
                        "total_lines": flattened.total_lines,
                        "token_count": flattened.token_count,
                    }
                ),
                "total_files": flattened.file_count,
                "total_lines": flattened.total_lines,
                "ingestion_status": "completed",
                "error_message": None,
            }
        ]

        errors = self.bq_client.insert_rows_json(table_id, rows)

        if errors:
            logger.error(f"Error inserting rows: {errors}")
        else:
            logger.info(f"Stored metadata in BigQuery for {repo_config['name']}")

    async def log_ingestion_error(self, repo_name: str, error_message: str):
        """Log ingestion error to BigQuery"""
        table_id = f"{self.settings.gcp.project_id}.{self.settings.gcp.bigquery_dataset}.ingestion_logs"

        rows = [
            {
                "log_id": f"{repo_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "ingestion_type": "repository",
                "entity_id": repo_name,
                "status": "failed",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": error_message,
                "metadata": json.dumps({"repo_name": repo_name}),
            }
        ]

        self.bq_client.insert_rows_json(table_id, rows)

    async def ingest_all(self, filter_priority: str = None, filter_category: str = None, limit: int = None):
        """
        Ingest all configured repositories

        Args:
            filter_priority: Filter by priority (critical, high, medium, low)
            filter_category: Filter by category
            limit: Limit number of repositories to ingest
        """
        repos = self.load_repository_config()

        # Apply filters
        if filter_priority:
            repos = [r for r in repos if r.get("priority") == filter_priority]
            logger.info(f"Filtered to {len(repos)} repositories with priority={filter_priority}")

        if filter_category:
            repos = [r for r in repos if r.get("category") == filter_category]
            logger.info(f"Filtered to {len(repos)} repositories with category={filter_category}")

        if limit:
            repos = repos[:limit]
            logger.info(f"Limited to {limit} repositories")

        # Ingest repositories with concurrency control
        logger.info(f"Starting ingestion of {len(repos)} repositories...")

        results = []
        for repo in repos:
            result = await self.ingest_repository(repo)
            results.append(result)

            # Add delay to avoid rate limiting
            await asyncio.sleep(2)

        # Summary
        successful = sum(results)
        failed = len(results) - successful

        logger.info("\n" + "=" * 70)
        logger.info(f"Ingestion completed: {successful} successful, {failed} failed")
        logger.info("=" * 70)

    async def cleanup(self):
        """Cleanup resources"""
        await self.flattener.close()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest repositories for PNKLN Intelligence Pipeline")
    parser.add_argument("--priority", choices=["critical", "high", "medium", "low"], help="Filter by priority")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--limit", type=int, help="Limit number of repositories")

    args = parser.parse_args()

    pipeline = RepositoryIngestionPipeline()

    try:
        await pipeline.ingest_all(filter_priority=args.priority, filter_category=args.category, limit=args.limit)
    finally:
        await pipeline.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
