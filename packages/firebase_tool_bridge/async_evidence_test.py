# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for AsyncBatchEvidenceWriter and enhanced EvidenceLogger."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path


from firebase_tool_bridge.evidence import (
  AsyncBatchEvidenceWriter,
  EvidenceLogger,
  SyncEvidenceWriter,
)


class TestSyncEvidenceWriter:
  """Tests for the original synchronous writer."""

  def test_write_creates_file(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = SyncEvidenceWriter(f)
    writer.write('{"a":1}')
    assert f.exists()
    assert f.read_text().strip() == '{"a":1}'

  def test_multiple_writes_append(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = SyncEvidenceWriter(f)
    writer.write('{"a":1}')
    writer.write('{"b":2}')
    lines = f.read_text().strip().split("\n")
    assert len(lines) == 2

  def test_flush_is_noop(self, tmp_path: Path) -> None:
    writer = SyncEvidenceWriter(tmp_path / "test.ndjson")
    writer.flush()  # Should not raise

  def test_close_is_noop(self, tmp_path: Path) -> None:
    writer = SyncEvidenceWriter(tmp_path / "test.ndjson")
    writer.close()  # Should not raise


class TestAsyncBatchEvidenceWriter:
  """Tests for the buffered async writer."""

  def test_write_buffers_records(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=10.0, max_buffer_size=50)
    writer.write('{"a":1}')
    # Should NOT be on disk yet
    if f.exists():
      assert f.read_text().strip() == ""  # Buffer not flushed
    assert writer.pending_count == 1
    writer.close()

  def test_flush_writes_all(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=60.0, max_buffer_size=1000)
    for i in range(5):
      writer.write(f'{{"n":{i}}}')
    assert writer.pending_count == 5
    writer.flush()
    assert writer.pending_count == 0
    lines = f.read_text().strip().split("\n")
    assert len(lines) == 5
    writer.close()

  def test_max_buffer_triggers_flush(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=60.0, max_buffer_size=3)
    writer.write('{"a":1}')
    writer.write('{"b":2}')
    writer.write('{"c":3}')  # This should trigger auto-flush
    assert writer.pending_count == 0
    assert f.exists()
    lines = f.read_text().strip().split("\n")
    assert len(lines) == 3
    writer.close()

  def test_periodic_flush(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=0.1, max_buffer_size=1000)
    writer.write('{"a":1}')
    # Poll instead of fixed sleep — converges immediately on fast
    # systems, survives loaded CI environments (up to 2s budget).
    deadline = time.monotonic() + 2.0
    while writer.pending_count > 0 and time.monotonic() < deadline:
      time.sleep(0.05)
    assert writer.pending_count == 0, (
      f"Periodic flush did not fire within 2s (pending={writer.pending_count})"
    )
    assert f.exists()
    writer.close()

  def test_close_flushes_remaining(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=60.0, max_buffer_size=1000)
    writer.write('{"a":1}')
    writer.write('{"b":2}')
    writer.close()
    lines = f.read_text().strip().split("\n")
    assert len(lines) == 2

  def test_write_after_close_is_warning(self, tmp_path: Path) -> None:
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=60.0, max_buffer_size=1000)
    writer.close()
    writer.write('{"late":true}')  # Should log warning, not crash
    assert writer.pending_count == 0

  def test_thread_safety(self, tmp_path: Path) -> None:
    """Multiple threads writing concurrently should not lose records."""
    f = tmp_path / "test.ndjson"
    writer = AsyncBatchEvidenceWriter(f, flush_interval_secs=60.0, max_buffer_size=1000)
    n_threads = 8
    n_writes = 50
    barrier = threading.Barrier(n_threads)

    def writer_thread(tid: int) -> None:
      barrier.wait()
      for i in range(n_writes):
        writer.write(f'{{"tid":{tid},"i":{i}}}')

    threads = [
      threading.Thread(target=writer_thread, args=(t,)) for t in range(n_threads)
    ]
    for t in threads:
      t.start()
    for t in threads:
      t.join()

    writer.close()
    lines = f.read_text().strip().split("\n")
    assert len(lines) == n_threads * n_writes


class TestEvidenceLoggerAsyncMode:
  """Test EvidenceLogger with async_writes=True."""

  def test_async_logger_creates_file(self, tmp_path: Path) -> None:
    evidence = EvidenceLogger(repo_root=tmp_path, async_writes=True)
    evidence.log(
      function_name="test_fn",
      args={"key": "value"},
      risk_tier="low",
      confirmation_required=False,
      confirmation_received=None,
      result_summary="ok",
      duration_ms=1.0,
    )
    evidence.flush()
    evidence.close()
    f = tmp_path / ".agent" / "evidence" / "function_calls.ndjson"
    assert f.exists()
    record = json.loads(f.read_text().strip())
    assert record["function_name"] == "test_fn"

  def test_sync_logger_still_works(self, tmp_path: Path) -> None:
    evidence = EvidenceLogger(repo_root=tmp_path, async_writes=False)
    evidence.log(
      function_name="sync_fn",
      args={},
      risk_tier="medium",
      confirmation_required=False,
      confirmation_received=None,
      result_summary="ok",
      duration_ms=2.0,
    )
    f = tmp_path / ".agent" / "evidence" / "function_calls.ndjson"
    assert f.exists()
    record = json.loads(f.read_text().strip())
    assert record["function_name"] == "sync_fn"

  def test_async_latency_lower_than_sync(self, tmp_path: Path) -> None:
    """Async writes should be faster per-call than sync."""
    n_calls = 50
    base_args = {
      "args": {"k": "v"},
      "risk_tier": "low",
      "confirmation_required": False,
      "confirmation_received": None,
      "result_summary": "ok",
      "duration_ms": 1.0,
    }

    # Sync timing
    sync_logger = EvidenceLogger(repo_root=tmp_path / "sync", async_writes=False)
    start = time.perf_counter()
    for i in range(n_calls):
      sync_logger.log(function_name=f"fn_{i}", **base_args)
    sync_ms = (time.perf_counter() - start) * 1000

    # Async timing
    async_logger = EvidenceLogger(
      repo_root=tmp_path / "async",
      async_writes=True,
      max_buffer_size=1000,
    )
    start = time.perf_counter()
    for i in range(n_calls):
      async_logger.log(function_name=f"fn_{i}", **base_args)
    async_ms = (time.perf_counter() - start) * 1000
    async_logger.close()

    # Async should be meaningfully faster
    assert async_ms < sync_ms, (
      f"Async ({async_ms:.1f}ms) should be faster than sync ({sync_ms:.1f}ms)"
    )
