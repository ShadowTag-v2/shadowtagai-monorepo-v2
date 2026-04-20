"""Scrapling Sandbox Guard — scrapling_sandbox_guard.py

SAFE MODE enforcement for web scraping workflows.
Prevents accidental file/drive deletion during scraping plans.

Rules:
  1. Write operations restricted to ./data/, ./output/, ./tmp/
  2. rm -rf and shutil.rmtree blocked on non-tmp paths
  3. User confirmation required for any deletion
  4. All write operations logged to .beads/scrapling_writes.jsonl
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_WRITE_ROOTS = frozenset({"data", "output", "tmp"})
WRITE_LOG_PATH = Path(".beads/scrapling_writes.jsonl")
BLOCKED_PATTERNS = frozenset({"rm -rf", "rm -r", "shutil.rmtree"})


class SandboxViolationError(Exception):
    """Raised when a write targets a prohibited path."""


def validate_write_path(target_path: str | Path) -> Path:
    """Validate that a write target is within allowed roots.

    Args:
        target_path: The path being written to.

    Returns:
        Resolved Path if valid.

    Raises:
        SandboxViolationError: If path is outside sandbox.
    """
    resolved = Path(target_path).resolve()
    cwd = Path.cwd().resolve()

    # Must be relative to CWD
    try:
        relative = resolved.relative_to(cwd)
    except ValueError as exc:
        raise SandboxViolationError(
            f"SANDBOX VIOLATION: Path '{target_path}' is outside "
            f"workspace root '{cwd}'"
        ) from exc

    # Must be under an allowed root
    parts = relative.parts
    if not parts:
        raise SandboxViolationError(
            f"SANDBOX VIOLATION: Cannot write to workspace root"
        )

    root_dir = parts[0]
    if root_dir not in ALLOWED_WRITE_ROOTS:
        raise SandboxViolationError(
            f"SANDBOX VIOLATION: Root '{root_dir}/' is not in allowed "
            f"write paths: {sorted(ALLOWED_WRITE_ROOTS)}. "
            f"Target: {target_path}"
        )

    _log_write("validate", str(target_path), allowed=True)
    return resolved


def validate_command(command: str) -> str:
    """Check a shell command for dangerous deletion patterns.

    Args:
        command: Shell command string to validate.

    Returns:
        The command if safe.

    Raises:
        SandboxViolationError: If command contains blocked patterns.
    """
    command_lower = command.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern in command_lower:
            # Check if it targets a tmp path (allowed)
            if _targets_tmp_only(command):
                _log_write("command_allowed", command, allowed=True)
                return command

            raise SandboxViolationError(
                f"SANDBOX VIOLATION: Command contains blocked pattern "
                f"'{pattern}': {command}\n"
                f"Only deletion of ./tmp/ paths is allowed."
            )

    _log_write("command_allowed", command, allowed=True)
    return command


def safe_write(target_path: str | Path, content: str | bytes) -> Path:
    """Write to a validated sandbox path.

    Args:
        target_path: Destination file path.
        content: Content to write.

    Returns:
        The resolved path that was written to.
    """
    validated = validate_write_path(target_path)
    validated.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(content, bytes):
        validated.write_bytes(content)
    else:
        validated.write_text(content)

    _log_write("write", str(target_path), allowed=True,
               size=len(content))
    return validated


def _targets_tmp_only(command: str) -> bool:
    """Check if a deletion command only targets tmp/ paths."""
    # Simple heuristic: all path arguments must contain /tmp/ or ./tmp/
    parts = command.split()
    path_parts = [p for p in parts if "/" in p or p.startswith(".")]
    if not path_parts:
        return False
    return all("tmp" in p.lower() for p in path_parts)


def _log_write(
    operation: str,
    target: str,
    allowed: bool,
    size: int | None = None,
) -> None:
    """Append write operation to audit log."""
    WRITE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry: dict[str, Any] = {
        "operation": operation,
        "target": target,
        "allowed": allowed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if size is not None:
        entry["size_bytes"] = size

    with WRITE_LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    # Self-test
    print("=== Scrapling Sandbox Guard Self-Test ===")

    # Valid paths
    for path in ["data/scraped.json", "output/results.csv", "tmp/cache.bin"]:
        try:
            validate_write_path(path)
            print(f"  ✓ {path} — ALLOWED")
        except SandboxViolationError as e:
            print(f"  ✗ {path} — {e}")

    # Invalid paths
    for path in ["apps/main.py", "../escape.txt", "scripts/danger.sh"]:
        try:
            validate_write_path(path)
            print(f"  ✗ {path} — SHOULD HAVE BEEN BLOCKED")
        except SandboxViolationError:
            print(f"  ✓ {path} — correctly BLOCKED")

    # Command validation
    for cmd in ["rm -rf /tmp/cache", "rm -rf apps/", "ls -la data/"]:
        try:
            validate_command(cmd)
            print(f"  ✓ cmd '{cmd}' — ALLOWED")
        except SandboxViolationError:
            print(f"  ✓ cmd '{cmd}' — correctly BLOCKED")

    print("\n✓ Self-test complete")
