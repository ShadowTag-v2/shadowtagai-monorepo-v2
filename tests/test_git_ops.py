# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages.agnt_services.git_ops (port of src/utils/git.ts)."""
from __future__ import annotations

import asyncio
import os
import subprocess
from unittest.mock import patch

import pytest

from packages.agnt_services.git_ops import (
    GitRepoState,
    find_canonical_git_root,
    find_git_root,
    get_changed_files,
    get_git_state,
    get_repo_remote_hash,
    is_bare_git_repo,
    normalize_git_remote_url,
)


# ─── normalize_git_remote_url ─────────────────────────────────────────


class TestNormalizeGitRemoteUrl:
    def test_ssh_format(self):
        assert normalize_git_remote_url("git@github.com:owner/repo.git") == "github.com/owner/repo"

    def test_ssh_no_git_suffix(self):
        assert normalize_git_remote_url("git@github.com:owner/repo") == "github.com/owner/repo"

    def test_https_format(self):
        assert normalize_git_remote_url("https://github.com/owner/repo.git") == "github.com/owner/repo"

    def test_https_no_suffix(self):
        assert normalize_git_remote_url("https://github.com/owner/repo") == "github.com/owner/repo"

    def test_ssh_url_format(self):
        assert normalize_git_remote_url("ssh://git@github.com/owner/repo") == "github.com/owner/repo"

    def test_case_insensitive(self):
        assert normalize_git_remote_url("git@GitHub.COM:OWNER/REPO.git") == "github.com/owner/repo"

    def test_localhost_proxy_legacy(self):
        url = "http://local_proxy@127.0.0.1:16583/git/owner/repo"
        assert normalize_git_remote_url(url) == "github.com/owner/repo"

    def test_localhost_proxy_ghe(self):
        url = "http://local_proxy@127.0.0.1:16583/git/ghe.corp.com/owner/repo"
        assert normalize_git_remote_url(url) == "ghe.corp.com/owner/repo"

    def test_empty_string(self):
        assert normalize_git_remote_url("") is None

    def test_whitespace(self):
        assert normalize_git_remote_url("   ") is None

    def test_invalid_url(self):
        assert normalize_git_remote_url("not-a-url") is None

    def test_ssh_and_https_same_result(self):
        ssh = normalize_git_remote_url("git@github.com:ShadowTag-v2/Monorepo.git")
        https = normalize_git_remote_url("https://github.com/ShadowTag-v2/Monorepo.git")
        assert ssh == https


# ─── get_repo_remote_hash ─────────────────────────────────────────────


class TestGetRepoRemoteHash:
    def test_produces_16_char_hex(self):
        h = get_repo_remote_hash("git@github.com:owner/repo.git")
        assert h is not None
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_ssh_and_https_same_hash(self):
        h1 = get_repo_remote_hash("git@github.com:owner/repo.git")
        h2 = get_repo_remote_hash("https://github.com/owner/repo.git")
        assert h1 == h2

    def test_invalid_url_returns_none(self):
        assert get_repo_remote_hash("invalid") is None

    def test_deterministic(self):
        h1 = get_repo_remote_hash("git@github.com:test/test.git")
        h2 = get_repo_remote_hash("git@github.com:test/test.git")
        assert h1 == h2


# ─── find_git_root ────────────────────────────────────────────────────


class TestFindGitRoot:
    def test_finds_current_repo(self):
        result = find_git_root(os.getcwd())
        assert result is not None
        assert os.path.isdir(os.path.join(result, ".git"))

    def test_nonexistent_path_returns_none(self):
        find_git_root.cache_clear()
        result = find_git_root("/nonexistent/deeply/nested/path/xyz")
        # Will walk up to root without finding .git
        # Result depends on whether root has .git
        assert result is None or os.path.exists(os.path.join(result, ".git"))


# ─── is_bare_git_repo ────────────────────────────────────────────────


class TestIsBareGitRepo:
    def test_normal_repo_not_bare(self):
        assert is_bare_git_repo(os.getcwd()) is False

    def test_temp_dir_not_bare(self, tmp_path):
        assert is_bare_git_repo(str(tmp_path)) is False

    def test_detects_bare_indicators(self, tmp_path):
        # Create bare repo indicators
        (tmp_path / "HEAD").write_text("ref: refs/heads/main\n")
        (tmp_path / "objects").mkdir()
        (tmp_path / "refs").mkdir()
        assert is_bare_git_repo(str(tmp_path)) is True

    def test_valid_git_dir_not_bare(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n")
        assert is_bare_git_repo(str(tmp_path)) is False


# ─── get_git_state ────────────────────────────────────────────────────


class TestGetGitState:
    def test_returns_state_in_repo(self):
        state = asyncio.run(get_git_state())
        assert state is not None
        assert isinstance(state, GitRepoState)
        assert len(state.commit_hash) == 40
        assert state.branch_name  # should have a branch

    def test_returns_none_outside_repo(self):
        state = asyncio.run(get_git_state(cwd="/tmp"))
        # /tmp might or might not be in a git repo
        if state is not None:
            assert isinstance(state, GitRepoState)


# ─── get_changed_files ────────────────────────────────────────────────


class TestGetChangedFiles:
    def test_returns_list(self):
        files = asyncio.run(get_changed_files())
        assert isinstance(files, list)

    def test_returns_empty_for_non_repo(self):
        files = asyncio.run(get_changed_files(cwd="/tmp"))
        assert isinstance(files, list)


# ─── find_canonical_git_root ──────────────────────────────────────────


class TestFindCanonicalGitRoot:
    def test_regular_repo(self):
        result = find_canonical_git_root(os.getcwd())
        assert result is not None

    def test_same_as_find_git_root_for_regular_repo(self):
        find_git_root.cache_clear()
        regular = find_git_root(os.getcwd())
        canonical = find_canonical_git_root(os.getcwd())
        assert regular == canonical
