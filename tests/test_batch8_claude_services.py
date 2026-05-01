# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for Batch 8 — magic_docs, plugin_manager, token_estimation.

Coverage targets:
- magic_docs.detector: Header detection, registration, clearing
- magic_docs.updater: Update prompt generation, rate limiting
- plugin_manager.manager: Diff, reconciliation, status tracking
- token_estimation.estimator: Token counting, model fallback
"""

from __future__ import annotations

import pathlib
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest


# ===================================================================
# magic_docs tests
# ===================================================================


class TestMagicDocDetector:
    """Tests for magic_docs.detector module."""

    def test_detect_basic_header(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        content = "# MAGIC DOC: Architecture Notes\n\nSome content here."
        result = detect_magic_doc_header(content)
        assert result is not None
        assert result.title == "Architecture Notes"
        assert result.instructions is None

    def test_detect_header_with_instructions(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        content = "# MAGIC DOC: API Reference\n_Keep this focused on public endpoints_\n\nContent."
        result = detect_magic_doc_header(content)
        assert result is not None
        assert result.title == "API Reference"
        assert result.instructions == "Keep this focused on public endpoints"

    def test_detect_header_case_insensitive(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        content = "# magic doc: My Document\nSome content."
        result = detect_magic_doc_header(content)
        assert result is not None
        assert result.title == "My Document"

    def test_no_header(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        content = "# Regular Header\n\nNo magic doc here."
        result = detect_magic_doc_header(content)
        assert result is None

    def test_empty_content(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        assert detect_magic_doc_header("") is None

    def test_register_and_get(self) -> None:
        from packages.magic_docs.detector import (
            clear_tracked_magic_docs,
            get_tracked_magic_docs,
            register_magic_doc,
        )

        clear_tracked_magic_docs()
        assert register_magic_doc("/tmp/test.md") is True
        assert register_magic_doc("/tmp/test.md") is False  # duplicate
        docs = get_tracked_magic_docs()
        assert len(docs) == 1
        assert docs[0].path == "/tmp/test.md"
        clear_tracked_magic_docs()

    def test_clear_tracked(self) -> None:
        from packages.magic_docs.detector import (
            clear_tracked_magic_docs,
            get_tracked_magic_docs,
            register_magic_doc,
        )

        clear_tracked_magic_docs()
        register_magic_doc("/tmp/a.md")
        register_magic_doc("/tmp/b.md")
        count = clear_tracked_magic_docs()
        assert count == 2
        assert len(get_tracked_magic_docs()) == 0

    def test_unregister(self) -> None:
        from packages.magic_docs.detector import (
            clear_tracked_magic_docs,
            get_tracked_magic_docs,
            register_magic_doc,
            unregister_magic_doc,
        )

        clear_tracked_magic_docs()
        register_magic_doc("/tmp/test.md")
        assert unregister_magic_doc("/tmp/test.md") is True
        assert unregister_magic_doc("/tmp/nonexistent.md") is False
        assert len(get_tracked_magic_docs()) == 0
        clear_tracked_magic_docs()

    def test_asterisk_italics(self) -> None:
        from packages.magic_docs.detector import detect_magic_doc_header

        content = "# MAGIC DOC: Test\n*Instructions with asterisks*\n\nBody."
        result = detect_magic_doc_header(content)
        assert result is not None
        assert result.instructions == "Instructions with asterisks"


class TestMagicDocUpdater:
    """Tests for magic_docs.updater module."""

    def test_update_single_valid(self, tmp_path: pathlib.Path) -> None:
        from packages.magic_docs.detector import clear_tracked_magic_docs, register_magic_doc
        from packages.magic_docs.updater import update_single_magic_doc

        clear_tracked_magic_docs()
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# MAGIC DOC: Test Title\n\nExisting content.")
        register_magic_doc(str(doc_path))

        prompt = update_single_magic_doc(str(doc_path), dry_run=True)
        assert prompt is not None
        assert "Test Title" in prompt
        assert "Existing content" in prompt
        clear_tracked_magic_docs()

    def test_update_missing_file(self) -> None:
        from packages.magic_docs.detector import clear_tracked_magic_docs, register_magic_doc
        from packages.magic_docs.updater import update_single_magic_doc

        clear_tracked_magic_docs()
        register_magic_doc("/nonexistent/path/test.md")
        result = update_single_magic_doc("/nonexistent/path/test.md")
        assert result is None
        clear_tracked_magic_docs()

    def test_update_removed_header(self, tmp_path: pathlib.Path) -> None:
        from packages.magic_docs.detector import clear_tracked_magic_docs, register_magic_doc
        from packages.magic_docs.updater import update_single_magic_doc

        clear_tracked_magic_docs()
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# Regular Header\n\nNo magic here.")
        register_magic_doc(str(doc_path))

        result = update_single_magic_doc(str(doc_path))
        assert result is None
        clear_tracked_magic_docs()

    def test_update_all_empty(self) -> None:
        from packages.magic_docs.detector import clear_tracked_magic_docs
        from packages.magic_docs.updater import update_magic_docs

        clear_tracked_magic_docs()
        results = update_magic_docs()
        assert results == {}


# ===================================================================
# plugin_manager tests
# ===================================================================


class TestPluginInstallationManager:
    """Tests for plugin_manager.manager module."""

    def test_marketplace_status_defaults(self) -> None:
        from packages.plugin_manager.manager import InstallationStatus, MarketplaceStatus

        status = MarketplaceStatus(name="test-marketplace")
        assert status.status == InstallationStatus.PENDING
        assert status.error == ""
        assert status.updated_at > 0

    def test_reconciliation_result_defaults(self) -> None:
        from packages.plugin_manager.manager import ReconciliationResult

        result = ReconciliationResult()
        assert result.installed == []
        assert result.updated == []
        assert result.failed == []
        assert result.up_to_date == []
        assert result.duration_ms == 0.0

    def test_diff_marketplaces(self, tmp_path: pathlib.Path) -> None:
        from packages.plugin_manager.manager import PluginInstallationManager

        skills_dir = tmp_path / "skills"
        repos_dir = tmp_path / "repos"
        skills_dir.mkdir()
        repos_dir.mkdir()

        # Create one existing repo with .git
        existing = repos_dir / "existing-repo"
        existing.mkdir()
        (existing / ".git").mkdir()

        # Create one without .git (needs update)
        no_git = repos_dir / "no-git-repo"
        no_git.mkdir()

        mgr = PluginInstallationManager(skills_dir, repos_dir)
        declared = [
            {"name": "existing-repo", "path": str(existing), "source": "https://example.com/a"},
            {"name": "no-git-repo", "path": str(no_git), "source": "https://example.com/b"},
            {"name": "missing-repo", "path": str(repos_dir / "missing"), "source": "https://example.com/c"},
        ]

        missing, changed, up_to_date = mgr.diff_marketplaces(declared)
        assert "missing-repo" in missing
        assert "no-git-repo" in changed
        assert "existing-repo" in up_to_date

    def test_progress_callback(self, tmp_path: pathlib.Path) -> None:
        from packages.plugin_manager.manager import PluginInstallationManager

        mgr = PluginInstallationManager(tmp_path / "skills", tmp_path / "repos")
        events: list[tuple[str, str]] = []
        mgr.set_progress_callback(lambda name, status, err: events.append((name, status)))

        # Initialize a status first
        from packages.plugin_manager.manager import MarketplaceStatus
        mgr._statuses["test"] = MarketplaceStatus(name="test")

        mgr._emit_progress("test", "installing")
        mgr._emit_progress("test", "installed")
        assert len(events) == 2
        assert events[0] == ("test", "installing")
        assert events[1] == ("test", "installed")

    def test_clear_caches(self, tmp_path: pathlib.Path) -> None:
        from packages.plugin_manager.manager import MarketplaceStatus, PluginInstallationManager

        mgr = PluginInstallationManager(tmp_path / "skills", tmp_path / "repos")
        mgr._statuses["a"] = MarketplaceStatus(name="a")
        mgr.clear_caches()
        assert len(mgr.get_statuses()) == 0

    def test_get_declared_marketplaces_empty(self, tmp_path: pathlib.Path) -> None:
        from packages.plugin_manager.manager import PluginInstallationManager

        mgr = PluginInstallationManager(tmp_path / "skills", tmp_path / "repos")
        declared = mgr.get_declared_marketplaces()
        assert declared == []

    def test_get_declared_marketplaces_with_repos(self, tmp_path: pathlib.Path) -> None:
        from packages.plugin_manager.manager import PluginInstallationManager

        repos_dir = tmp_path / "repos"
        repos_dir.mkdir()
        (repos_dir / "google-skills").mkdir()
        (repos_dir / "vercel-skills").mkdir()

        mgr = PluginInstallationManager(tmp_path / "skills", repos_dir)
        declared = mgr.get_declared_marketplaces()
        names = [d["name"] for d in declared]
        assert "google-skills" in names
        assert "vercel-skills" in names


# ===================================================================
# token_estimation tests
# ===================================================================


class TestTokenEstimation:
    """Tests for token_estimation.estimator module."""

    def test_estimate_tokens_simple(self) -> None:
        from packages.token_estimation import estimate_tokens

        count = estimate_tokens("Hello, world!")
        assert count > 0
        assert isinstance(count, int)

    def test_estimate_tokens_empty(self) -> None:
        from packages.token_estimation import estimate_tokens

        count = estimate_tokens("")
        assert count == 0

    def test_estimate_tokens_unicode(self) -> None:
        from packages.token_estimation import estimate_tokens

        count = estimate_tokens("こんにちは世界 🌍")
        assert count > 0

    def test_estimate_tokens_long_text(self) -> None:
        from packages.token_estimation import estimate_tokens

        text = "word " * 10000
        count = estimate_tokens(text)
        # ~10000 words ≈ ~10000-13000 tokens
        assert 5000 < count < 20000

    def test_model_specific_estimation(self) -> None:
        from packages.token_estimation import estimate_tokens

        text = "This is a test sentence."
        count_default = estimate_tokens(text)
        count_gemini = estimate_tokens(text, model="gemini-3.1-flash")
        # Both should return reasonable counts
        assert count_default > 0
        assert count_gemini > 0
