# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Unit tests for Firestore SweepResult persistence layer.

Tests cover:
  1. sweep_result_to_doc — correct field mapping
  2. persist_sweep_result — graceful fallback when Firestore unavailable
  3. query_recent_sweeps — empty list when disabled
  4. get_sweep_by_id — None when disabled

Run:
    python -m pytest tests/unit/test_firestore_persistence.py -v
"""

from __future__ import annotations

import sys
import pathlib
from unittest.mock import MagicMock, patch


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "packages"))


class TestSweepResultToDoc:
    """Verify sweep_result_to_doc produces correct Firestore document."""

    def test_basic_mapping(self) -> None:
        from speculation_engine.firestore_persistence import sweep_result_to_doc
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(
            query="Legal AI competitive landscape",
            report_text="# Report\nDetailed analysis...",
            duration_seconds=123.4,
            interaction_id="int-abc123",
            agent="deep_research_max",
        )

        doc = sweep_result_to_doc(
            result,
            session_id="kairos-42-1234567890",
            pipeline_mode="research_sweep",
            status="completed",
        )

        assert doc["query"] == "Legal AI competitive landscape"
        assert doc["report_text"] == "# Report\nDetailed analysis..."
        assert doc["duration_seconds"] == 123.4
        assert doc["interaction_id"] == "int-abc123"
        assert doc["agent"] == "deep_research_max"
        assert doc["image_count"] == 0
        assert doc["pipeline_mode"] == "research_sweep"
        assert doc["session_id"] == "kairos-42-1234567890"
        assert doc["status"] == "completed"
        assert "daemon_pid" in doc
        assert "created_at_epoch" in doc

    def test_with_images(self) -> None:
        from speculation_engine.firestore_persistence import sweep_result_to_doc
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(
            query="test",
            report_text="report",
            images=["img1.png", "img2.png", "img3.png"],
        )

        doc = sweep_result_to_doc(result)
        assert doc["image_count"] == 3

    def test_default_values(self) -> None:
        from speculation_engine.firestore_persistence import sweep_result_to_doc
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(query="q", report_text="r")
        doc = sweep_result_to_doc(result)

        assert doc["pipeline_mode"] == "research_sweep"
        assert doc["status"] == "completed"
        assert doc["session_id"] == ""
        assert doc["duration_seconds"] == 0.0


class TestPersistSweepResult:
    """Verify persist_sweep_result handles missing Firestore gracefully."""

    def test_returns_none_when_firestore_unavailable(self) -> None:
        from speculation_engine.firestore_persistence import persist_sweep_result
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(query="test", report_text="report")

        # Patch _get_firestore_client to return None (no Firestore)
        with patch(
            "speculation_engine.firestore_persistence._get_firestore_client",
            return_value=None,
        ):
            doc_id = persist_sweep_result(result)
            assert doc_id is None

    def test_returns_doc_id_on_success(self) -> None:
        from speculation_engine.firestore_persistence import persist_sweep_result
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(query="test", report_text="report")

        # Mock Firestore client
        mock_client = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "mock-doc-123"
        mock_client.collection.return_value.add.return_value = (None, mock_doc_ref)

        with (
            patch(
                "speculation_engine.firestore_persistence._get_firestore_client",
                return_value=mock_client,
            ),
            patch(
                "speculation_engine.firestore_persistence.fs",
                create=True,
            ),
        ):
            # We need to mock the google.cloud.firestore import inside persist_sweep_result
            mock_fs_module = MagicMock()
            mock_fs_module.SERVER_TIMESTAMP = "SERVER_TIMESTAMP"
            with patch.dict("sys.modules", {"google.cloud.firestore": mock_fs_module, "google.cloud": MagicMock()}):
                doc_id = persist_sweep_result(result, session_id="test-session")
                assert doc_id == "mock-doc-123"


class TestQueryRecentSweeps:
    """Verify query_recent_sweeps handles missing Firestore gracefully."""

    def test_returns_empty_when_unavailable(self) -> None:
        from speculation_engine.firestore_persistence import query_recent_sweeps

        with patch(
            "speculation_engine.firestore_persistence._get_firestore_client",
            return_value=None,
        ):
            results = query_recent_sweeps(limit=5)
            assert results == []


class TestGetSweepById:
    """Verify get_sweep_by_id handles missing Firestore gracefully."""

    def test_returns_none_when_unavailable(self) -> None:
        from speculation_engine.firestore_persistence import get_sweep_by_id

        with patch(
            "speculation_engine.firestore_persistence._get_firestore_client",
            return_value=None,
        ):
            result = get_sweep_by_id("some-doc-id")
            assert result is None
