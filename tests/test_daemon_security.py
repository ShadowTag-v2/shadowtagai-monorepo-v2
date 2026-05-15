"""Tests for ReadOnlyBashGuard and DreamLockFile security components.

Covers:
  - ReadOnlyBashGuard: blocks all 14 destructive command patterns
  - ReadOnlyBashGuard: allows safe commands (ruff, git status, etc.)
  - ReadOnlyBashGuard: context manager lifecycle (engage/disengage)
  - DreamLockFile: acquire/release lifecycle
  - DreamLockFile: stale lock detection and breaking
  - DreamLockFile: dead PID orphan cleanup
  - DreamLockFile: concurrent acquisition rejection
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

# Import the components under test
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from dream_consolidation import (
  DestructiveCommandError,
  DreamLockFile,
  ReadOnlyBashGuard,
  _validate_command,
)


# ---------------------------------------------------------------------------
# ReadOnlyBashGuard Tests
# ---------------------------------------------------------------------------


class TestValidateCommand:
  """Test the _validate_command function directly."""

  @pytest.mark.parametrize(
    "cmd",
    [
      "rm -rf /tmp/test",
      "rm file.txt",
      "unlink /path/to/file",
      "sed -i 's/old/new/' file.txt",
      "mv file1 file2",
      "chmod 777 file",
      "chown root file",
      "truncate -s 0 file",
      "shred secret.txt",
      "dd if=/dev/zero of=file",
      "> /etc/passwd",
      "> ../../../etc/shadow",
      "git reset --hard HEAD",
      "git clean -fd",
      "sudo anything",
    ],
  )
  def test_blocks_destructive_commands(self, cmd: str) -> None:
    """Each of the 14+ destructive patterns must raise."""
    with pytest.raises(DestructiveCommandError):
      _validate_command(cmd)

  @pytest.mark.parametrize(
    "cmd",
    [
      "ruff check .",
      "ruff format --check .",
      "git status --porcelain",
      "git log -n 5",
      "git fetch --prune origin",
      "python -m pytest tests/",
      "ast-grep scan --rule '{}' .",
      "cat README.md",
      "ls -la",
      "echo hello world",
      "grep -r 'pattern' src/",
      "wc -l file.txt",
    ],
  )
  def test_allows_safe_commands(self, cmd: str) -> None:
    """Safe commands must not raise."""
    _validate_command(cmd)  # Should not raise

  def test_accepts_list_format(self) -> None:
    """Commands can be passed as list[str] too."""
    _validate_command(["ruff", "check", "."])  # Safe — no raise
    with pytest.raises(DestructiveCommandError):
      _validate_command(["rm", "-rf", "/"])


class TestReadOnlyBashGuard:
  """Test the context manager behavior."""

  def test_engage_disengage_lifecycle(self) -> None:
    """Guard must restore subprocess.run after exiting."""
    original_run = subprocess.run
    with ReadOnlyBashGuard():
      assert subprocess.run is not original_run, "run should be patched inside guard"
    assert subprocess.run is original_run, "run should be restored after guard"

  def test_blocks_destructive_inside_guard(self) -> None:
    """Destructive commands raise inside the guard."""
    with ReadOnlyBashGuard(), pytest.raises(DestructiveCommandError):
      subprocess.run(["rm", "-rf", "/tmp/test"])

  def test_allows_safe_inside_guard(self) -> None:
    """Safe commands pass through to real subprocess.run inside the guard."""
    with ReadOnlyBashGuard():
      result = subprocess.run(
        ["echo", "hello"],
        capture_output=True,
        text=True,
      )
      assert result.returncode == 0
      assert "hello" in result.stdout

  def test_restores_after_exception(self) -> None:
    """Even if an exception occurs, subprocess.run must be restored."""
    original_run = subprocess.run
    try:
      with ReadOnlyBashGuard():
        raise ValueError("test exception")
    except ValueError:
      pass
    assert subprocess.run is original_run


# ---------------------------------------------------------------------------
# DreamLockFile Tests
# ---------------------------------------------------------------------------


class TestDreamLockFile:
  """Test the PID-based lock file mechanism."""

  def test_acquire_and_release(self, tmp_path: Path) -> None:
    """Basic acquire/release cycle."""
    lock_path = tmp_path / "test.lock"
    lock = DreamLockFile(lock_path=lock_path)

    assert lock.acquire() is True
    assert lock_path.exists()

    # Verify lock content
    data = json.loads(lock_path.read_text())
    assert data["pid"] == os.getpid()
    assert "acquired_at" in data
    assert "hostname" in data

    lock.release()
    assert not lock_path.exists()

  def test_rejects_concurrent_acquisition(self, tmp_path: Path) -> None:
    """Second acquire must fail when lock is held by current PID."""
    lock_path = tmp_path / "test.lock"
    lock1 = DreamLockFile(lock_path=lock_path)
    lock2 = DreamLockFile(lock_path=lock_path)

    assert lock1.acquire() is True
    assert lock2.acquire() is False  # Should fail — held by us (same PID, not stale)

    lock1.release()

  def test_breaks_dead_pid_lock(self, tmp_path: Path) -> None:
    """Lock held by a dead PID should be auto-broken."""
    lock_path = tmp_path / "test.lock"

    # Write a lock with a definitely-dead PID
    dead_pid = 99999999
    lock_data = {
      "pid": dead_pid,
      "acquired_at": "2026-01-01T00:00:00+00:00",
      "hostname": "test-host",
    }
    lock_path.write_text(json.dumps(lock_data))

    # New lock should break the orphaned lock
    lock = DreamLockFile(lock_path=lock_path)
    assert lock.acquire() is True

    # Verify it's now our lock
    new_data = json.loads(lock_path.read_text())
    assert new_data["pid"] == os.getpid()

    lock.release()

  def test_breaks_stale_lock(self, tmp_path: Path) -> None:
    """Lock older than STALE_THRESHOLD_SECONDS should be broken even if PID is alive."""
    lock_path = tmp_path / "test.lock"

    # Write a lock with our own PID but very old timestamp
    stale_data = {
      "pid": os.getpid(),
      "acquired_at": "2020-01-01T00:00:00+00:00",
      "hostname": "test-host",
    }
    lock_path.write_text(json.dumps(stale_data))

    lock = DreamLockFile(lock_path=lock_path)
    assert lock.acquire() is True  # Should break the stale lock

    lock.release()

  def test_handles_corrupt_lock_file(self, tmp_path: Path) -> None:
    """Corrupt lock file should be silently replaced."""
    lock_path = tmp_path / "test.lock"
    lock_path.write_text("THIS IS NOT JSON")

    lock = DreamLockFile(lock_path=lock_path)
    assert lock.acquire() is True

    # Verify valid JSON now
    data = json.loads(lock_path.read_text())
    assert data["pid"] == os.getpid()

    lock.release()

  def test_creates_parent_directories(self, tmp_path: Path) -> None:
    """Lock file parent directories should be created automatically."""
    lock_path = tmp_path / "nested" / "deep" / "test.lock"
    lock = DreamLockFile(lock_path=lock_path)

    assert lock.acquire() is True
    assert lock_path.parent.exists()

    lock.release()

  def test_release_is_idempotent(self, tmp_path: Path) -> None:
    """Releasing a non-existent lock should not raise."""
    lock_path = tmp_path / "test.lock"
    lock = DreamLockFile(lock_path=lock_path)
    lock.release()  # No-op — file doesn't exist, should not raise

  def test_wont_release_others_lock(self, tmp_path: Path) -> None:
    """Won't release a lock held by a different PID."""
    lock_path = tmp_path / "test.lock"

    # Write a lock for a different PID
    other_data = {
      "pid": os.getpid() + 1,  # Different PID
      "acquired_at": "2026-05-01T00:00:00+00:00",
      "hostname": "test-host",
    }
    lock_path.write_text(json.dumps(other_data))

    lock = DreamLockFile(lock_path=lock_path)
    lock.release()  # Should warn and NOT delete

    assert lock_path.exists(), "Should not have deleted another process's lock"
