# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Test suite for the Magic Docs package (CP-09).

Validates header detection, registration, update prompts, and rate limiting
against the Claude Code v2.1.91 MagicDocs/magicDocs.ts contract.
"""

from __future__ import annotations


import pytest

from packages.magic_docs.detector import (
  MagicDocHeader,
  MagicDocInfo,
  clear_tracked_magic_docs,
  detect_magic_doc_header,
  get_tracked_magic_docs,
  register_magic_doc,
  unregister_magic_doc,
)
from packages.magic_docs.updater import (
  update_magic_docs,
  update_single_magic_doc,
)


# ── Detection tests ─────────────────────────────────────────────────────


class TestDetectMagicDocHeader:
  """Verify header detection parity with TS original."""

  def test_basic_header(self) -> None:
    content = "# MAGIC DOC: Architecture Notes\nSome content here"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.title == "Architecture Notes"
    assert result.instructions is None

  def test_header_with_instructions(self) -> None:
    content = "# MAGIC DOC: API Guide\n_Focus on REST endpoints_\nContent"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.title == "API Guide"
    assert result.instructions == "Focus on REST endpoints"

  def test_header_with_asterisk_italics(self) -> None:
    content = "# MAGIC DOC: Notes\n*Update only the summary section*\nBody"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.instructions == "Update only the summary section"

  def test_header_case_insensitive(self) -> None:
    content = "# magic doc: Lower Case Title\nBody text"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.title == "Lower Case Title"

  def test_no_header(self) -> None:
    content = "# Regular Heading\nJust a normal markdown file"
    assert detect_magic_doc_header(content) is None

  def test_empty_content(self) -> None:
    assert detect_magic_doc_header("") is None

  def test_header_with_blank_line_before_instructions(self) -> None:
    content = "# MAGIC DOC: Test\n\n_These are instructions_\nBody"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.instructions == "These are instructions"

  def test_non_italic_line_after_header(self) -> None:
    content = "# MAGIC DOC: Readme\nNot italic text\nBody"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.instructions is None

  def test_header_embedded_in_content(self) -> None:
    """Header can appear on any line (MULTILINE flag)."""
    content = "Some preamble\n# MAGIC DOC: Embedded\nBody"
    result = detect_magic_doc_header(content)
    assert result is not None
    assert result.title == "Embedded"


# ── Registration tests ───────────────────────────────────────────────────


class TestMagicDocRegistration:
  """Validate thread-safe registration and tracking."""

  def setup_method(self) -> None:
    clear_tracked_magic_docs()

  def teardown_method(self) -> None:
    clear_tracked_magic_docs()

  def test_register_new_doc(self) -> None:
    assert register_magic_doc("/tmp/test.md") is True
    docs = get_tracked_magic_docs()
    assert len(docs) == 1
    assert docs[0].path == "/tmp/test.md"

  def test_register_duplicate(self) -> None:
    register_magic_doc("/tmp/test.md")
    assert register_magic_doc("/tmp/test.md") is False
    assert len(get_tracked_magic_docs()) == 1

  def test_unregister_existing(self) -> None:
    register_magic_doc("/tmp/test.md")
    assert unregister_magic_doc("/tmp/test.md") is True
    assert len(get_tracked_magic_docs()) == 0

  def test_unregister_nonexistent(self) -> None:
    assert unregister_magic_doc("/tmp/nonexistent.md") is False

  def test_clear_returns_count(self) -> None:
    register_magic_doc("/tmp/a.md")
    register_magic_doc("/tmp/b.md")
    register_magic_doc("/tmp/c.md")
    assert clear_tracked_magic_docs() == 3
    assert clear_tracked_magic_docs() == 0

  def test_register_multiple_unique(self) -> None:
    for i in range(5):
      register_magic_doc(f"/tmp/doc_{i}.md")
    assert len(get_tracked_magic_docs()) == 5


# ── Updater tests ────────────────────────────────────────────────────────


class TestMagicDocUpdater:
  """Test prompt generation and update lifecycle."""

  def setup_method(self) -> None:
    clear_tracked_magic_docs()

  def teardown_method(self) -> None:
    clear_tracked_magic_docs()

  def test_update_generates_prompt(self, tmp_path) -> None:
    doc = tmp_path / "test.md"
    doc.write_text("# MAGIC DOC: Test Doc\nSome content")
    result = update_single_magic_doc(str(doc), dry_run=True)
    assert result is not None
    assert "Test Doc" in result
    assert str(doc) in result

  def test_update_missing_file(self) -> None:
    result = update_single_magic_doc("/nonexistent/path.md")
    assert result is None

  def test_update_non_magic_doc(self, tmp_path) -> None:
    doc = tmp_path / "plain.md"
    doc.write_text("# Regular Document\nNo magic here")
    result = update_single_magic_doc(str(doc))
    assert result is None

  def test_update_with_instructions(self, tmp_path) -> None:
    doc = tmp_path / "test.md"
    doc.write_text("# MAGIC DOC: API Ref\n_Only update endpoints_\nContent")
    result = update_single_magic_doc(str(doc), dry_run=True)
    assert result is not None
    assert "Only update endpoints" in result

  def test_rate_limiting(self, tmp_path) -> None:
    """Verify update_magic_docs respects rate limiting."""
    doc = tmp_path / "test.md"
    doc.write_text("# MAGIC DOC: Rate Test\nBody")
    register_magic_doc(str(doc))

    # First update should work.
    results = update_magic_docs()
    assert str(doc) in results
    assert results[str(doc)] is not None

    # Immediate second update should be rate-limited.
    results = update_magic_docs()
    assert str(doc) not in results  # skipped by rate limiter

  def test_batch_update_multiple(self, tmp_path) -> None:
    for i in range(3):
      d = tmp_path / f"doc_{i}.md"
      d.write_text(f"# MAGIC DOC: Doc {i}\nContent {i}")
      register_magic_doc(str(d))

    results = update_magic_docs()
    assert len(results) == 3
    assert all(v is not None for v in results.values())

  def test_dry_run_no_side_effects(self, tmp_path) -> None:
    doc = tmp_path / "test.md"
    doc.write_text("# MAGIC DOC: DryRun Test\nBody")
    result = update_single_magic_doc(str(doc), dry_run=True)
    assert result is not None
    # Dry run should not update the rate limiter — a subsequent call
    # should not be rate limited.
    result2 = update_single_magic_doc(str(doc), dry_run=True)
    assert result2 is not None


# ── Data class tests ─────────────────────────────────────────────────────


class TestDataClasses:
  def test_magic_doc_header_frozen(self) -> None:
    h = MagicDocHeader(title="Test")
    with pytest.raises(AttributeError):
      h.title = "Changed"  # type: ignore[misc]

  def test_magic_doc_info_frozen(self) -> None:
    info = MagicDocInfo(path="/tmp/test.md")
    with pytest.raises(AttributeError):
      info.path = "/other"  # type: ignore[misc]
