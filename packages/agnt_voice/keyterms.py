"""STT vocabulary boosting for voice_stream.

Ported from src/services/voiceKeyterms.ts

Provides domain-specific vocabulary hints (Deepgram "keywords") so the STT
engine correctly recognises coding terminology, project names, and branch
names that would otherwise be misheard.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Global keyterms ─────────────────────────────────────────────────

# Terms Deepgram consistently mangles without keyword hints.
# Note: "Claude" and "Anthropic" are already server-side base keyterms.
# Avoid terms nobody speaks aloud as-spelled (stdout → "standard out").
GLOBAL_KEYTERMS: tuple[str, ...] = (
    "MCP",
    "symlink",
    "grep",
    "regex",
    "localhost",
    "codebase",
    "TypeScript",
    "JSON",
    "OAuth",
    "webhook",
    "gRPC",
    "dotfiles",
    "subagent",
    "worktree",
)

MAX_KEYTERMS = 50

# ─── Identifier splitting ────────────────────────────────────────────

# Pre-compiled regex for camelCase/PascalCase boundary detection
_CAMEL_BOUNDARY = re.compile(r"([a-z])([A-Z])")
_SEPARATOR_SPLIT = re.compile(r"[-_./\s]+")


def split_identifier(name: str) -> list[str]:
    """Split an identifier into individual words.

    Handles camelCase, PascalCase, kebab-case, snake_case, and
    path segments. Fragments of 2 chars or fewer are discarded
    to avoid noise.

    >>> split_identifier("voiceKeyterms")
    ['voice', 'Keyterms']
    >>> split_identifier("my-cool-project")
    ['cool', 'project']
    >>> split_identifier("a_b_longword")
    ['longword']
    """
    spaced = _CAMEL_BOUNDARY.sub(r"\1 \2", name)
    parts = _SEPARATOR_SPLIT.split(spaced)
    return [w.strip() for w in parts if w.strip() and 2 < len(w.strip()) <= 20]


def _file_name_words(file_path: str) -> list[str]:
    """Extract words from a filename's stem."""
    stem = Path(file_path).stem
    return split_identifier(stem)


# ─── Git branch detection ────────────────────────────────────────────


async def _get_git_branch() -> str | None:
    """Get the current git branch name, or None if not in a repo."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0 and stdout:
            branch = stdout.decode().strip()
            return branch if branch and branch != "HEAD" else None
    except (FileNotFoundError, OSError):
        pass
    return None


def _get_git_branch_sync() -> str | None:
    """Synchronous fallback for git branch detection."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch and branch != "HEAD" else None
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    return None


# ─── Public API ──────────────────────────────────────────────────────


async def get_voice_keyterms(
    recent_files: frozenset[str] | None = None,
    *,
    project_root: str | None = None,
) -> list[str]:
    """Build a list of keyterms for the voice_stream STT endpoint.

    Combines hardcoded global coding terms with session context
    (project name, git branch, recent files) without any model calls.

    Args:
        recent_files: Set of recently accessed file paths.
        project_root: Override project root path. Falls back to CWD.

    Returns:
        Up to MAX_KEYTERMS vocabulary hints for STT boosting.
    """
    terms: set[str] = set(GLOBAL_KEYTERMS)

    # Project root basename as a single term — users say "claude CLI internal"
    # as a phrase, not isolated words.
    root = project_root or os.environ.get("AGNT_PROJECT_ROOT", "")
    if not root:
        try:
            root = os.getcwd()
        except OSError:
            root = ""
    if root:
        name = os.path.basename(root)
        if 2 < len(name) <= 50:
            terms.add(name)

    # Git branch words (e.g. "feat/voice-keyterms" → "feat", "voice", "keyterms")
    try:
        branch = await _get_git_branch()
        if branch:
            for word in split_identifier(branch):
                terms.add(word)
    except Exception:
        logger.debug("Git branch detection failed", exc_info=True)

    # Recent file names — only scan enough to fill remaining slots
    if recent_files:
        for file_path in recent_files:
            if len(terms) >= MAX_KEYTERMS:
                break
            for word in _file_name_words(file_path):
                terms.add(word)

    return list(terms)[:MAX_KEYTERMS]


def get_voice_keyterms_sync(
    recent_files: frozenset[str] | None = None,
    *,
    project_root: str | None = None,
) -> list[str]:
    """Synchronous version of get_voice_keyterms.

    Useful in contexts where an event loop is not available.
    """
    terms: set[str] = set(GLOBAL_KEYTERMS)

    root = project_root or os.environ.get("AGNT_PROJECT_ROOT", "")
    if not root:
        try:
            root = os.getcwd()
        except OSError:
            root = ""
    if root:
        name = os.path.basename(root)
        if 2 < len(name) <= 50:
            terms.add(name)

    try:
        branch = _get_git_branch_sync()
        if branch:
            for word in split_identifier(branch):
                terms.add(word)
    except Exception:
        logger.debug("Git branch detection failed", exc_info=True)

    if recent_files:
        for file_path in recent_files:
            if len(terms) >= MAX_KEYTERMS:
                break
            for word in _file_name_words(file_path):
                terms.add(word)

    return list(terms)[:MAX_KEYTERMS]
