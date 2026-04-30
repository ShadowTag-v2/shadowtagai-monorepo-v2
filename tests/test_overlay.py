# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for orbstack_sandbox.overlay module."""

from __future__ import annotations

from pathlib import Path

import pytest

from orbstack_sandbox.overlay import OverlayDiff, OverlayManager


class TestOverlayDiff:
    def test_empty_diff(self) -> None:
        diff = OverlayDiff()
        assert not diff.has_changes
        assert diff.file_count == 0

    def test_has_changes(self) -> None:
        diff = OverlayDiff(created=["a.py"])
        assert diff.has_changes
        assert diff.file_count == 1

    def test_to_dict(self) -> None:
        diff = OverlayDiff(created=["a.py"], modified=["b.py"])
        d = diff.to_dict()
        assert d["file_count"] == 2
        assert "a.py" in d["created"]


class TestOverlayManager:
    def test_create_overlay(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        path = mgr.create("test-session")
        assert path.exists()
        assert "test-session" in mgr.list_active()

    def test_create_duplicate_raises(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        mgr.create("dup-session")
        with pytest.raises(ValueError, match="already exists"):
            mgr.create("dup-session")

    def test_get_path(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        mgr.create("s1")
        assert mgr.get_path("s1") is not None
        assert mgr.get_path("nonexistent") is None

    def test_compute_diff_created(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        overlay_path = mgr.create("s1")
        # Write a new file to overlay.
        (overlay_path / "new_file.py").write_text("print('hello')")
        diff = mgr.compute_diff("s1")
        assert "new_file.py" in diff.created
        assert diff.has_changes

    def test_compute_diff_modified(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        # Create workspace file.
        (tmp_path / "existing.py").write_text("original")
        overlay_path = mgr.create("s2")
        # Modify in overlay.
        (overlay_path / "existing.py").write_text("modified")
        diff = mgr.compute_diff("s2")
        assert "existing.py" in diff.modified

    def test_compute_diff_unchanged(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        (tmp_path / "same.py").write_text("content")
        overlay_path = mgr.create("s3")
        (overlay_path / "same.py").write_text("content")
        diff = mgr.compute_diff("s3")
        assert not diff.has_changes

    def test_merge_to_workspace(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        overlay_path = mgr.create("merge-test")
        (overlay_path / "merged.py").write_text("merged content")
        count = mgr.merge_to_workspace("merge-test")
        assert count == 1
        assert (tmp_path / "merged.py").read_text() == "merged content"

    def test_merge_filtered(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        overlay_path = mgr.create("filter-test")
        (overlay_path / "allowed.py").write_text("yes")
        (overlay_path / "blocked.py").write_text("no")
        count = mgr.merge_to_workspace("filter-test", allowed_paths=["allowed.py"])
        assert count == 1
        assert (tmp_path / "allowed.py").exists()
        assert not (tmp_path / "blocked.py").exists()

    def test_destroy(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        overlay_path = mgr.create("destroy-test")
        assert overlay_path.exists()
        result = mgr.destroy("destroy-test")
        assert result is True
        assert not overlay_path.exists()
        assert "destroy-test" not in mgr.list_active()

    def test_destroy_nonexistent(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        assert mgr.destroy("nope") is False

    def test_disk_pressure_ok(self, tmp_path: Path) -> None:
        mgr = OverlayManager(workspace_root=tmp_path)
        mgr.create("pressure-test")
        assert mgr.check_disk_pressure("pressure-test") is True
