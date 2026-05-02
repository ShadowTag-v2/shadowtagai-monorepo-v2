# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sandbox Path Resolver — Secure filesystem path resolution.

Implements the Claude Code sandbox-adapter.ts path resolution semantics:
  - `/` prefix  → relative to settings/workspace root
  - `//` prefix → absolute path (filesystem root)
  - Bare paths  → relative to CWD within sandbox

Prevents:
  - Path traversal attacks (../ escape)
  - Symlink escape from sandbox boundary
  - Access to NEVER_SAFE filesystem paths

Reference: Claude Code utils/sandbox/sandbox-adapter.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# Paths that must NEVER be accessed regardless of context
NEVER_ACCESS_PATHS = frozenset(
    {
        "/etc/shadow",
        "/etc/passwd",
        "/etc/sudoers",
        "/root",
        "/proc/self",
        "/sys/kernel",
        "~/.ssh/id_rsa",
        "~/.ssh/id_ed25519",
        "~/.gnupg",
        "~/.config/configstore/firebase-tools.json",
        "~/.config/gcloud/application_default_credentials.json",
    }
)

# Sensitive directories that require elevated context
SENSITIVE_DIRS = frozenset(
    {
        ".git",
        ".agents",
        "keys",
        "secrets",
        ".env",
        "node_modules/.cache",
    }
)


@dataclass(frozen=True)
class ResolvedPath:
    """Result of path resolution.

    Attributes:
        resolved: The fully resolved absolute path.
        original: The original input path.
        is_allowed: Whether access is permitted.
        deny_reason: If not allowed, the reason.
        is_sensitive: Whether the path is in a sensitive directory.
        resolution_type: How the path was resolved (absolute/relative/workspace).
    """

    resolved: Path
    original: str
    is_allowed: bool = True
    deny_reason: str = ""
    is_sensitive: bool = False
    resolution_type: str = "relative"


class SandboxPathResolver:
    """Resolves and validates filesystem paths within a sandbox boundary.

    Args:
        workspace_root: The workspace/settings root directory.
        cwd: Current working directory within the sandbox.
        allowed_roots: Additional allowed root directories (e.g., /tmp).
    """

    def __init__(
        self,
        workspace_root: Path,
        cwd: Path | None = None,
        allowed_roots: list[Path] | None = None,
    ) -> None:
        self._workspace_root = workspace_root.resolve()
        self._cwd = (cwd or workspace_root).resolve()
        self._allowed_roots = [r.resolve() for r in (allowed_roots or [])]
        self._allowed_roots.append(self._workspace_root)

    def resolve(self, path_str: str) -> ResolvedPath:
        """Resolve a path string to an absolute path within the sandbox.

        Path semantics:
            `//path`  → absolute filesystem path
            `/path`   → relative to workspace root
            `path`    → relative to CWD

        Args:
            path_str: The path string to resolve.

        Returns:
            ResolvedPath with resolution details and access decision.
        """
        if not path_str or not path_str.strip():
            return ResolvedPath(
                resolved=self._cwd,
                original=path_str,
                is_allowed=False,
                deny_reason="Empty path",
            )

        path_str = path_str.strip()

        # Determine resolution type
        if path_str.startswith("//"):
            # Absolute filesystem path
            raw = Path(path_str[1:])  # Strip one leading slash
            resolution_type = "absolute"
        elif path_str.startswith("/"):
            # Relative to workspace root
            raw = self._workspace_root / path_str.lstrip("/")
            resolution_type = "workspace"
        else:
            # Relative to CWD
            raw = self._cwd / path_str
            resolution_type = "relative"

        # Resolve symlinks and normalize
        try:
            resolved = raw.resolve()
        except OSError, RuntimeError:
            return ResolvedPath(
                resolved=raw,
                original=path_str,
                is_allowed=False,
                deny_reason=f"Path resolution failed: {path_str}",
                resolution_type=resolution_type,
            )

        # Check NEVER_ACCESS
        resolved_str = str(resolved)
        home = str(Path.home())
        for never_path in NEVER_ACCESS_PATHS:
            expanded = never_path.replace("~", home)
            if resolved_str == expanded or resolved_str.startswith(expanded + "/"):
                return ResolvedPath(
                    resolved=resolved,
                    original=path_str,
                    is_allowed=False,
                    deny_reason=f"NEVER_ACCESS path: {never_path}",
                    resolution_type=resolution_type,
                )

        # Check path traversal (must stay within allowed roots)
        in_allowed = any(self._is_subpath(resolved, root) for root in self._allowed_roots)

        # Absolute paths get an exception if they exist and are in safe locations
        if resolution_type == "absolute" and not in_allowed:
            # Allow /tmp and /var/folders for temp files
            if resolved_str.startswith("/tmp") or resolved_str.startswith("/var/folders"):
                in_allowed = True

        if not in_allowed:
            return ResolvedPath(
                resolved=resolved,
                original=path_str,
                is_allowed=False,
                deny_reason=f"Path '{resolved}' is outside sandbox boundary",
                resolution_type=resolution_type,
            )

        # Check sensitive directories
        is_sensitive = any(sensitive in resolved.parts for sensitive in SENSITIVE_DIRS)

        return ResolvedPath(
            resolved=resolved,
            original=path_str,
            is_allowed=True,
            is_sensitive=is_sensitive,
            resolution_type=resolution_type,
        )

    @staticmethod
    def _is_subpath(child: Path, parent: Path) -> bool:
        """Check if child is under parent without following symlinks."""
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    def __repr__(self) -> str:
        return f"SandboxPathResolver(root={self._workspace_root}, cwd={self._cwd})"
