# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for Firestore Bridge — Phase 3 Milestone 5.

Tests the diff computation engine and bridge lifecycle without requiring
a live Firestore emulator. Firestore write operations are mocked.

Coverage targets:
  - compute_diff: hunk parsing, language detection, hash integrity
  - FirestoreBridge.compute_diffs: multi-file overlay diffing
  - FirestoreBridge.commit_to_firestore: accept/reject/partial flows
  - Security: Trust Level 0 enforcement, attorney UID validation
  - Edge cases: empty files, new files, binary-like content
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, patch

import pytest

from apps.counselconduit.api.sandbox.firestore_bridge import (
  BridgeResult,
  DiffHunk,
  FirestoreBridge,
  compute_diff,
  _detect_language,
  _parse_unified_diff,
  _sha256,
)
from apps.counselconduit.api.sandbox.session import (
  CommitAction,
  SandboxSession,
  SecurityError,
  SessionConfig,
  SessionState,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def session_config() -> SessionConfig:
  """Standard test session config — Trust Level 0."""
  return SessionConfig(
    matter_id="matter-test-001",
    attorney_uid="attorney-uid-abc",
    trust_level=0,
  )


@pytest.fixture()
def reviewing_session(session_config: SessionConfig) -> SandboxSession:
  """Session pre-loaded in REVIEWING state with overlay files."""
  session = SandboxSession(
    session_id="test-session-001",
    config=session_config,
    state=SessionState.REVIEWING,
    overlay_files={
      "brief.md": "# Updated Brief\n\nNew content here.\n",
      "memo.py": "def analyze():\n    return 'privileged'\n",
    },
  )
  return session


@pytest.fixture()
def bridge(reviewing_session: SandboxSession) -> FirestoreBridge:
  """Initialized FirestoreBridge with reviewing session."""
  return FirestoreBridge(session=reviewing_session)


# ── Unit: Language Detection ──────────────────────────────────────────────


class TestDetectLanguage:
  """Tests for _detect_language utility."""

  def test_python(self) -> None:
    assert _detect_language("src/main.py") == "python"

  def test_typescript(self) -> None:
    assert _detect_language("app/page.ts") == "typescript"

  def test_tsx(self) -> None:
    assert _detect_language("components/Button.tsx") == "typescriptreact"

  def test_javascript(self) -> None:
    assert _detect_language("index.js") == "javascript"

  def test_json(self) -> None:
    assert _detect_language("package.json") == "json"

  def test_markdown(self) -> None:
    assert _detect_language("README.md") == "markdown"

  def test_yaml(self) -> None:
    assert _detect_language("config.yaml") == "yaml"

  def test_yml_variant(self) -> None:
    assert _detect_language("docker-compose.yml") == "yaml"

  def test_css(self) -> None:
    assert _detect_language("styles.css") == "css"

  def test_unknown_extension(self) -> None:
    assert _detect_language("data.xyz") == "plaintext"

  def test_no_extension(self) -> None:
    assert _detect_language("Makefile") == "plaintext"

  def test_csharp(self) -> None:
    assert _detect_language("Program.cs") == "csharp"

  def test_go(self) -> None:
    assert _detect_language("main.go") == "go"


# ── Unit: SHA-256 Hashing ─────────────────────────────────────────────────


class TestSha256:
  """Tests for _sha256 content hashing."""

  def test_empty_string(self) -> None:
    expected = hashlib.sha256(b"").hexdigest()
    assert _sha256("") == expected

  def test_known_value(self) -> None:
    expected = hashlib.sha256(b"hello").hexdigest()
    assert _sha256("hello") == expected

  def test_unicode_content(self) -> None:
    content = "日本語テスト"
    expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert _sha256(content) == expected

  def test_deterministic(self) -> None:
    assert _sha256("test") == _sha256("test")

  def test_different_content(self) -> None:
    assert _sha256("foo") != _sha256("bar")


# ── Unit: Diff Computation ────────────────────────────────────────────────


class TestComputeDiff:
  """Tests for compute_diff function."""

  def test_identical_content_no_hunks(self) -> None:
    """Identical files should produce zero hunks."""
    result = compute_diff("line1\nline2\n", "line1\nline2\n", "test.py")
    assert len(result.hunks) == 0
    assert result.path == "test.py"
    assert result.language == "python"

  def test_simple_addition(self) -> None:
    """Adding a line should produce a hunk with an add change."""
    original = "line1\nline2\n"
    overlay = "line1\nline2\nline3\n"
    result = compute_diff(original, overlay, "test.ts")
    assert len(result.hunks) >= 1
    assert result.language == "typescript"
    # At least one 'add' change
    all_changes = [c for h in result.hunks for c in h.changes]
    add_changes = [c for c in all_changes if c["type"] == "add"]
    assert len(add_changes) >= 1

  def test_simple_deletion(self) -> None:
    """Removing a line should produce a hunk with a delete change."""
    original = "line1\nline2\nline3\n"
    overlay = "line1\nline3\n"
    result = compute_diff(original, overlay, "test.py")
    assert len(result.hunks) >= 1
    all_changes = [c for h in result.hunks for c in h.changes]
    delete_changes = [c for c in all_changes if c["type"] == "delete"]
    assert len(delete_changes) >= 1

  def test_modification(self) -> None:
    """Changing a line should produce both delete and add changes."""
    original = "old_value = True\n"
    overlay = "new_value = False\n"
    result = compute_diff(original, overlay, "config.py")
    all_changes = [c for h in result.hunks for c in h.changes]
    assert any(c["type"] == "delete" for c in all_changes)
    assert any(c["type"] == "add" for c in all_changes)

  def test_new_file(self) -> None:
    """Diffing against empty original should work for new files."""
    result = compute_diff("", "new content\n", "new_file.ts")
    assert len(result.hunks) >= 1
    assert result.original_hash == _sha256("")
    assert result.overlay_hash == _sha256("new content\n")

  def test_empty_overlay(self) -> None:
    """Diffing to empty overlay (file deletion) produces hunks."""
    result = compute_diff("content\n", "", "deleted.md")
    assert len(result.hunks) >= 1

  def test_privilege_status_preserved(self) -> None:
    result = compute_diff("a\n", "b\n", "doc.md", privilege_status="privileged")
    assert result.privilege_status == "privileged"

  def test_ai_confidence_preserved(self) -> None:
    result = compute_diff("a\n", "b\n", "doc.md", ai_confidence=0.95)
    assert result.ai_confidence == 0.95

  def test_hash_integrity(self) -> None:
    """Original and overlay hashes should match SHA-256 of content."""
    original = "original content\n"
    overlay = "overlay content\n"
    result = compute_diff(original, overlay, "test.py")
    assert result.original_hash == _sha256(original)
    assert result.overlay_hash == _sha256(overlay)

  def test_to_dict_structure(self) -> None:
    """to_dict should produce the expected JSON-serializable structure."""
    result = compute_diff("a\n", "b\n", "test.py", privilege_status="work_product")
    d = result.to_dict()
    assert "path" in d
    assert "language" in d
    assert "hunks" in d
    assert "privilege_status" in d
    assert d["privilege_status"] == "work_product"
    assert "hunk_count" in d
    assert "original_hash" in d
    assert "overlay_hash" in d

  def test_multiline_diff(self) -> None:
    """Multi-line changes produce correct hunk structure."""
    original = "line1\nline2\nline3\nline4\nline5\n"
    overlay = "line1\nMODIFIED\nline3\nline4\nADDED\nline5\n"
    result = compute_diff(original, overlay, "big.py")
    assert len(result.hunks) >= 1
    total_changes = sum(len(h.changes) for h in result.hunks)
    assert total_changes >= 2  # At least the modification + addition


# ── Unit: Unified Diff Parser ─────────────────────────────────────────────


class TestParseUnifiedDiff:
  """Tests for _parse_unified_diff hunk parser."""

  def test_empty_diff(self) -> None:
    assert _parse_unified_diff([]) == []

  def test_single_hunk(self) -> None:
    diff_lines = [
      "--- a/test.py\n",
      "+++ b/test.py\n",
      "@@ -1,3 +1,3 @@\n",
      " line1\n",
      "-old\n",
      "+new\n",
      " line3\n",
    ]
    hunks = _parse_unified_diff(diff_lines)
    assert len(hunks) == 1
    assert hunks[0].old_start == 1
    assert hunks[0].new_start == 1

  def test_multiple_hunks(self) -> None:
    diff_lines = [
      "--- a/test.py\n",
      "+++ b/test.py\n",
      "@@ -1,3 +1,3 @@\n",
      " context\n",
      "-old1\n",
      "+new1\n",
      "@@ -10,3 +10,3 @@\n",
      " context2\n",
      "-old2\n",
      "+new2\n",
    ]
    hunks = _parse_unified_diff(diff_lines)
    assert len(hunks) == 2
    assert hunks[0].old_start == 1
    assert hunks[1].old_start == 10

  def test_change_types_correct(self) -> None:
    diff_lines = [
      "@@ -1,3 +1,3 @@\n",
      " context\n",
      "-deleted\n",
      "+added\n",
    ]
    hunks = _parse_unified_diff(diff_lines)
    changes = hunks[0].changes
    types = [c["type"] for c in changes]
    assert "context" in types
    assert "delete" in types
    assert "add" in types


# ── Integration: FirestoreBridge ──────────────────────────────────────────


class TestFirestoreBridgeInit:
  """Tests for FirestoreBridge initialization and security."""

  def test_trust_level_0_required(self) -> None:
    """Bridge MUST reject sessions with trust_level != 0."""
    config = SessionConfig(
      matter_id="m-1",
      attorney_uid="a-1",
      trust_level=1,  # NOT zero
    )
    session = SandboxSession(config=config, state=SessionState.REVIEWING)
    with pytest.raises(SecurityError, match="Trust Level 0"):
      FirestoreBridge(session=session)

  def test_trust_level_0_accepted(self, reviewing_session: SandboxSession) -> None:
    """Bridge accepts Trust Level 0 sessions."""
    bridge = FirestoreBridge(session=reviewing_session)
    assert bridge.session.config.trust_level == 0


class TestBridgeComputeDiffs:
  """Tests for FirestoreBridge.compute_diffs."""

  def test_diffs_computed_for_overlay_files(self, bridge: FirestoreBridge) -> None:
    """Should compute diffs for every file in the overlay."""
    originals = {
      "brief.md": "# Original Brief\n",
      "memo.py": "def analyze():\n    pass\n",
    }
    diffs = bridge.compute_diffs(originals)
    assert len(diffs) == 2
    paths = {d.path for d in diffs}
    assert "brief.md" in paths
    assert "memo.py" in paths

  def test_new_file_in_overlay(self, bridge: FirestoreBridge) -> None:
    """Files in overlay but not in originals should diff against empty."""
    originals = {}  # No originals — all files are new
    diffs = bridge.compute_diffs(originals)
    assert len(diffs) == 2
    for diff in diffs:
      assert diff.original_hash == _sha256("")

  def test_privilege_map_applied(self, bridge: FirestoreBridge) -> None:
    """Privilege status should be correctly mapped per file."""
    originals = {"brief.md": "", "memo.py": ""}
    privilege_map = {"brief.md": "privileged", "memo.py": "work_product"}
    diffs = bridge.compute_diffs(originals, privilege_map=privilege_map)
    priv = {d.path: d.privilege_status for d in diffs}
    assert priv["brief.md"] == "privileged"
    assert priv["memo.py"] == "work_product"

  def test_confidence_map_applied(self, bridge: FirestoreBridge) -> None:
    """AI confidence scores should be correctly mapped per file."""
    originals = {"brief.md": "", "memo.py": ""}
    confidence_map = {"brief.md": 0.9, "memo.py": 0.3}
    diffs = bridge.compute_diffs(originals, confidence_map=confidence_map)
    conf = {d.path: d.ai_confidence for d in diffs}
    assert conf["brief.md"] == 0.9
    assert conf["memo.py"] == 0.3

  def test_default_privilege_public(self, bridge: FirestoreBridge) -> None:
    """Default privilege status should be 'public'."""
    diffs = bridge.compute_diffs({})
    for diff in diffs:
      assert diff.privilege_status == "public"

  def test_default_confidence_half(self, bridge: FirestoreBridge) -> None:
    """Default AI confidence should be 0.5."""
    diffs = bridge.compute_diffs({})
    for diff in diffs:
      assert diff.ai_confidence == 0.5


class TestBridgeCommit:
  """Tests for FirestoreBridge.commit_to_firestore."""

  @pytest.mark.asyncio()
  async def test_accept_commits_all_files(self, bridge: FirestoreBridge) -> None:
    """ACCEPT should commit all overlay files."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock) as mock_write,
      patch.object(
        bridge, "_write_audit", new_callable=AsyncMock, return_value="audit-001"
      ),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.ACCEPT,
        attorney_uid="attorney-uid-abc",
        firm_id="firm-001",
      )
    assert result.success is True
    assert len(result.committed_files) == 2
    mock_write.assert_awaited_once()

  @pytest.mark.asyncio()
  async def test_reject_no_writes(self, bridge: FirestoreBridge) -> None:
    """REJECT should produce no Firestore writes."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock) as mock_write,
      patch.object(
        bridge, "_write_audit", new_callable=AsyncMock, return_value="audit-002"
      ),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.REJECT,
        attorney_uid="attorney-uid-abc",
        firm_id="firm-001",
        rejection_reason="Not approved",
      )
    assert result.success is True
    assert len(result.rejected_files) == 2
    assert len(result.committed_files) == 0
    mock_write.assert_not_awaited()

  @pytest.mark.asyncio()
  async def test_partial_accept_selected_files(self, bridge: FirestoreBridge) -> None:
    """PARTIAL_ACCEPT should only commit selected files."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock) as mock_write,
      patch.object(
        bridge, "_write_audit", new_callable=AsyncMock, return_value="audit-003"
      ),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.PARTIAL_ACCEPT,
        attorney_uid="attorney-uid-abc",
        firm_id="firm-001",
        selected_files=["brief.md"],
      )
    assert result.success is True
    assert "brief.md" in result.committed_files
    mock_write.assert_awaited_once()

  @pytest.mark.asyncio()
  async def test_wrong_attorney_uid_rejected(self, bridge: FirestoreBridge) -> None:
    """Commit with wrong attorney UID should fail."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock),
      patch.object(bridge, "_write_audit", new_callable=AsyncMock, return_value=""),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.ACCEPT,
        attorney_uid="wrong-uid",
        firm_id="firm-001",
      )
    # Session.commit() should raise PermissionError for wrong UID
    assert result.success is False

  @pytest.mark.asyncio()
  async def test_audit_id_returned(self, bridge: FirestoreBridge) -> None:
    """Audit ID should be populated in the result."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock),
      patch.object(
        bridge, "_write_audit", new_callable=AsyncMock, return_value="audit-xyz"
      ),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.ACCEPT,
        attorney_uid="attorney-uid-abc",
        firm_id="firm-001",
      )
    assert result.audit_id == "audit-xyz"

  @pytest.mark.asyncio()
  async def test_duration_ms_populated(self, bridge: FirestoreBridge) -> None:
    """Duration should be positive after commit."""
    with (
      patch.object(bridge, "_write_documents", new_callable=AsyncMock),
      patch.object(
        bridge, "_write_audit", new_callable=AsyncMock, return_value="aud-1"
      ),
    ):
      result = await bridge.commit_to_firestore(
        action=CommitAction.ACCEPT,
        attorney_uid="attorney-uid-abc",
        firm_id="firm-001",
      )
    assert result.duration_ms >= 0


# ── Data Structure Serialization ──────────────────────────────────────────


class TestDiffHunkSerialization:
  """Tests for DiffHunk.to_dict."""

  def test_round_trip(self) -> None:
    hunk = DiffHunk(
      old_start=10,
      old_lines=3,
      new_start=10,
      new_lines=4,
      changes=[{"type": "add", "content": "new line", "lineNumber": 12}],
    )
    d = hunk.to_dict()
    assert d["old_start"] == 10
    assert d["new_lines"] == 4
    assert len(d["changes"]) == 1


class TestBridgeResultSerialization:
  """Tests for BridgeResult.to_dict."""

  def test_success_result(self) -> None:
    result = BridgeResult(
      success=True,
      committed_files=["a.py", "b.py"],
      audit_id="aud-1",
      duration_ms=42.5,
    )
    d = result.to_dict()
    assert d["success"] is True
    assert len(d["committed_files"]) == 2
    assert d["audit_id"] == "aud-1"
    assert d["duration_ms"] == 42.5

  def test_failure_result(self) -> None:
    result = BridgeResult(success=False, error="Trust violation")
    d = result.to_dict()
    assert d["success"] is False
    assert d["error"] == "Trust violation"
