# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Kairos Evidence Adapter — async queue bridge for swarm concurrency.

Provides a thin adapter that accepts evidence records via an asyncio.Queue
and feeds them into the existing AsyncBatchEvidenceWriter. This eliminates
the GIL-thrashing bottleneck when 100+ concurrent sub-agents dispatch
function calls simultaneously.

Architecture:
    KAIROS Daemon owns the asyncio.Queue
    → KairosEvidenceAdapter consumes from queue
    → AsyncBatchEvidenceWriter handles buffered disk I/O
    → Evidence NDJSON is durable and tamper-evident

This is NOT a replacement for EvidenceLogger — it is a supplementary
adapter for high-concurrency swarm scenarios where the synchronous
`EvidenceLogger.log()` path would cause GIL contention.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from firebase_tool_bridge.evidence import AsyncBatchEvidenceWriter

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SwarmEvidenceRecord:
  """Lightweight evidence record for swarm dispatch.

  Optimized for minimal allocation — frozen dataclass with slots.
  """

  function_name: str
  args_hash: str
  status: str
  timestamp: str = field(
    default_factory=lambda: datetime.now(UTC).isoformat(),
  )
  duration_ms: float = 0.0
  agent_id: str | None = None

  def to_json(self) -> str:
    """Serialize to compact JSON line."""
    d = {
      "func": self.function_name,
      "hash": self.args_hash,
      "status": self.status,
      "ts": self.timestamp,
      "ms": round(self.duration_ms, 2),
    }
    if self.agent_id:
      d["agent"] = self.agent_id
    return json.dumps(d, separators=(",", ":"))


def hash_args_fast(args: dict[str, Any]) -> str:
  """Fast SHA-256 hash of canonicalized args.

  Identical to evidence.hash_args but inlined to avoid import
  overhead in the hot path.
  """
  canonical = json.dumps(args, sort_keys=True, default=str)
  return hashlib.sha256(canonical.encode()).hexdigest()


class KairosEvidenceAdapter:
  """Async queue consumer that feeds into AsyncBatchEvidenceWriter.

  Usage in KAIROS daemon::

      queue = asyncio.Queue()
      adapter = KairosEvidenceAdapter(queue, evidence_dir=Path(".agent/evidence"))

      # Start the consumer
      asyncio.create_task(adapter.run())

      # From any coroutine, enqueue evidence
      adapter.enqueue("fetch_weather", {"city": "Boston"}, "SUCCESS")

  The adapter runs as a long-lived asyncio task, consuming records
  from the queue and batching them to disk via AsyncBatchEvidenceWriter.
  """

  def __init__(
    self,
    queue: asyncio.Queue[SwarmEvidenceRecord],
    *,
    evidence_dir: Path | None = None,
    flush_interval_secs: float = 1.0,
    max_buffer_size: int = 200,
  ) -> None:
    """Initialize the adapter.

    Args:
        queue: The asyncio.Queue shared with KAIROS daemon.
        evidence_dir: Directory for evidence NDJSON files.
        flush_interval_secs: Flush interval for the batch writer.
        max_buffer_size: Max records before forced flush.
    """
    self._queue = queue
    self._evidence_dir = evidence_dir or Path(".agent/evidence")
    self._evidence_dir.mkdir(parents=True, exist_ok=True)

    self._writer = AsyncBatchEvidenceWriter(
      self._evidence_dir / "swarm_evidence.ndjson",
      flush_interval_secs=flush_interval_secs,
      max_buffer_size=max_buffer_size,
    )
    self._records_consumed = 0
    self._running = False

  def enqueue(
    self,
    function_name: str,
    args: dict[str, Any],
    status: str = "SUCCESS",
    *,
    duration_ms: float = 0.0,
    agent_id: str | None = None,
  ) -> None:
    """Non-blocking enqueue — safe to call from any coroutine.

    This is the sub-100µs hot path. No file I/O happens here.

    Args:
        function_name: The dispatched function name.
        args: Arguments (hashed, never stored raw).
        status: Execution status (SUCCESS, REJECTED, FAILED).
        duration_ms: Execution duration.
        agent_id: Optional swarm agent identifier.
    """
    record = SwarmEvidenceRecord(
      function_name=function_name,
      args_hash=hash_args_fast(args),
      status=status,
      duration_ms=duration_ms,
      agent_id=agent_id,
    )
    try:
      self._queue.put_nowait(record)
    except asyncio.QueueFull:
      logger.warning(
        "Evidence queue full — dropping record for '%s'",
        function_name,
      )

  async def run(self) -> None:
    """Consume records from the queue and write to disk.

    Runs indefinitely until cancelled. Safe to use as an
    asyncio.Task managed by the KAIROS daemon.
    """
    self._running = True
    logger.info("KairosEvidenceAdapter started — consuming from queue")

    try:
      while True:
        record = await self._queue.get()
        self._writer.write(record.to_json())
        self._records_consumed += 1
        self._queue.task_done()
    except asyncio.CancelledError:
      logger.info(
        "KairosEvidenceAdapter shutting down — %d records consumed",
        self._records_consumed,
      )
      self._writer.close()
      self._running = False
      raise

  def close(self) -> None:
    """Flush and close the underlying writer."""
    self._writer.close()

  @property
  def records_consumed(self) -> int:
    """Total records consumed since start."""
    return self._records_consumed

  @property
  def pending_in_writer(self) -> int:
    """Records buffered in the writer awaiting flush."""
    return self._writer.pending_count

  @property
  def running(self) -> bool:
    """Whether the consumer loop is active."""
    return self._running


async def benchmark_kairos_adapter(
  num_records: int = 1000,
) -> dict[str, float]:
  """Benchmark the adapter's enqueue throughput.

  Returns:
      Dict with ops_per_sec, total_ms, and avg_us metrics.
  """
  queue: asyncio.Queue[SwarmEvidenceRecord] = asyncio.Queue(
    maxsize=num_records + 100,
  )
  adapter = KairosEvidenceAdapter(queue, evidence_dir=Path("/tmp/kairos_bench"))

  # Start consumer
  consumer_task = asyncio.create_task(adapter.run())

  # Benchmark enqueue (the hot path)
  start = time.perf_counter()
  for i in range(num_records):
    adapter.enqueue(
      f"tool_{i % 10}",
      {"key": f"value_{i}"},
      "SUCCESS",
      duration_ms=float(i),
      agent_id=f"agent_{i % 5}",
    )
  enqueue_ms = (time.perf_counter() - start) * 1000

  # Wait for all records to be consumed
  await queue.join()
  total_ms = (time.perf_counter() - start) * 1000

  consumer_task.cancel()
  with contextlib.suppress(asyncio.CancelledError):
    await consumer_task

  ops_per_sec = num_records / (enqueue_ms / 1000)
  avg_us = (enqueue_ms / num_records) * 1000

  return {
    "ops_per_sec": round(ops_per_sec, 1),
    "total_ms": round(total_ms, 2),
    "enqueue_ms": round(enqueue_ms, 2),
    "avg_enqueue_us": round(avg_us, 2),
    "records": num_records,
  }
