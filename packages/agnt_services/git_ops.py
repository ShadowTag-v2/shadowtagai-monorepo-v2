# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Git Operations — Repository state inspection and security.

Ported from src/utils/git.ts (Claude Code v2.1.91, 890 lines).
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = 5 * 1024 * 1024 * 1024
MAX_FILE_COUNT = 20_000
SNIFF_BUFFER_SIZE = 64 * 1024

_BINARY_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".webp",
        ".mp3",
        ".mp4",
        ".wav",
        ".ogg",
        ".avi",
        ".mov",
        ".zip",
        ".gz",
        ".tar",
        ".bz2",
        ".7z",
        ".rar",
        ".xz",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".o",
        ".a",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".pdf",
        ".pyc",
        ".pyo",
        ".class",
        ".jar",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".bin",
        ".dat",
    }
)

_SSH_RE = re.compile(r"^git@([^:]+):(.+?)(?:\.git)?$")
_URL_RE = re.compile(r"^(?:https?|ssh)://(?:[^@]+@)?([^/]+)/(.+?)(?:\.git)?$")
_LOCALHOST_RE = re.compile(r"^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


def _git_exe() -> str:
    import shutil

    return shutil.which("git") or "git"


def _run_git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [_git_exe(), *args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return subprocess.CompletedProcess([_git_exe(), *args], 128, "", str(exc))


async def _run_git_async(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _run_git(*args, cwd=cwd))


@lru_cache(maxsize=50)
def find_git_root(start_path: str) -> str | None:
    """Walk up from start_path to find .git directory or file."""
    current = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def find_canonical_git_root(start_path: str) -> str | None:
    """Find canonical repo root, resolving through worktrees with security checks."""
    git_root = find_git_root(start_path)
    if not git_root:
        return None
    try:
        git_path = os.path.join(git_root, ".git")
        if os.path.isdir(git_path):
            return git_root
        content = Path(git_path).read_text().strip()
        if not content.startswith("gitdir:"):
            return git_root
        wt_dir = os.path.normpath(os.path.join(git_root, content[7:].strip()))
        cd_path = os.path.join(wt_dir, "commondir")
        common = os.path.normpath(os.path.join(wt_dir, Path(cd_path).read_text().strip()))
        if os.path.dirname(os.path.abspath(wt_dir)) != os.path.abspath(os.path.join(common, "worktrees")):
            return git_root
        bl = os.path.realpath(Path(os.path.join(wt_dir, "gitdir")).read_text().strip())
        if bl != os.path.join(os.path.realpath(git_root), ".git"):
            return git_root
        return os.path.dirname(common) if os.path.basename(common) == ".git" else common
    except OSError:
        return git_root


def _is_localhost(host: str) -> bool:
    h = host.split(":")[0]
    return h == "localhost" or bool(_LOCALHOST_RE.match(h))


def normalize_git_remote_url(url: str) -> str | None:
    """Normalize SSH/HTTPS/proxy URLs to host/owner/repo (lowercase)."""
    t = url.strip()
    if not t:
        return None
    m = _SSH_RE.match(t)
    if m:
        return f"{m.group(1)}/{m.group(2)}".lower()
    m = _URL_RE.match(t)
    if m:
        host, path = m.group(1), m.group(2)
        if _is_localhost(host) and path.startswith("git/"):
            pp = path[4:]
            segs = pp.split("/")
            if len(segs) >= 3 and "." in segs[0]:
                return pp.lower()
            return f"github.com/{pp}".lower()
        return f"{host}/{path}".lower()
    return None


def get_repo_remote_hash(remote_url: str) -> str | None:
    """SHA256 hash (16 chars) of normalized remote URL."""
    n = normalize_git_remote_url(remote_url)
    return hashlib.sha256(n.encode()).hexdigest()[:16] if n else None


@dataclass(frozen=True, slots=True)
class GitRepoState:
    commit_hash: str
    branch_name: str
    remote_url: str | None
    is_head_on_remote: bool
    is_clean: bool
    worktree_count: int


async def get_git_state(cwd: str | None = None) -> GitRepoState | None:
    try:
        head, branch, remote, upstream, status, wt = await asyncio.gather(
            _run_git_async("rev-parse", "HEAD", cwd=cwd),
            _run_git_async("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
            _run_git_async("remote", "get-url", "origin", cwd=cwd),
            _run_git_async("rev-parse", "@{u}", cwd=cwd),
            _run_git_async("--no-optional-locks", "status", "--porcelain", cwd=cwd),
            _run_git_async("worktree", "list", "--porcelain", cwd=cwd),
        )
        if head.returncode != 0:
            return None
        return GitRepoState(
            commit_hash=head.stdout.strip(),
            branch_name=branch.stdout.strip(),
            remote_url=remote.stdout.strip() if remote.returncode == 0 else None,
            is_head_on_remote=upstream.returncode == 0,
            is_clean=status.stdout.strip() == "",
            worktree_count=wt.stdout.count("worktree ") if wt.returncode == 0 else 1,
        )
    except Exception:
        return None


async def find_remote_base(cwd: str | None = None) -> str | None:
    r = await _run_git_async("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", cwd=cwd)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    r = await _run_git_async("remote", "show", "origin", "--", "HEAD", cwd=cwd)
    if r.returncode == 0:
        m = re.search(r"HEAD branch: (\S+)", r.stdout)
        if m:
            return f"origin/{m.group(1)}"
    for c in ("origin/main", "origin/staging", "origin/master"):
        r = await _run_git_async("rev-parse", "--verify", c, cwd=cwd)
        if r.returncode == 0:
            return c
    return None


def is_bare_git_repo(cwd: str | None = None) -> bool:
    """Security: detect bare/exploited git repos that execute hooks from cwd."""
    target = cwd or os.getcwd()
    gp = os.path.join(target, ".git")
    try:
        if os.path.isfile(gp):
            return False
        if os.path.isdir(gp) and os.path.isfile(os.path.join(gp, "HEAD")):
            return False
    except OSError:
        pass
    for name, fn in [("HEAD", os.path.isfile), ("objects", os.path.isdir), ("refs", os.path.isdir)]:
        try:
            if fn(os.path.join(target, name)):
                return True
        except OSError:
            pass
    return False


async def get_changed_files(cwd: str | None = None) -> list[str]:
    r = await _run_git_async("--no-optional-locks", "status", "--porcelain", cwd=cwd)
    if r.returncode != 0:
        return []
    return [l[3:].strip() for l in r.stdout.strip().split("\n") if l.strip()]
