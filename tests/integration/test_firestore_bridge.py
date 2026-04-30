# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for CoW overlay ↔ Firestore bridge (Phase 3 Milestone 2).

Tests:
  1. Diff computation (unified diff parsing, hunk structure)
  2. Bridge security enforcement (Trust Level 0, attorney UID)
  3. Commit flow (accept, reject, partial accept)
  4. Audit trail generation
  5. Edge cases (empty files, new files, large diffs)
"""

from __future__ import annotations

import pytest

from apps.counselconduit.api.sandbox.firestore_bridge import (
    BridgeResult,
    DiffHunk,
    FirestoreBridge,
    _detect_language,
    _sha256,
    compute_diff,
)
from apps.counselconduit.api.sandbox.session import (
    SandboxSession,
    SecurityError,
    SessionConfig,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def session_config() -> SessionConfig:
    return SessionConfig(
        matter_id="matter-test-001",
        attorney_uid="attorney-uid-abc",
        trust_level=0,
    )


@pytest.fixture()
def session(session_config: SessionConfig) -> SandboxSession:
    return SandboxSession(config=session_config)


@pytest.fixture()
def reviewing_session(session: SandboxSession) -> SandboxSession:
    """A session already in REVIEWING state with overlay files."""
    session.start_speculation()
    session.present_for_review(
        overlay_files={
            "contracts/nda.md": "# NDA\n\nUpdated terms.\n",
            "contracts/engagement.md": "# Engagement Letter\n\nRevised scope.\n",
        },
        diff_summary=[{"path": "contracts/nda.md", "hunks": 1}],
    )
    return session


# ── Utility Tests ─────────────────────────────────────────────────────────


class TestLanguageDetection:
    def test_python_extension(self) -> None:
        assert _detect_language("src/main.py") == "python"

    def test_typescript_extension(self) -> None:
        assert _detect_language("components/App.tsx") == "typescriptreact"

    def test_unknown_extension(self) -> None:
        assert _detect_language("README") == "plaintext"

    def test_markdown_extension(self) -> None:
        assert _detect_language("docs/guide.md") == "markdown"


class TestSHA256:
    def test_deterministic(self) -> None:
        assert _sha256("hello") == _sha256("hello")

    def test_different_inputs(self) -> None:
        assert _sha256("hello") != _sha256("world")


# ── Diff Computation Tests ────────────────────────────────────────────────


class TestComputeDiff:
    def test_no_changes(self) -> None:
        content = "line 1\nline 2\nline 3\n"
        diff = compute_diff(content, content, "test.py")
        assert len(diff.hunks) == 0
        assert diff.original_hash == diff.overlay_hash

    def test_addition(self) -> None:
        original = "line 1\nline 2\n"
        overlay = "line 1\nline 2\nline 3\n"
        diff = compute_diff(original, overlay, "test.py")
        assert len(diff.hunks) >= 1
        add_changes = [c for h in diff.hunks for c in h.changes if c["type"] == "add"]
        assert any("line 3" in c["content"] for c in add_changes)

    def test_deletion(self) -> None:
        original = "line 1\nline 2\nline 3\n"
        overlay = "line 1\nline 3\n"
        diff = compute_diff(original, overlay, "test.py")
        assert len(diff.hunks) >= 1
        del_changes = [c for h in diff.hunks for c in h.changes if c["type"] == "delete"]
        assert any("line 2" in c["content"] for c in del_changes)

    def test_new_file(self) -> None:
        diff = compute_diff("", "new content\n", "new_file.ts")
        assert diff.language == "typescript"
        assert diff.original_hash != diff.overlay_hash
        assert len(diff.hunks) >= 1

    def test_privilege_propagation(self) -> None:
        diff = compute_diff(
            "old\n",
            "new\n",
            "doc.md",
            privilege_status="privileged",
            ai_confidence=0.92,
        )
        assert diff.privilege_status == "privileged"
        assert diff.ai_confidence == 0.92

    def test_to_dict_structure(self) -> None:
        diff = compute_diff("a\n", "b\n", "test.py")
        d = diff.to_dict()
        assert "path" in d
        assert "language" in d
        assert "hunks" in d
        assert "privilege_status" in d
        assert "ai_confidence" in d
        assert "original_hash" in d
        assert "overlay_hash" in d
        assert "hunk_count" in d


# ── DiffHunk Tests ────────────────────────────────────────────────────────


class TestDiffHunk:
    def test_to_dict(self) -> None:
        hunk = DiffHunk(
            old_start=1,
            old_lines=3,
            new_start=1,
            new_lines=4,
            changes=[{"type": "add", "content": "new line", "lineNumber": 4}],
        )
        d = hunk.to_dict()
        assert d["old_start"] == 1
        assert d["new_lines"] == 4
        assert len(d["changes"]) == 1

    def test_frozen_dataclass(self) -> None:
        hunk = DiffHunk(old_start=1, old_lines=1, new_start=1, new_lines=1)
        with pytest.raises(AttributeError):
            hunk.old_start = 99  # type: ignore[misc]


# ── BridgeResult Tests ────────────────────────────────────────────────────


class TestBridgeResult:
    def test_success_result(self) -> None:
        result = BridgeResult(
            success=True,
            committed_files=["a.py", "b.py"],
            audit_id="audit-123",
            duration_ms=42.5,
        )
        d = result.to_dict()
        assert d["success"] is True
        assert len(d["committed_files"]) == 2
        assert d["duration_ms"] == 42.5

    def test_failure_result(self) -> None:
        result = BridgeResult(success=False, error="Permission denied")
        assert result.to_dict()["error"] == "Permission denied"


# ── FirestoreBridge Security Tests ────────────────────────────────────────


class TestFirestoreBridgeSecurity:
    def test_rejects_non_zero_trust(self) -> None:
        """Trust Level != 0 must be rejected."""
        config = SessionConfig(matter_id="m1", attorney_uid="a1", trust_level=1)
        session = SandboxSession(config=config)
        with pytest.raises(SecurityError, match="Trust Level 0"):
            FirestoreBridge(session)

    def test_accepts_trust_level_zero(self, reviewing_session: SandboxSession) -> None:
        """Trust Level 0 must be accepted."""
        bridge = FirestoreBridge(reviewing_session)
        assert bridge.session is reviewing_session


# ── FirestoreBridge Diff Computation Tests ────────────────────────────────


class TestFirestoreBridgeDiffs:
    def test_compute_diffs_from_overlay(self, reviewing_session: SandboxSession) -> None:
        bridge = FirestoreBridge(reviewing_session)
        diffs = bridge.compute_diffs(
            original_files={
                "contracts/nda.md": "# NDA\n\nOriginal terms.\n",
            },
            privilege_map={"contracts/nda.md": "privileged"},
            confidence_map={"contracts/nda.md": 0.85},
        )
        assert len(diffs) == 2  # 2 overlay files
        nda_diff = next(d for d in diffs if d.path == "contracts/nda.md")
        assert nda_diff.privilege_status == "privileged"
        assert nda_diff.ai_confidence == 0.85

    def test_new_file_in_overlay(self, reviewing_session: SandboxSession) -> None:
        bridge = FirestoreBridge(reviewing_session)
        diffs = bridge.compute_diffs(
            original_files={},  # No originals — all new files
        )
        # Both overlay files should be treated as new
        assert all(d.original_hash != d.overlay_hash for d in diffs)
