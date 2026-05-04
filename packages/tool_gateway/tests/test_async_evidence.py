# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for AsyncEvidenceLogger — non-blocking tool gateway audit trail."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tool_gateway.async_evidence import AsyncEvidenceLogger


@pytest.fixture
def beads_dir(tmp_path: Path) -> Path:
    """Temporary beads directory."""
    d = tmp_path / ".beads"
    d.mkdir()
    return d


@pytest.fixture
def mock_decision() -> MagicMock:
    """A mock Decision object with expected attributes."""
    d = MagicMock()
    d.allowed = True
    d.reason = "Contract matched"
    d.contract_id = "test-contract-001"
    d.reuse_hints = ["cached"]
    d.preconditions_met = True
    return d


class TestAsyncEvidenceLogger:
    """Tests for the async evidence logging system."""

    @pytest.mark.asyncio
    async def test_log_check_creates_file(self, beads_dir: Path, mock_decision: MagicMock):
        """log_check should create a JSONL entry in the issues file."""
        logger = AsyncEvidenceLogger(beads_dir)
        await logger.log_check(
            tool_id="test_tool",
            context={"key": "value"},
            decision=mock_decision,
        )

        issues_file = beads_dir / "issues.jsonl"
        assert issues_file.exists()

        lines = issues_file.read_text().strip().split("\n")
        assert len(lines) == 1

        entry = json.loads(lines[0])
        assert entry["type"] == "tool_gateway_check"
        assert entry["tool_id"] == "test_tool"
        assert entry["allowed"] is True
        assert entry["contract_id"] == "test-contract-001"

    @pytest.mark.asyncio
    async def test_log_execution_creates_entry(self, beads_dir: Path):
        """log_execution should create a tool_gateway_execution entry."""
        logger = AsyncEvidenceLogger(beads_dir)
        await logger.log_execution(
            tool_id="exec_tool",
            success=True,
            detail="Completed successfully",
        )

        issues_file = beads_dir / "issues.jsonl"
        entry = json.loads(issues_file.read_text().strip())
        assert entry["type"] == "tool_gateway_execution"
        assert entry["success"] is True
        assert entry["detail"] == "Completed successfully"

    @pytest.mark.asyncio
    async def test_multiple_entries_append(self, beads_dir: Path, mock_decision: MagicMock):
        """Multiple log calls should append, not overwrite."""
        logger = AsyncEvidenceLogger(beads_dir)
        await logger.log_check("tool_a", {}, mock_decision)
        await logger.log_check("tool_b", {"x": 1}, mock_decision)
        await logger.log_execution("tool_c", success=False, detail="err")

        lines = (beads_dir / "issues.jsonl").read_text().strip().split("\n")
        assert len(lines) == 3

    @pytest.mark.asyncio
    async def test_non_serializable_context_stringified(self, beads_dir: Path, mock_decision: MagicMock):
        """Non-serializable context values should be stringified."""
        logger = AsyncEvidenceLogger(beads_dir)
        await logger.log_check(
            tool_id="test_tool",
            context={"path": Path("/some/path"), "normal": "value"},
            decision=mock_decision,
        )

        entry = json.loads((beads_dir / "issues.jsonl").read_text().strip())
        assert "path" in entry["context_keys"]

    @pytest.mark.asyncio
    async def test_detail_truncated_at_500(self, beads_dir: Path):
        """Detail strings longer than 500 chars should be truncated."""
        logger = AsyncEvidenceLogger(beads_dir)
        long_detail = "x" * 1000
        await logger.log_execution("tool_d", success=True, detail=long_detail)

        entry = json.loads((beads_dir / "issues.jsonl").read_text().strip())
        assert len(entry["detail"]) == 500

    @pytest.mark.asyncio
    async def test_beads_dir_created_if_missing(self, tmp_path: Path, mock_decision: MagicMock):
        """If beads_dir doesn't exist, it should be created automatically."""
        beads_dir = tmp_path / "nonexistent" / ".beads"
        logger = AsyncEvidenceLogger(beads_dir)
        await logger.log_check("tool_x", {}, mock_decision)

        assert beads_dir.exists()
        assert (beads_dir / "issues.jsonl").exists()
