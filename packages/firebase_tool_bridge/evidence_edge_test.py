# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Edge case tests for EvidenceLogger — robustness against filesystem failures."""

from __future__ import annotations

import json
import stat
import threading
from pathlib import Path

import pytest

from firebase_tool_bridge.evidence import (
  DEFAULT_EVIDENCE_DIR,
  EvidenceLogger,
  EvidenceRecord,
  hash_args,
)


class TestHashArgsEdgeCases:
  def test_empty_dict(self):
    h = hash_args({})
    assert len(h) == 64
    assert h == hash_args({})

  def test_deterministic_across_key_order(self):
    assert hash_args({"b": 2, "a": 1}) == hash_args({"a": 1, "b": 2})

  def test_large_payload(self):
    large = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}
    assert len(hash_args(large)) == 64

  def test_nested_objects(self):
    assert len(hash_args({"a": {"b": {"c": [1, 2, 3]}}})) == 64

  def test_special_chars(self):
    assert len(hash_args({"msg": "Hello 🌍 — café"})) == 64

  def test_non_serializable_uses_str(self):
    assert len(hash_args({"path": Path("/tmp/test")})) == 64


class TestEvidenceRecordEdgeCases:
  def test_to_dict_omits_none(self):
    record = EvidenceRecord(
      function_name="test",
      args_hash="abc",
      risk_tier="low",
      confirmation_required=False,
      confirmation_received=None,
      execution_result_summary="ok",
      duration_ms=1.0,
      error=None,
    )
    d = record.to_dict()
    assert "confirmation_received" not in d
    assert "error" not in d

  def test_to_dict_includes_error(self):
    record = EvidenceRecord(
      function_name="test",
      args_hash="abc",
      risk_tier="high",
      confirmation_required=True,
      confirmation_received=True,
      execution_result_summary="failed",
      duration_ms=5.0,
      success=False,
      error="ValueError: bad",
    )
    d = record.to_dict()
    assert d["error"] == "ValueError: bad"
    assert d["success"] is False

  def test_unicode_function_name(self):
    record = EvidenceRecord(
      function_name="日本語_fn",
      args_hash="abc",
      risk_tier="low",
      confirmation_required=False,
      confirmation_received=None,
      execution_result_summary="ok",
      duration_ms=1.0,
    )
    assert record.to_dict()["function_name"] == "日本語_fn"


class TestEvidenceLoggerEdgeCases:
  def _log(self, logger, name="test_fn"):
    return logger.log(
      function_name=name,
      args={"k": "v"},
      risk_tier="low",
      confirmation_required=False,
      confirmation_received=None,
      result_summary="ok",
      duration_ms=1.0,
    )

  def test_creates_directory(self, tmp_path):
    d = tmp_path / ".agent" / "evidence"
    assert not d.exists()
    EvidenceLogger(repo_root=tmp_path)
    assert d.exists()

  def test_appends_ndjson(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    self._log(logger, "fn_1")
    self._log(logger, "fn_2")
    self._log(logger, "fn_3")
    f = tmp_path / DEFAULT_EVIDENCE_DIR / "function_calls.ndjson"
    lines = f.read_text().strip().splitlines()
    assert len(lines) == 3
    for line in lines:
      assert "function_name" in json.loads(line)

  def test_compact_json(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    self._log(logger)
    f = tmp_path / DEFAULT_EVIDENCE_DIR / "function_calls.ndjson"
    content = f.read_text().strip()
    assert '": ' not in content

  def test_read_only_file_raises(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    f = tmp_path / DEFAULT_EVIDENCE_DIR / "function_calls.ndjson"
    f.touch()
    f.chmod(stat.S_IRUSR)
    try:
      with pytest.raises(PermissionError):
        self._log(logger)
    finally:
      f.chmod(stat.S_IRUSR | stat.S_IWUSR)

  def test_concurrent_writes(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    errors = []

    def worker(tid):
      try:
        for i in range(20):
          logger.log(
            function_name=f"t{tid}_c{i}",
            args={"t": tid, "c": i},
            risk_tier="low",
            confirmation_required=False,
            confirmation_received=None,
            result_summary=f"t{tid}c{i}",
            duration_ms=float(i),
          )
      except Exception as e:
        errors.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
    assert not errors
    f = tmp_path / DEFAULT_EVIDENCE_DIR / "function_calls.ndjson"
    lines = f.read_text().strip().splitlines()
    assert len(lines) == 80
    for line in lines:
      json.loads(line)

  def test_timer_and_elapsed(self):
    start = EvidenceLogger.timer()
    assert isinstance(start, float) and start > 0
    assert EvidenceLogger.elapsed_ms(start) >= 0

  def test_log_returns_record(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    record = self._log(logger, "ret_check")
    assert isinstance(record, EvidenceRecord)
    assert record.function_name == "ret_check"
    assert len(record.args_hash) == 64

  def test_error_record(self, tmp_path):
    logger = EvidenceLogger(repo_root=tmp_path)
    record = logger.log(
      function_name="fail",
      args={"x": 1},
      risk_tier="high",
      confirmation_required=True,
      confirmation_received=True,
      result_summary="error",
      duration_ms=50.0,
      success=False,
      error="ValueError: bad",
    )
    assert record.success is False
    assert record.error == "ValueError: bad"
