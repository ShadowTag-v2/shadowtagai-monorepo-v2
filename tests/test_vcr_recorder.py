# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for VCR Recorder — P3.1 deterministic API record/replay/diff.

Exercises all four VCR modes (OFF, RECORD, REPLAY, DIFF),
cassette persistence, hash-based/sequential lookup, diff reporting,
and the ReplayMiss error path.

Reference: AGNT STATE B Spec P3.1
"""

from __future__ import annotations

import json
from pathlib import Path


import pytest

from vcr.cassette import Cassette, CassetteEntry, compute_request_hash
from vcr.recorder import DiffMismatch, ReplayMiss, VCRMode, VCRRecorder


# ── Helpers ──────────────────────────────────────────────────────────────────


def _mock_live_call(request_body: dict) -> dict:
    """Simulate a Gemini API response."""
    return {
        "candidates": [
            {
                "content": {"parts": [{"text": f"Response to: {request_body.get('contents', '')}"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 20, "totalTokenCount": 30},
    }


def _sample_request(content: str = "Hello") -> dict:
    """Create a sample request body."""
    return {"model": "gemini-3.1-flash", "contents": [{"parts": [{"text": content}]}]}


# ── Cassette Tests ───────────────────────────────────────────────────────────


class TestCassette:
    """Test JSONL-backed cassette storage."""

    def test_record_and_lookup(self, tmp_path: Path) -> None:
        """Record an entry and look it up by hash."""
        cassette = Cassette(tmp_path / "test.jsonl")
        req = _sample_request("test")
        resp = _mock_live_call(req)

        entry = cassette.record(request_body=req, response_body=resp, model="gemini-3.1-flash")
        looked_up = cassette.lookup(entry.request_hash)

        assert looked_up is not None
        assert looked_up.response_body == resp

    def test_sequential_replay(self, tmp_path: Path) -> None:
        """Sequential replay returns entries in order."""
        cassette = Cassette(tmp_path / "seq.jsonl")

        for i in range(3):
            req = _sample_request(f"msg-{i}")
            cassette.record(request_body=req, response_body={"idx": i})

        for i in range(3):
            entry = cassette.next_sequential()
            assert entry is not None
            assert entry.response_body["idx"] == i

        assert cassette.next_sequential() is None

    def test_reset_cursor(self, tmp_path: Path) -> None:
        """Resetting cursor allows replaying from the start."""
        cassette = Cassette(tmp_path / "reset.jsonl")
        cassette.record(request_body=_sample_request("a"), response_body={"v": 1})

        first = cassette.next_sequential()
        assert first is not None
        assert cassette.next_sequential() is None

        cassette.reset_cursor()
        second = cassette.next_sequential()
        assert second is not None
        assert second.response_body == {"v": 1}

    def test_persistence_roundtrip(self, tmp_path: Path) -> None:
        """Entries survive save/load cycle."""
        path = tmp_path / "persist.jsonl"
        c1 = Cassette(path)
        c1.record(request_body=_sample_request("persist"), response_body={"data": "saved"})

        c2 = Cassette(path)
        c2.load()
        assert len(c2) == 1
        assert c2.entries[0].response_body["data"] == "saved"

    def test_empty_cassette(self, tmp_path: Path) -> None:
        """Empty cassette has zero entries."""
        cassette = Cassette(tmp_path / "empty.jsonl")
        assert len(cassette) == 0
        assert cassette.lookup("nonexistent") is None
        assert cassette.next_sequential() is None

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Loading a nonexistent file should silently produce empty cassette."""
        cassette = Cassette(tmp_path / "nope.jsonl")
        cassette.load()
        assert len(cassette) == 0


class TestComputeRequestHash:
    """Test deterministic request hashing."""

    def test_deterministic(self) -> None:
        """Same input produces same hash."""
        req = _sample_request("deterministic")
        h1 = compute_request_hash(req)
        h2 = compute_request_hash(req)
        assert h1 == h2

    def test_strips_nondeterministic_fields(self) -> None:
        """timestamp, session_id, request_id are stripped before hashing."""
        req1 = {**_sample_request("strip"), "timestamp": 1000, "session_id": "s1"}
        req2 = {**_sample_request("strip"), "timestamp": 2000, "session_id": "s2"}
        assert compute_request_hash(req1) == compute_request_hash(req2)

    def test_different_content_different_hash(self) -> None:
        """Different content produces different hashes."""
        h1 = compute_request_hash(_sample_request("alpha"))
        h2 = compute_request_hash(_sample_request("beta"))
        assert h1 != h2


class TestCassetteEntry:
    """Test CassetteEntry serialization."""

    def test_roundtrip(self) -> None:
        """to_dict/from_dict roundtrip preserves all fields."""
        entry = CassetteEntry(
            request_hash="abc123",
            request_body={"model": "test"},
            response_body={"result": "ok"},
            model="gemini-3.1-flash",
            timestamp=1000.0,
            latency_ms=42.5,
            token_usage={"prompt": 10, "completion": 20},
            tags=["test", "unit"],
        )
        d = entry.to_dict()
        restored = CassetteEntry.from_dict(d)

        assert restored.request_hash == entry.request_hash
        assert restored.response_body == entry.response_body
        assert restored.tags == entry.tags


# ── VCRRecorder Tests ────────────────────────────────────────────────────────


class TestVCRRecorderOff:
    """Test VCR OFF mode (passthrough)."""

    def test_off_mode_passthrough(self, tmp_path: Path) -> None:
        """OFF mode passes requests directly to live_call."""
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.OFF)
        req = _sample_request("off")

        response = recorder.intercept(req, _mock_live_call)
        assert "candidates" in response
        assert recorder.stats["recordings"] == 0


class TestVCRRecorderRecord:
    """Test VCR RECORD mode."""

    def test_record_captures_response(self, tmp_path: Path) -> None:
        """RECORD mode stores the live response in cassette."""
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        req = _sample_request("record-test")

        response = recorder.intercept(req, _mock_live_call, model="gemini-3.1-flash")

        assert "candidates" in response
        assert recorder.stats["recordings"] == 1

        # Verify cassette file was written
        cassette_file = tmp_path / "default.jsonl"
        assert cassette_file.exists()
        with open(cassette_file) as f:
            lines = f.readlines()
        assert len(lines) == 1

    def test_record_multiple_entries(self, tmp_path: Path) -> None:
        """Multiple recordings are appended to the same cassette."""
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)

        for i in range(5):
            recorder.intercept(_sample_request(f"multi-{i}"), _mock_live_call)

        assert recorder.stats["recordings"] == 5


class TestVCRRecorderReplay:
    """Test VCR REPLAY mode."""

    def test_replay_returns_recorded(self, tmp_path: Path) -> None:
        """REPLAY mode returns previously recorded responses."""
        req = _sample_request("replay-test")

        # Phase 1: Record
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        original_response = recorder.intercept(req, _mock_live_call)

        # Phase 2: Replay
        replay_recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.REPLAY)
        replayed_response = replay_recorder.intercept(req, lambda r: pytest.fail("should not call live"))

        assert replayed_response == original_response
        assert replay_recorder.stats["replays"] == 1

    def test_replay_miss_raises(self, tmp_path: Path) -> None:
        """REPLAY mode raises ReplayMiss when no matching entry exists."""

        # Create empty cassette file
        (tmp_path / "default.jsonl").touch()
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.REPLAY)

        with pytest.raises(ReplayMiss):
            recorder.intercept(_sample_request("unknown"), lambda r: {})

        assert recorder.stats["replay_misses"] == 1

    def test_sequential_fallback(self, tmp_path: Path) -> None:
        """REPLAY uses sequential fallback when hash doesn't match."""

        # Record with one request
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        recorder.intercept(_sample_request("original"), _mock_live_call)

        # Replay with a different request (hash won't match, falls back to sequential)
        replay = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.REPLAY)
        response = replay.intercept(_sample_request("different"), lambda r: pytest.fail("should not call"))

        assert "candidates" in response
        assert replay.stats["replays"] == 1


class TestVCRRecorderDiff:
    """Test VCR DIFF mode."""

    def test_diff_match(self, tmp_path: Path) -> None:
        """DIFF mode reports a match when live == recorded."""
        req = _sample_request("diff-match")

        # Record
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        recorder.intercept(req, _mock_live_call)

        # Diff with same response
        diff_recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.DIFF)
        diff_recorder.intercept(req, _mock_live_call)

        assert diff_recorder.stats["diffs_run"] == 1
        assert diff_recorder.stats["diffs_matched"] == 1
        assert diff_recorder.stats["diffs_mismatched"] == 0

    def test_diff_mismatch(self, tmp_path: Path) -> None:
        """DIFF mode detects mismatches between live and recorded."""
        req = _sample_request("diff-mismatch")

        # Record
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        recorder.intercept(req, _mock_live_call)

        # Diff with different response
        def different_response(r: dict) -> dict:
            return {"candidates": [{"content": {"parts": [{"text": "DIFFERENT"}]}}]}

        diff_recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.DIFF)
        diff_recorder.intercept(req, different_response)

        assert diff_recorder.stats["diffs_run"] == 1
        assert diff_recorder.stats["diffs_mismatched"] == 1
        assert len(diff_recorder.diff_results) == 1
        assert not diff_recorder.diff_results[0].is_match

    def test_diff_new_recording(self, tmp_path: Path) -> None:
        """DIFF mode records new entries when no match exists."""
        (tmp_path / "default.jsonl").touch()

        diff_recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.DIFF)
        diff_recorder.intercept(_sample_request("new-entry"), _mock_live_call)

        assert diff_recorder.stats["diffs_run"] == 1
        # Should have recorded the new entry
        cassette = Cassette(tmp_path / "default.jsonl")
        cassette.load()
        assert len(cassette) == 1


class TestDiffReport:
    """Test diff report generation."""

    def test_write_diff_report(self, tmp_path: Path) -> None:
        """write_diff_report produces valid JSON."""
        req = _sample_request("report")

        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.RECORD)
        recorder.intercept(req, _mock_live_call)

        diff_recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.DIFF)

        def alt_response(r: dict) -> dict:
            return {"alt": True}

        diff_recorder.intercept(req, alt_response)

        report_path = tmp_path / "report.json"
        diff_recorder.write_diff_report(report_path)

        assert report_path.exists()
        with open(report_path) as f:
            report = json.load(f)

        assert report["mode"] == "diff"
        assert report["stats"]["diffs_mismatched"] == 1
        assert len(report["mismatches"]) == 1


class TestDiffMismatchObject:
    """Test the DiffMismatch value object."""

    def test_match_detection(self) -> None:
        """Identical responses should be a match."""
        response = {"answer": 42}
        mismatch = DiffMismatch("hash1", response, response)
        assert mismatch.is_match
        assert len(mismatch.diff_lines) == 0

    def test_mismatch_detection(self) -> None:
        """Different responses should produce diff lines."""
        mismatch = DiffMismatch("hash2", {"a": 1}, {"a": 2})
        assert not mismatch.is_match
        assert len(mismatch.diff_lines) > 0


class TestVCRRecorderRepr:
    """Test VCRRecorder string representation."""

    def test_repr(self, tmp_path: Path) -> None:
        """repr should include mode and cassette name."""
        recorder = VCRRecorder(cassette_dir=tmp_path, mode=VCRMode.OFF)
        r = repr(recorder)
        assert "off" in r
        assert "default.jsonl" in r
