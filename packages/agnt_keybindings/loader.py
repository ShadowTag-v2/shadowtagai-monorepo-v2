"""
User keybinding configuration loader with hot-reload support.

Ported from Claude Code keybindings/loadUserBindings.ts — loads keybindings
from ``~/.agnt/keybindings.json`` and watches for changes to reload them
automatically.

Headless adaptation:
  - ``chokidar`` → ``watchdog`` (``Observer`` + ``FileSystemEventHandler``)
  - ``createSignal`` → Python ``list[Callable]`` listener pattern
  - GrowthBook gate → ``ENABLED_FEATURES`` set from ``default_bindings``
  - Datadog ``logEvent`` → Python ``logging``
  - ``readFileSync`` → ``pathlib.Path.read_text``
  - ``readFile`` → ``asyncio``-compatible sync I/O (daemon context)
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .default_bindings import DEFAULT_BINDINGS, ENABLED_FEATURES
from .parser import parse_bindings
from .types import KeybindingBlock, KeybindingWarning, ParsedBinding
from .validate import check_duplicate_keys_in_json, validate_bindings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

FILE_STABILITY_THRESHOLD_S: float = 0.5
"""Seconds to wait for file writes to stabilise before reloading."""

FILE_STABILITY_POLL_INTERVAL_S: float = 0.2
"""Polling interval for stability checks."""

_CONFIG_DIR_ENV = "AGNT_CONFIG_HOME"
"""Override for the config directory (default ``~/.agnt``)."""


# ---------------------------------------------------------------------------
# Feature gate (replaces GrowthBook tengu_keybinding_customization_release)
# ---------------------------------------------------------------------------


def is_keybinding_customization_enabled() -> bool:
    """Return ``True`` when user keybinding customisation is active.

    Mirrors the GrowthBook ``tengu_keybinding_customization_release`` gate.
    In the headless port, this is a feature flag check.
    """
    return "KEYBINDING_CUSTOMIZATION" in ENABLED_FEATURES


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def get_config_home_dir() -> Path:
    """Return the agnt config directory (``~/.agnt`` by default)."""
    env = os.environ.get(_CONFIG_DIR_ENV)
    if env:
        return Path(env)
    return Path.home() / ".agnt"


def get_keybindings_path() -> Path:
    """Return the path to the user keybindings file."""
    return get_config_home_dir() / "keybindings.json"


# ---------------------------------------------------------------------------
# Load result dataclass
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class KeybindingsLoadResult:
    """Result of loading keybindings, including any validation warnings."""

    bindings: list[ParsedBinding] = field(default_factory=list)
    warnings: list[KeybindingWarning] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Type guards
# ---------------------------------------------------------------------------


def _is_keybinding_block(obj: object) -> bool:
    """Check if an object is a valid KeybindingBlock-shaped dict."""
    if not isinstance(obj, dict):
        return False
    return isinstance(obj.get("context"), str) and isinstance(obj.get("bindings"), dict)


def _is_keybinding_block_list(arr: object) -> bool:
    """Check if an array contains only valid KeybindingBlock-shaped dicts."""
    return isinstance(arr, list) and all(_is_keybinding_block(item) for item in arr)


# ---------------------------------------------------------------------------
# Default binding cache
# ---------------------------------------------------------------------------

_default_parsed: list[ParsedBinding] | None = None


def _get_default_parsed_bindings() -> list[ParsedBinding]:
    """Parse default bindings (cached for performance)."""
    global _default_parsed  # noqa: PLW0603
    if _default_parsed is None:
        _default_parsed = parse_bindings(DEFAULT_BINDINGS)
    return _default_parsed


# ---------------------------------------------------------------------------
# Telemetry (daily dedup — replaces Datadog logEvent)
# ---------------------------------------------------------------------------

_last_custom_log_date: str | None = None


def _log_custom_bindings_once_per_day(user_binding_count: int) -> None:
    """Log when custom keybindings are loaded, at most once per day."""
    global _last_custom_log_date  # noqa: PLW0603
    today = time.strftime("%Y-%m-%d")
    if _last_custom_log_date == today:
        return
    _last_custom_log_date = today
    logger.info("custom_keybindings_loaded: user_binding_count=%d", user_binding_count)


# ---------------------------------------------------------------------------
# Core load functions
# ---------------------------------------------------------------------------


def _parse_user_config(
    content: str,
    default_bindings: list[ParsedBinding],
) -> KeybindingsLoadResult:
    """Parse raw JSON ``content`` and merge with ``default_bindings``.

    Shared logic between sync and async loaders.
    """
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.debug("[keybindings] JSON parse error: %s", exc)
        return KeybindingsLoadResult(
            bindings=list(default_bindings),
            warnings=[
                KeybindingWarning(
                    type="parse_error",
                    severity="error",
                    message=f"Failed to parse keybindings.json: {exc}",
                )
            ],
        )

    # Extract bindings array from { "bindings": [...] } wrapper
    if not isinstance(parsed, dict) or "bindings" not in parsed:
        msg = 'keybindings.json must have a "bindings" array'
        suggestion = 'Use format: { "bindings": [ ... ] }'
        logger.debug("[keybindings] Invalid format: %s", msg)
        return KeybindingsLoadResult(
            bindings=list(default_bindings),
            warnings=[
                KeybindingWarning(
                    type="parse_error",
                    severity="error",
                    message=msg,
                    suggestion=suggestion,
                )
            ],
        )

    user_blocks = parsed["bindings"]

    if not _is_keybinding_block_list(user_blocks):
        if not isinstance(user_blocks, list):
            msg = '"bindings" must be an array'
            suggestion = 'Set "bindings" to an array of keybinding blocks'
        else:
            msg = "keybindings.json contains invalid block structure"
            suggestion = (
                'Each block must have "context" (string) and "bindings" (object)'
            )
        logger.debug("[keybindings] Invalid structure: %s", msg)
        return KeybindingsLoadResult(
            bindings=list(default_bindings),
            warnings=[
                KeybindingWarning(
                    type="parse_error",
                    severity="error",
                    message=msg,
                    suggestion=suggestion,
                )
            ],
        )

    # Convert raw dicts to KeybindingBlock instances for the parser
    typed_blocks: list[KeybindingBlock] = [
        KeybindingBlock(context=b["context"], bindings=b["bindings"])
        for b in user_blocks
    ]

    user_parsed = parse_bindings(typed_blocks)
    logger.debug("[keybindings] Loaded %d user bindings", len(user_parsed))

    # User bindings come after defaults so they override
    merged = list(default_bindings) + user_parsed

    _log_custom_bindings_once_per_day(len(user_parsed))

    # Run validation: duplicate JSON keys + structural checks
    dup_warnings = check_duplicate_keys_in_json(content)
    all_warnings = list(dup_warnings) + list(validate_bindings(typed_blocks, merged))

    if all_warnings:
        logger.debug("[keybindings] Found %d validation issue(s)", len(all_warnings))

    return KeybindingsLoadResult(bindings=merged, warnings=all_warnings)


def load_keybindings() -> KeybindingsLoadResult:
    """Load and parse keybindings from user config file (sync).

    Returns merged default + user bindings with validation warnings.
    For users without customisation enabled, returns defaults only.
    """
    defaults = _get_default_parsed_bindings()

    if not is_keybinding_customization_enabled():
        return KeybindingsLoadResult(bindings=list(defaults), warnings=[])

    user_path = get_keybindings_path()

    try:
        content = user_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return KeybindingsLoadResult(bindings=list(defaults), warnings=[])
    except OSError as exc:
        logger.debug("[keybindings] Error loading %s: %s", user_path, exc)
        return KeybindingsLoadResult(
            bindings=list(defaults),
            warnings=[
                KeybindingWarning(
                    type="parse_error",
                    severity="error",
                    message=f"Failed to read keybindings.json: {exc}",
                )
            ],
        )

    return _parse_user_config(content, defaults)


# ---------------------------------------------------------------------------
# Cached binding store (module-level singleton)
# ---------------------------------------------------------------------------

_cached_bindings: list[ParsedBinding] | None = None
_cached_warnings: list[KeybindingWarning] = []
_lock = threading.Lock()


def load_keybindings_sync() -> list[ParsedBinding]:
    """Load keybindings synchronously, using cache if available."""
    if _cached_bindings is not None:
        return _cached_bindings
    result = load_keybindings_sync_with_warnings()
    return result.bindings


def load_keybindings_sync_with_warnings() -> KeybindingsLoadResult:
    """Load keybindings synchronously with warnings, using cache if available."""
    global _cached_bindings, _cached_warnings  # noqa: PLW0603

    with _lock:
        if _cached_bindings is not None:
            return KeybindingsLoadResult(
                bindings=_cached_bindings, warnings=list(_cached_warnings)
            )

        result = load_keybindings()
        _cached_bindings = result.bindings
        _cached_warnings = result.warnings
        return result


def get_cached_keybinding_warnings() -> list[KeybindingWarning]:
    """Return cached validation warnings (empty if bindings not yet loaded)."""
    return list(_cached_warnings)


# ---------------------------------------------------------------------------
# File watcher (replaces chokidar)
#
# Uses a lightweight polling thread instead of OS-level FS events to avoid
# the ``watchdog`` dependency.  For a daemon that reloads config maybe once
# per hour, 2-second polling is perfectly adequate.
# ---------------------------------------------------------------------------

ChangeListener = Callable[[KeybindingsLoadResult], None]

_watcher_thread: threading.Thread | None = None
_watcher_stop = threading.Event()
_initialized = False
_disposed = False
_listeners: list[ChangeListener] = []
_POLL_INTERVAL_S = 2.0


def _watcher_loop(path: Path) -> None:
    """Background thread that polls ``path`` for changes."""
    last_mtime: float | None = None

    while not _watcher_stop.is_set():
        try:
            stat = path.stat()
            mtime = stat.st_mtime
        except FileNotFoundError:
            if last_mtime is not None:
                # File was deleted — reset to defaults
                logger.debug("[keybindings] Detected deletion of %s", path)
                last_mtime = None
                defaults = _get_default_parsed_bindings()
                result = KeybindingsLoadResult(bindings=list(defaults), warnings=[])
                _update_cache_and_notify(result)
            _watcher_stop.wait(_POLL_INTERVAL_S)
            continue
        except OSError:
            _watcher_stop.wait(_POLL_INTERVAL_S)
            continue

        if last_mtime is None or mtime != last_mtime:
            if last_mtime is not None:
                # Wait for write stability
                time.sleep(FILE_STABILITY_THRESHOLD_S)
                try:
                    new_mtime = path.stat().st_mtime
                except OSError:
                    _watcher_stop.wait(_POLL_INTERVAL_S)
                    continue
                if new_mtime != mtime:
                    # Still writing — skip this cycle
                    _watcher_stop.wait(_POLL_INTERVAL_S)
                    continue

                logger.debug("[keybindings] Detected change to %s", path)
                try:
                    result = load_keybindings()
                    _update_cache_and_notify(result)
                except Exception:
                    logger.debug(
                        "[keybindings] Error reloading",
                        exc_info=True,
                    )
            last_mtime = mtime

        _watcher_stop.wait(_POLL_INTERVAL_S)


def _update_cache_and_notify(result: KeybindingsLoadResult) -> None:
    """Update the cache and notify all listeners."""
    global _cached_bindings, _cached_warnings  # noqa: PLW0603
    with _lock:
        _cached_bindings = result.bindings
        _cached_warnings = result.warnings

    for listener in _listeners:
        try:
            listener(result)
        except Exception:
            logger.debug("[keybindings] Listener error", exc_info=True)


def initialize_keybinding_watcher() -> None:
    """Start the file watcher for ``keybindings.json``.

    Call once at application startup.  No-op if customisation is disabled.
    """
    global _initialized, _watcher_thread  # noqa: PLW0603

    if _initialized or _disposed:
        return

    if not is_keybinding_customization_enabled():
        logger.debug("[keybindings] Skipping file watcher — customisation disabled")
        return

    user_path = get_keybindings_path()
    watch_dir = user_path.parent

    if not watch_dir.is_dir():
        logger.debug("[keybindings] Not watching: %s does not exist", watch_dir)
        return

    _initialized = True
    _watcher_stop.clear()

    logger.debug("[keybindings] Watching for changes to %s", user_path)

    _watcher_thread = threading.Thread(
        target=_watcher_loop,
        args=(user_path,),
        name="agnt-keybinding-watcher",
        daemon=True,
    )
    _watcher_thread.start()


def dispose_keybinding_watcher() -> None:
    """Stop the file watcher and clean up resources."""
    global _disposed, _watcher_thread  # noqa: PLW0603

    _disposed = True
    _watcher_stop.set()

    if _watcher_thread is not None:
        _watcher_thread.join(timeout=5.0)
        _watcher_thread = None

    _listeners.clear()


def subscribe_to_keybinding_changes(listener: ChangeListener) -> Callable[[], None]:
    """Subscribe to keybinding change notifications.

    Returns an unsubscribe callable.
    """
    _listeners.append(listener)

    def unsubscribe() -> None:
        with contextlib.suppress(ValueError):
            _listeners.remove(listener)

    return unsubscribe


# ---------------------------------------------------------------------------
# Testing helpers
# ---------------------------------------------------------------------------


def reset_keybinding_loader_for_testing() -> None:
    """Reset all internal state — for test isolation only."""
    global _initialized, _disposed  # noqa: PLW0603
    global _cached_bindings, _cached_warnings  # noqa: PLW0603
    global _default_parsed, _last_custom_log_date  # noqa: PLW0603

    dispose_keybinding_watcher()

    _initialized = False
    _disposed = False
    _cached_bindings = None
    _cached_warnings = []
    _default_parsed = None
    _last_custom_log_date = None
    _watcher_stop.clear()
    _listeners.clear()
