# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Infrastructure Initialization Script
Sets up GCP resources: BigQuery, GCS, Vertex AI
"""

import asyncio
import logging
from pathlib import Path
from google.cloud import bigquery, storage
from google.cloud import aiplatform

from pnkln_intelligence.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfrastructureInitializer:
  """Initialize GCP infrastructure for PNKLN Intelligence Pipeline"""

  def __init__(self):
    self.settings = get_settings()
    self.bq_client = bigquery.Client(project=self.settings.gcp.project_id)
    self.gcs_client = storage.Client(project=self.settings.gcp.project_id)

  def init_bigquery(self):
    """Create BigQuery dataset and tables"""
    logger.info("Initializing BigQuery resources...")

    # Create dataset
    dataset_id = f"{self.settings.gcp.project_id}.{self.settings.gcp.bigquery_dataset}"

    try:
      dataset = bigquery.Dataset(dataset_id)
      dataset.location = self.settings.gcp.bigquery_location
      dataset.description = "PNKLN Intelligence Pipeline - Code Search and Analysis"
      dataset.labels = {"component": "code-search", "environment": "production"}

      dataset = self.bq_client.create_dataset(dataset, exists_ok=True)
      logger.info(f"Created dataset: {dataset_id}")

    except Exception as e:
      logger.error(f"Error creating dataset: {e}")
      raise

    # Load and execute schema SQL
    schema_path = (
      Path(__file__).parent.parent / "infrastructure" / "bigquery_schemas.sql"
    )

    if not schema_path.exists():
      logger.error(f"Schema file not found: {schema_path}")
      return

    with open(schema_path) as f:
      schema_sql = f.read()

    # Replace project_id placeholder
    schema_sql = schema_sql.replace("{project_id}", self.settings.gcp.project_id)

    # Execute each CREATE TABLE statement
    statements = schema_sql.split(";")

    for statement in statements:
      statement = statement.strip()
      if not statement or statement.startswith("--"):
        continue

      try:
        self.bq_client.query(statement).result()
        logger.info("Executed SQL statement successfully")
      except Exception as e:
        logger.warning(f"Error executing statement: {e}")
        # Continue with other statements

    logger.info("BigQuery initialization completed")

  def init_gcs(self):
    """Create GCS buckets and apply lifecycle policies"""
    logger.info("Initializing GCS buckets...")

    bucket_name = self.settings.gcp.gcs_bucket_raw

    try:
      # Create bucket
      bucket = self.gcs_client.bucket(bucket_name)

      if not bucket.exists():
        bucket = self.gcs_client.create_bucket(
          bucket_name, location=self.settings.gcp.location
        )
        logger.info(f"Created bucket: {bucket_name}")
      else:
        logger.info(f"Bucket already exists: {bucket_name}")

      # Create directory structure
      directories = [
        "raw/repositories/",
        "raw/research_papers/",
        "processed/code_chunks/by_language/",
        "processed/code_chunks/by_repository/",
        "processed/embeddings/",
        "models/fine_tuned/",
        "indexes/vector_search_snapshots/",
        "logs/ingestion/",
      ]

      for directory in directories:
        blob = bucket.blob(directory + ".keep")
        if not blob.exists():
          blob.upload_from_string("")
          logger.info(f"Created directory: {directory}")

      # Apply lifecycle policy
      lifecycle_path = (
        Path(__file__).parent.parent / "infrastructure" / "gcs_lifecycle_policy.json"
      )

      if lifecycle_path.exists():
        import json

        with open(lifecycle_path) as f:
          lifecycle_policy = json.load(f)

        bucket.lifecycle_rules = lifecycle_policy["lifecycle"]["rule"]
        bucket.patch()
        logger.info("Applied lifecycle policy to bucket")

    except Exception as e:
      logger.error(f"Error creating GCS bucket: {e}")
      raise

    logger.info("GCS initialization completed")

  async def init_vertex_ai(self):
    """Initialize Vertex AI resources"""
    logger.info("Initializing Vertex AI resources...")

    try:
      aiplatform.init(
        project=self.settings.gcp.project_id, location=self.settings.gcp.location
      )

      logger.info("Vertex AI initialized successfully")
      logger.info(
        "Note: Index and endpoint creation should be done after embeddings are ready"
      )
      logger.info(
        "Use VectorSearchManager.create_index() and create_index_endpoint() when ready"
      )

    except Exception as e:
      logger.error(f"Error initializing Vertex AI: {e}")
      raise

  async def run_all(self):
    """Run all initialization steps"""
    logger.info("Starting infrastructure initialization...")

    self.init_bigquery()
    self.init_gcs()
    await self.init_vertex_ai()

    logger.info("\n" + "=" * 70)
    logger.info("Infrastructure initialization completed successfully!")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info(
      "1. Start ingesting repositories: python -m pnkln_intelligence.scripts.ingest_repos"
    )
    logger.info(
      "2. Discover arXiv papers: python -m pnkln_intelligence.scripts.discover_papers"
    )
    logger.info(
      "3. Generate embeddings: python -m pnkln_intelligence.scripts.generate_embeddings"
    )
    logger.info(
      "4. Create vector search index: python -m pnkln_intelligence.scripts.create_index"
    )


async def main():
  """Main entry point"""
  initializer = InfrastructureInitializer()
  await initializer.run_all()


if __name__ == "__main__":
  asyncio.run(main())
