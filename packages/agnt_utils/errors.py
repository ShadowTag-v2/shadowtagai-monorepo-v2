# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""errors — structured error hierarchy and utilities.

Ported from Claude Code v2.1.91 ``errors.ts``.
Provides a standardized error taxonomy, stack-truncation for context-window
efficiency, and OS errno helpers for filesystem operations.
"""

from __future__ import annotations

import errno
import traceback
from typing import Any


# ══════════════════════════════════════════════════════════════════════════════
#  Error hierarchy
# ══════════════════════════════════════════════════════════════════════════════


class AgntError(Exception):
    """Base exception for all agnt_utils errors."""


class AbortError(AgntError):
    """Raised when an operation is cancelled via an abort signal."""


class ConfigParseError(AgntError):
    """Raised when a configuration file cannot be parsed.

    Attributes:
        file_path:      Path to the malformed config file.
        default_config: Fallback config that should be used instead.
    """

    def __init__(
        self,
        message: str,
        file_path: str,
        default_config: Any = None,
    ) -> None:
        super().__init__(message)
        self.file_path = file_path
        self.default_config = default_config


class ShellError(AgntError):
    """Raised when a shell command fails.

    Attributes:
        stdout:      Captured stdout.
        stderr:      Captured stderr.
        return_code: Process exit code.
        interrupted: True if the process was killed by a signal.
    """

    def __init__(
        self,
        stdout: str,
        stderr: str,
        return_code: int,
        interrupted: bool = False,
    ) -> None:
        super().__init__("Shell command failed")
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.interrupted = interrupted


class TelemetrySafeError(AgntError):
    """Error whose message is verified safe for telemetry (no PII/paths/code).

    Attributes:
        telemetry_message: The scrubbed message safe for external logging.
    """

    def __init__(self, message: str, telemetry_message: str | None = None) -> None:
        super().__init__(message)
        self.telemetry_message = telemetry_message or message


# ══════════════════════════════════════════════════════════════════════════════
#  Utility functions
# ══════════════════════════════════════════════════════════════════════════════


def to_error(e: Any) -> Exception:
    """Normalize an unknown value into an Exception.

    Use at catch-site boundaries when you need a proper Exception instance.
    """
    if isinstance(e, Exception):
        return e
    return Exception(str(e))


def error_message(e: Any) -> str:
    """Extract a string message from an unknown error-like value."""
    if isinstance(e, Exception):
        return str(e)
    return str(e)


def is_abort_error(e: Any) -> bool:
    """True if *e* is an AbortError or asyncio.CancelledError."""
    import asyncio

    return isinstance(e, (AbortError, asyncio.CancelledError))


def has_exact_message(e: Any, message: str) -> bool:
    """True if *e* is an Exception with exactly *message*."""
    return isinstance(e, Exception) and str(e) == message


# ── Errno helpers ─────────────────────────────────────────────────────────────

_FS_INACCESSIBLE_CODES = frozenset(
    {
        errno.ENOENT,
        errno.EACCES,
        errno.EPERM,
        # ENOTDIR: a path component is a file, not a directory
        getattr(errno, "ENOTDIR", None),
        # ELOOP: too many symlink levels
        getattr(errno, "ELOOP", None),
    }
) - {None}


def get_errno_code(e: Any) -> int | None:
    """Extract the numeric errno from an OSError, or None."""
    if isinstance(e, OSError) and isinstance(e.errno, int):
        return e.errno
    return None


def is_enoent(e: Any) -> bool:
    """True if *e* is an ENOENT (file/dir not found) OSError."""
    return get_errno_code(e) == errno.ENOENT


def is_fs_inaccessible(e: Any) -> bool:
    """True if *e* is a filesystem error for a missing/unreachable path.

    Covers ENOENT, EACCES, EPERM, ENOTDIR, and ELOOP.
    """
    code = get_errno_code(e)
    return code is not None and code in _FS_INACCESSIBLE_CODES


# ── Stack truncation ─────────────────────────────────────────────────────────


def short_error_stack(e: Any, max_frames: int = 5) -> str:
    """Return error message + top *max_frames* stack frames.

    Full traces can waste 500-2000 chars of context window on irrelevant
    internal frames.  Use this when the error flows to a model as a
    tool_result.
    """
    if not isinstance(e, BaseException):
        return str(e)

    tb = traceback.extract_tb(e.__traceback__)
    if not tb:
        return str(e)

    header = f"{type(e).__name__}: {e}"
    if len(tb) <= max_frames:
        lines = traceback.format_exception(type(e), e, e.__traceback__)
        return "".join(lines).rstrip()

    frames = tb[:max_frames]
    formatted = traceback.format_list(frames)
    return header + "\n" + "".join(formatted).rstrip()


# ── HTTP error classifier ────────────────────────────────────────────────────

# Equivalent of AxiosErrorKind; works with httpx, requests, etc.
HTTP_ERROR_AUTH = "auth"
HTTP_ERROR_TIMEOUT = "timeout"
HTTP_ERROR_NETWORK = "network"
HTTP_ERROR_HTTP = "http"
HTTP_ERROR_OTHER = "other"


def classify_http_error(
    e: Any,
) -> dict[str, Any]:
    """Classify an HTTP error into auth/timeout/network/http/other buckets.

    Works with any exception that has ``status_code`` or ``response.status_code``
    attributes (httpx, requests, etc.).
    """
    message = error_message(e)

    status: int | None = getattr(e, "status_code", None)
    if status is None:
        resp = getattr(e, "response", None)
        if resp is not None:
            status = getattr(resp, "status_code", None)

    if status is not None:
        if status in (401, 403):
            return {"kind": HTTP_ERROR_AUTH, "status": status, "message": message}
        return {"kind": HTTP_ERROR_HTTP, "status": status, "message": message}

    # Check for connection/timeout errors by name.
    exc_name = type(e).__name__.lower()
    if "timeout" in exc_name:
        return {"kind": HTTP_ERROR_TIMEOUT, "status": status, "message": message}
    if "connect" in exc_name or "dns" in exc_name:
        return {"kind": HTTP_ERROR_NETWORK, "status": status, "message": message}

    return {"kind": HTTP_ERROR_OTHER, "status": status, "message": message}
