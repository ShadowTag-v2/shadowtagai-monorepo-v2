# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Intelligence Pipeline - BigQuery Storage

Stores intelligence items in BigQuery for:
- Historical analysis
- Business impact tracking
- Compliance audit trail
- Dashboard queries
"""

import os
import json
import logging
from datetime import datetime
from google.cloud import bigquery
from google.api_core import exceptions

from ..models.intelligence_item import IntelligenceItem

logger = logging.getLogger(__name__)


class BigQueryStorage:
    """
    BigQuery storage handler for intelligence items
    """

    def __init__(self, project_id: str = None, dataset_id: str = None):
        """
        Initialize BigQuery storage

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id or os.getenv("PROJECT_ID")
        self.dataset_id = dataset_id or os.getenv("BIGQUERY_DATASET", "pnkln_intelligence")
        self.table_id = "intelligence_items"

        self.client = bigquery.Client(project=self.project_id)
        logger.info(f"BigQueryStorage initialized: {self.project_id}.{self.dataset_id}")

    async def store_items(self, items: list[IntelligenceItem]) -> int:
        """
        Store intelligence items in BigQuery

        Args:
            items: List of processed intelligence items

        Returns:
            Number of items stored
        """
        logger.info(f"=== Storing {len(items)} items in BigQuery ===")
        start_time = datetime.now()

        # Ensure dataset and table exist
        self._ensure_dataset()
        self._ensure_table()

        # Convert items to BigQuery rows
        rows = [self._item_to_row(item) for item in items]

        # Insert rows
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        errors = self.client.insert_rows_json(table_ref, rows)

        if errors:
            logger.error(f"Errors inserting rows: {errors}")
            return 0

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ Stored {len(items)} items in BigQuery in {duration:.1f}s")

        return len(items)

    def _ensure_dataset(self):
        """Ensure BigQuery dataset exists"""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"

        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_ref} exists")
        except exceptions.NotFound:
            logger.info(f"Creating dataset {dataset_ref}")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset)

    def _ensure_table(self):
        """Ensure BigQuery table exists with schema"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"

        try:
            self.client.get_table(table_ref)
            logger.info(f"Table {table_ref} exists")
        except exceptions.NotFound:
            logger.info(f"Creating table {table_ref}")

            schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("published_date", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("jr_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("jr_reasoning", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("tier", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("tier_reasoning", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("cor_synthesis", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("action_items", "STRING", mode="REPEATED"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            ]

            table = bigquery.Table(table_ref, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="published_date")
            self.client.create_table(table)

    def _item_to_row(self, item: IntelligenceItem) -> dict:
        """
        Convert IntelligenceItem to BigQuery row

        Args:
            item: Intelligence item

        Returns:
            Dictionary suitable for BigQuery insert
        """
        return {
            "id": item.id,
            "source": item.source.value,
            "title": item.title,
            "url": item.url,
            "content": item.content,
            "published_date": item.published_date.isoformat(),
            "ingested_at": item.ingested_at.isoformat(),
            "jr_score": item.jr_score,
            "jr_reasoning": item.jr_reasoning,
            "tier": item.tier.value if item.tier else None,
            "tier_reasoning": item.tier_reasoning,
            "cor_synthesis": item.cor_synthesis,
            "action_items": item.action_items,
            "metadata": json.dumps(item.metadata),
        }


async def main():
    """
    Main BigQuery storage entry point
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Load processed items
    input_file = "/tmp/intelligence_items_processed.json"
    with open(input_file) as f:
        items_data = json.load(f)

    items = [IntelligenceItem.from_dict(item_data) for item_data in items_data]

    # Store in BigQuery
    storage = BigQueryStorage()
    stored_count = await storage.store_items(items)

    print(f"✓ Stored {stored_count} items in BigQuery")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
