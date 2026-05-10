"""Data Lineage Tracking for Ingestion Pipeline."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DataLineageTracker:
    """Tracks the lifecycle of a data item through the ingestion pipeline."""

    def __init__(self, storage_path: str = "data/lineage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_run_id = str(uuid.uuid4())

    def track_item(
        self,
        source: str,
        raw_content: Any,
        stage: str = "collected",
        metadata: dict[str, Any] = None,
    ) -> str:
        """Record a lineage event for an item.
        Returns the lineage_id for the item.
        """
        lineage_id = str(uuid.uuid4())
        event = {
            "lineage_id": lineage_id,
            "run_id": self.current_run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "stage": stage,
            "content_hash": str(hash(str(raw_content))),  # Simple hash for demo
            "metadata": metadata or {},
            # In prod, we might store the full content in GCS/S3 and just link it here
            # For now, we'll store a snippet
            "content_snippet": str(raw_content)[:200] if raw_content else None,
        }

        self._persist_event(event)
        return lineage_id

    def update_item(
        self,
        lineage_id: str,
        stage: str,
        transformed_content: Any = None,
        metadata: dict[str, Any] = None,
    ):
        """Update the status/stage of an existing item."""
        event = {
            "lineage_id": lineage_id,
            "run_id": self.current_run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "metadata": metadata or {},
            "content_snippet": str(transformed_content)[:200] if transformed_content else None,
        }
        self._persist_event(event)

    def _persist_event(self, event: dict[str, Any]):
        """Write event to storage (simulated BigQuery/DB)."""
        # In a real system, this would insert into BigQuery
        # Here we append to a daily JSONL file
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        file_path = self.storage_path / f"lineage_{date_str}.jsonl"

        try:
            with open(file_path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist lineage event: {e}")
