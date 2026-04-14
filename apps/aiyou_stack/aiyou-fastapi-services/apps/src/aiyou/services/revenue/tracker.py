"""Revenue tracker service.

Provides async event tracking with BigQuery streaming and local buffering.
"""

import asyncio
import contextlib
import logging
from collections import deque

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

from .events import RevenueEvent

logger = logging.getLogger(__name__)


class RevenueTracker:
    """Revenue event tracker with BigQuery streaming.

    Features:
    - Async event emission
    - Local buffering for batch writes
    - Automatic retry on failures
    - Metrics collection
    """

    def __init__(
        self,
        project_id: str = "acquired-jet-478701-b3",
        dataset_id: str = "pnkln_analytics",
        table_id: str = "revenue_events",
        buffer_size: int = 100,
        flush_interval_seconds: int = 10,
    ):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval_seconds

        self._buffer: deque[RevenueEvent] = deque(maxlen=buffer_size * 2)
        self._client: bigquery.Client | None = None
        self._flush_task: asyncio.Task | None = None
        self._running = False

        # Metrics
        self.events_tracked = 0
        self.events_flushed = 0
        self.flush_errors = 0

    async def start(self):
        """Start the tracker and background flush task."""
        self._client = bigquery.Client(project=self.project_id)
        self._running = True

        # Ensure table exists
        await self._ensure_table()

        # Start background flush task
        self._flush_task = asyncio.create_task(self._flush_loop())

        logger.info(f"RevenueTracker started: {self.project_id}.{self.dataset_id}.{self.table_id}")

    async def stop(self):
        """Stop the tracker and flush remaining events."""
        self._running = False

        if self._flush_task:
            self._flush_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._flush_task

        # Final flush
        await self._flush()

        logger.info(
            f"RevenueTracker stopped. Total events: {self.events_tracked}, "
            f"Flushed: {self.events_flushed}, Errors: {self.flush_errors}",
        )

    async def track(self, event: RevenueEvent):
        """Track a revenue event.

        Events are buffered locally and flushed to BigQuery periodically.
        """
        self._buffer.append(event)
        self.events_tracked += 1

        # Flush if buffer is full
        if len(self._buffer) >= self.buffer_size:
            await self._flush()

    async def track_batch(self, events: list[RevenueEvent]):
        """Track multiple events at once."""
        for event in events:
            self._buffer.append(event)
            self.events_tracked += 1

        if len(self._buffer) >= self.buffer_size:
            await self._flush()

    async def _flush(self):
        """Flush buffered events to BigQuery."""
        if not self._buffer:
            return

        # Drain buffer
        events = []
        while self._buffer:
            events.append(self._buffer.popleft())

        if not events:
            return

        # Convert to BigQuery rows
        rows = [e.to_bigquery_row() for e in events]

        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            errors = self._client.insert_rows_json(table_ref, rows)

            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                self.flush_errors += len(errors)
                # Re-queue failed events
                for i, _error in enumerate(errors):
                    if i < len(events):
                        self._buffer.appendleft(events[i])
            else:
                self.events_flushed += len(events)
                logger.debug(f"Flushed {len(events)} events to BigQuery")

        except Exception as e:
            logger.error(f"BigQuery flush failed: {e}")
            self.flush_errors += len(events)
            # Re-queue all events
            for event in reversed(events):
                self._buffer.appendleft(event)

    async def _flush_loop(self):
        """Background task to periodically flush events."""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self._flush()

    async def _ensure_table(self):
        """Ensure the BigQuery table exists with correct schema."""
        dataset_ref = self._client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(self.table_id)

        schema = [
            SchemaField("event_id", "STRING", mode="REQUIRED"),
            SchemaField("event_type", "STRING", mode="REQUIRED"),
            SchemaField("service", "STRING", mode="REQUIRED"),
            SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            SchemaField("event_date", "DATE", mode="REQUIRED"),
            SchemaField("user_id", "STRING"),
            SchemaField("session_id", "STRING"),
            SchemaField("device_type", "STRING"),
            SchemaField("content_id", "STRING"),
            SchemaField("product_id", "STRING"),
            SchemaField("sku", "STRING"),
            SchemaField("revenue_cents", "INTEGER"),
            SchemaField("currency", "STRING"),
            SchemaField("payment_method", "STRING"),
            SchemaField("creator_id", "STRING"),
            SchemaField("creator_share_cents", "INTEGER"),
            SchemaField("platform_share_cents", "INTEGER"),
            SchemaField("country_code", "STRING"),
            SchemaField("region", "STRING"),
            SchemaField("quality_score", "INTEGER"),
            SchemaField("completion_percentage", "INTEGER"),
            SchemaField("properties", "JSON"),
        ]

        try:
            self._client.get_table(table_ref)
            logger.debug(f"Table {table_ref} already exists")
        except Exception:
            # Create table with date partitioning
            table = bigquery.Table(table_ref, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="event_date",
            )
            table.clustering_fields = ["service", "event_type"]

            self._client.create_table(table)
            logger.info(f"Created table {table_ref}")

    def get_metrics(self) -> dict:
        """Get tracker metrics."""
        return {
            "events_tracked": self.events_tracked,
            "events_flushed": self.events_flushed,
            "flush_errors": self.flush_errors,
            "buffer_size": len(self._buffer),
            "running": self._running,
        }


# Global tracker instance
_tracker: RevenueTracker | None = None


async def get_tracker() -> RevenueTracker:
    """Get or create the global revenue tracker."""
    global _tracker
    if _tracker is None:
        _tracker = RevenueTracker()
        await _tracker.start()
    return _tracker


async def shutdown_tracker():
    """Shutdown the global tracker."""
    global _tracker
    if _tracker:
        await _tracker.stop()
        _tracker = None
