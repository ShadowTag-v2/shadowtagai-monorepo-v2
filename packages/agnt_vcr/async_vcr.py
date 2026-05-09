# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Async VCR Record/Replay with automated cassette rotation.

Extends the base VCRReplay with:
1. Async-native intercept (await execute_fn)
2. Automated cassette rotation — stale cassettes older than
   max_age_s are auto-purged to prevent test drift.
3. Cassette index for O(1) cache hit lookups.

Safe Harbor constraint: cassettes are local-only disk files.
No network replay, no remote cassette stores.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import time
from typing import Any

from .vcr import VCRReplay

logger = logging.getLogger(__name__)

_DEFAULT_MAX_AGE_S = 86400 * 7  # 7 days


class AsyncVCR(VCRReplay):
    """Async-capable VCR with automatic cassette rotation.

    Adds async intercept support and time-based cassette expiry.
    Expired cassettes are re-recorded on next use (lazy rotation).
    """

    __slots__ = ("_max_age_s", "_index_path", "_index", "_lock")

    def __init__(
        self,
        cassette_dir: str = ".cassettes",
        max_age_s: float = _DEFAULT_MAX_AGE_S,
    ) -> None:
        super().__init__(cassette_dir=cassette_dir)
        self._max_age_s = max_age_s
        self._index_path = os.path.join(self.cassette_dir, "_index.json")
        self._index: dict[str, float] = self._load_index()
        self._lock = asyncio.Lock()

    def _load_index(self) -> dict[str, float]:
        """Load the cassette timestamp index from disk."""
        if os.path.exists(self._index_path):
            try:
                with open(self._index_path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError, OSError:
                logger.warning("Corrupt cassette index, rebuilding")
        return {}

    def _save_index(self) -> None:
        """Persist the cassette timestamp index to disk."""
        try:
            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(self._index, f, indent=2)
        except OSError as exc:
            logger.warning("Failed to save cassette index: %s", exc)

    def _is_stale(self, req_hash: str) -> bool:
        """Check if a cassette has exceeded max_age_s."""
        recorded_at = self._index.get(req_hash, 0.0)
        if recorded_at == 0.0:
            return True
        return (time.time() - recorded_at) > self._max_age_s

    async def async_intercept(
        self,
        method: str,
        kwargs: dict[str, Any],
        execute_fn: Any,
    ) -> Any:
        """Async-aware intercept with automatic cassette rotation.

        Args:
            method: Tool/API method name.
            kwargs: Request parameters.
            execute_fn: Async callable to execute if no valid cassette.

        Returns:
            Response from cassette (replay) or live execution (record).
        """
        sanitized_kwargs = self._sanitize_secrets(kwargs)
        req_hash = self._hash_request(method, sanitized_kwargs)
        cassette_path = self._get_cassette_path(req_hash)

        async with self._lock:
            # Replay path — check for valid, non-stale cassette
            if self.replaying and os.path.exists(cassette_path) and not self._is_stale(req_hash):
                with open(cassette_path, encoding="utf-8") as f:
                    data = json.load(f)
                logger.debug("VCR replay hit: %s (%s)", method, req_hash[:12])
                return data["response"]

            # Execute live
            if inspect.iscoroutinefunction(execute_fn):
                response = await execute_fn()
            else:
                response = execute_fn()

            # Record path — write cassette and update index
            if self.recording:
                cassette = {
                    "request": {"method": method, "kwargs": sanitized_kwargs},
                    "response": response,
                    "recorded_at": time.time(),
                }
                with open(cassette_path, "w", encoding="utf-8") as f:
                    json.dump(cassette, f, indent=2)
                self._index[req_hash] = time.time()
                self._save_index()
                logger.debug("VCR recorded: %s (%s)", method, req_hash[:12])

            return response

    def rotate_stale(self) -> int:
        """Purge all stale cassettes beyond max_age_s.

        Returns the count of rotated cassettes.
        """
        rotated = 0
        stale_hashes = [h for h in self._index if self._is_stale(h)]

        for req_hash in stale_hashes:
            cassette_path = self._get_cassette_path(req_hash)
            if os.path.exists(cassette_path):
                try:
                    os.unlink(cassette_path)
                    rotated += 1
                except OSError:
                    pass
            self._index.pop(req_hash, None)

        if rotated > 0:
            self._save_index()
            logger.info("VCR rotated %d stale cassette(s)", rotated)
        return rotated

    def cassette_count(self) -> int:
        """Return the number of active cassettes."""
        return len(self._index)

    def cassette_stats(self) -> dict[str, Any]:
        """Return cassette health statistics."""
        now = time.time()
        ages = [now - ts for ts in self._index.values()]
        total = len(ages)
        stale = sum(1 for a in ages if a > self._max_age_s)
        return {
            "total_cassettes": total,
            "stale_cassettes": stale,
            "fresh_cassettes": total - stale,
            "max_age_s": self._max_age_s,
            "oldest_age_s": max(ages) if ages else 0.0,
        }
