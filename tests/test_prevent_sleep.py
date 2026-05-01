"""Tests for packages.prevent_sleep — macOS sleep prevention.

Tests cover:
- Reference counting (start/stop symmetry)
- Force stop behavior
- Context manager usage
- Platform guard (non-Darwin no-op)
- Caffeinate process lifecycle
"""

from __future__ import annotations

import platform
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from packages.prevent_sleep.sleep_guard import (
    PreventSleepContext,
    _kill_caffeinate,
    _spawn_caffeinate,
    force_stop_prevent_sleep,
    get_ref_count,
    is_preventing_sleep,
    start_prevent_sleep,
    stop_prevent_sleep,
)


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset module-level state between tests."""
    force_stop_prevent_sleep()
    yield
    force_stop_prevent_sleep()


class TestRefCounting:
    """Reference counting is the core invariant."""

    def test_start_increments_ref_count(self):
        with patch("packages.prevent_sleep.sleep_guard._spawn_caffeinate"):
            with patch("packages.prevent_sleep.sleep_guard._start_restart_timer"):
                start_prevent_sleep()
                assert get_ref_count() == 1

    def test_stop_decrements_ref_count(self):
        with patch("packages.prevent_sleep.sleep_guard._spawn_caffeinate"):
            with patch("packages.prevent_sleep.sleep_guard._start_restart_timer"):
                start_prevent_sleep()
                start_prevent_sleep()
                assert get_ref_count() == 2
                stop_prevent_sleep()
                assert get_ref_count() == 1

    def test_stop_does_not_go_negative(self):
        stop_prevent_sleep()
        assert get_ref_count() == 0

    def test_force_stop_resets_to_zero(self):
        with patch("packages.prevent_sleep.sleep_guard._spawn_caffeinate"):
            with patch("packages.prevent_sleep.sleep_guard._start_restart_timer"):
                start_prevent_sleep()
                start_prevent_sleep()
                start_prevent_sleep()
                assert get_ref_count() == 3
                force_stop_prevent_sleep()
                assert get_ref_count() == 0


class TestContextManager:
    """Context manager wraps start/stop cleanly."""

    def test_context_manager_increments_and_decrements(self):
        with patch("packages.prevent_sleep.sleep_guard._spawn_caffeinate"):
            with patch("packages.prevent_sleep.sleep_guard._start_restart_timer"):
                with PreventSleepContext():
                    assert get_ref_count() == 1
                assert get_ref_count() == 0

    def test_context_manager_decrements_on_exception(self):
        with patch("packages.prevent_sleep.sleep_guard._spawn_caffeinate"):
            with patch("packages.prevent_sleep.sleep_guard._start_restart_timer"):
                with pytest.raises(ValueError):
                    with PreventSleepContext():
                        assert get_ref_count() == 1
                        raise ValueError("test")
                assert get_ref_count() == 0


class TestPlatformGuard:
    """Non-macOS platforms are no-ops."""

    @patch("packages.prevent_sleep.sleep_guard.platform.system", return_value="Linux")
    def test_spawn_noop_on_linux(self, mock_system):
        import packages.prevent_sleep.sleep_guard as mod

        mod._caffeinate_proc = None
        mod._spawn_caffeinate()
        assert mod._caffeinate_proc is None


class TestCaffeinateLifecycle:
    """Process spawn/kill behavior."""

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
    def test_spawn_creates_process(self):
        import packages.prevent_sleep.sleep_guard as mod

        mod._caffeinate_proc = None
        mod._spawn_caffeinate()
        assert mod._caffeinate_proc is not None
        assert mod._caffeinate_proc.poll() is None  # Still running
        mod._kill_caffeinate()

    def test_kill_handles_already_dead(self):
        import packages.prevent_sleep.sleep_guard as mod

        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.kill.side_effect = OSError("already dead")
        mod._caffeinate_proc = mock_proc
        mod._kill_caffeinate()  # Should not raise
        assert mod._caffeinate_proc is None

    def test_is_preventing_sleep_false_when_no_process(self):
        assert not is_preventing_sleep()
