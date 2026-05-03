# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR Recorder — API call interception for record/replay/diff.

This module wraps Gemini API calls to enable deterministic testing.
In RECORD mode, it captures all requests and responses to cassette files.
In REPLAY mode, it returns stored responses without making live API calls.
In DIFF mode, it makes live calls AND compares against recorded responses.

Ported from: services/vcr.ts (ant-only, FORCE_VCR=1)
Reference: AGNT STATE B Spec P3.1

Environment:
    AGNT_VCR_MODE: "off" | "record" | "replay" | "diff"
    AGNT_VCR_DIR: Override cassette storage directory
"""

from __future__ import annotations

import difflib
import json
import logging
import os
import time
from enum import StrEnum
from pathlib import Path
from typing import Any
from collections.abc import Callable

from vcr.cassette import Cassette, compute_request_hash

logger = logging.getLogger(__name__)


class VCRMode(StrEnum):
    """VCR operational modes."""

    OFF = "off"
    RECORD = "record"
    REPLAY = "replay"
    DIFF = "diff"


class ReplayMiss(Exception):
    """Raised when replay mode can't find a matching cassette entry."""


class DiffMismatch:
    """Result of a diff comparison between live and recorded responses.

    Attributes:
        request_hash: Hash of the request that was compared.
        live_response: The live API response.
        recorded_response: The recorded response from cassette.
        diff_lines: Unified diff output.
        is_match: Whether responses are semantically equivalent.
    """

    def __init__(
        self,
        request_hash: str,
        live_response: dict[str, Any],
        recorded_response: dict[str, Any],
    ) -> None:
        self.request_hash = request_hash
        self.live_response = live_response
        self.recorded_response = recorded_response

        live_str = json.dumps(live_response, indent=2, sort_keys=True, default=str)
        recorded_str = json.dumps(recorded_response, indent=2, sort_keys=True, default=str)

        self.diff_lines = list(
            difflib.unified_diff(
                recorded_str.splitlines(keepends=True),
                live_str.splitlines(keepends=True),
                fromfile="recorded",
                tofile="live",
            )
        )
        self.is_match = len(self.diff_lines) == 0


class VCRRecorder:
    """Intercepts API calls for deterministic record/replay/diff.

    Usage:
        recorder = VCRRecorder(cassette_dir=Path("vcr_cassettes"))

        # Wrap API calls
        response = recorder.intercept(
            request_body={"model": "gemini-3.1-flash", "contents": [...]},
            live_call=lambda req: gemini_api.generate(req),
        )

    Args:
        cassette_dir: Directory to store cassette files.
        mode: VCR mode (off/record/replay/diff). Defaults to env var.
        cassette_name: Name for the cassette file. Defaults to "default".
    """

    def __init__(
        self,
        cassette_dir: Path | None = None,
        mode: VCRMode | None = None,
        cassette_name: str = "default",
    ) -> None:
        if mode is not None:
            self._mode = mode
        else:
            try:
                from config.feature_flags import flags

                self._mode = VCRMode(flags.get_string("vcr_mode", default="off").lower())
            except (ImportError, ModuleNotFoundError):
                self._mode = VCRMode(os.environ.get("AGNT_VCR_MODE", "off").lower())

        default_dir = Path(
            os.environ.get(
                "AGNT_VCR_DIR",
                str(cassette_dir or Path.cwd() / "vcr_cassettes"),
            )
        )
        self._cassette_dir = default_dir

        self._cassette = Cassette(self._cassette_dir / f"{cassette_name}.jsonl")

        # Load existing cassette for replay/diff modes
        if self._mode in (VCRMode.REPLAY, VCRMode.DIFF):
            self._cassette.load()
            logger.info(
                "VCR %s mode: loaded %d entries from %s",
                self._mode.value,
                len(self._cassette),
                self._cassette.path,
            )

        # Diff results accumulator
        self._diff_results: list[DiffMismatch] = []

        # Stats
        self._stats = {
            "recordings": 0,
            "replays": 0,
            "replay_misses": 0,
            "diffs_run": 0,
            "diffs_matched": 0,
            "diffs_mismatched": 0,
        }

    @property
    def mode(self) -> VCRMode:
        """Current VCR mode."""
        return self._mode

    @property
    def stats(self) -> dict[str, int]:
        """Recording/replay statistics."""
        return dict(self._stats)

    @property
    def diff_results(self) -> list[DiffMismatch]:
        """All diff comparison results (diff mode only)."""
        return list(self._diff_results)

    def intercept(
        self,
        request_body: dict[str, Any],
        live_call: Callable[[dict[str, Any]], dict[str, Any]],
        model: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Intercept an API call based on current VCR mode.

        Args:
            request_body: The API request payload.
            live_call: Function that makes the actual API call.
            model: Model identifier for the request.
            tags: Optional tags for cassette entry.

        Returns:
            API response (live or recorded).

        Raises:
            ReplayMiss: In replay mode when no matching entry exists.
        """
        if self._mode == VCRMode.OFF:
            return live_call(request_body)

        if self._mode == VCRMode.RECORD:
            return self._record(request_body, live_call, model, tags)

        if self._mode == VCRMode.REPLAY:
            return self._replay(request_body)

        if self._mode == VCRMode.DIFF:
            return self._diff(request_body, live_call, model, tags)

        # Unreachable, but fail safe
        return live_call(request_body)

    def _record(
        self,
        request_body: dict[str, Any],
        live_call: Callable[[dict[str, Any]], dict[str, Any]],
        model: str,
        tags: list[str] | None,
    ) -> dict[str, Any]:
        """Record a live API call to cassette."""
        start = time.time()
        response = live_call(request_body)
        latency_ms = (time.time() - start) * 1000

        self._cassette.record(
            request_body=request_body,
            response_body=response,
            model=model,
            latency_ms=latency_ms,
            tags=tags or [],
        )

        self._stats["recordings"] += 1
        logger.debug(
            "VCR recorded: hash=%s model=%s latency=%.1fms",
            compute_request_hash(request_body)[:12],
            model,
            latency_ms,
        )

        return response

    def _replay(self, request_body: dict[str, Any]) -> dict[str, Any]:
        """Replay a recorded response from cassette.

        Uses hash-based lookup first, falls back to sequential.
        """
        req_hash = compute_request_hash(request_body)

        # Try hash-based lookup
        entry = self._cassette.lookup(req_hash)
        if entry is not None:
            self._stats["replays"] += 1
            logger.debug("VCR replay hit: hash=%s", req_hash[:12])
            return entry.response_body

        # Try sequential fallback
        entry = self._cassette.next_sequential()
        if entry is not None:
            self._stats["replays"] += 1
            logger.debug(
                "VCR replay (sequential): expected=%s got=%s",
                req_hash[:12],
                entry.request_hash[:12],
            )
            return entry.response_body

        # No match
        self._stats["replay_misses"] += 1
        raise ReplayMiss(f"No cassette entry for request hash {req_hash[:12]}. Cassette has {len(self._cassette)} entries.")

    def _diff(
        self,
        request_body: dict[str, Any],
        live_call: Callable[[dict[str, Any]], dict[str, Any]],
        model: str,
        tags: list[str] | None,
    ) -> dict[str, Any]:
        """Make live call and compare against recorded response."""
        # Make the live call
        start = time.time()
        live_response = live_call(request_body)
        latency_ms = (time.time() - start) * 1000

        # Look up recorded response
        req_hash = compute_request_hash(request_body)
        recorded_entry = self._cassette.lookup(req_hash)

        self._stats["diffs_run"] += 1

        if recorded_entry is None:
            # No recorded entry — record this as new
            self._cassette.record(
                request_body=request_body,
                response_body=live_response,
                model=model,
                latency_ms=latency_ms,
                tags=tags or [],
            )
            logger.info("VCR diff: no recorded entry for %s (new recording)", req_hash[:12])
            return live_response

        # Compare
        mismatch = DiffMismatch(
            request_hash=req_hash,
            live_response=live_response,
            recorded_response=recorded_entry.response_body,
        )
        self._diff_results.append(mismatch)

        if mismatch.is_match:
            self._stats["diffs_matched"] += 1
            logger.debug("VCR diff: MATCH for %s", req_hash[:12])
        else:
            self._stats["diffs_mismatched"] += 1
            logger.warning(
                "VCR diff: MISMATCH for %s (%d diff lines)",
                req_hash[:12],
                len(mismatch.diff_lines),
            )

        return live_response

    def write_diff_report(self, output_path: Path) -> None:
        """Write a diff report to disk.

        Args:
            output_path: Path for the diff report file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "mode": self._mode.value,
            "stats": self._stats,
            "timestamp": time.time(),
            "mismatches": [],
        }

        for result in self._diff_results:
            if not result.is_match:
                report["mismatches"].append(
                    {
                        "request_hash": result.request_hash,
                        "diff": "".join(result.diff_lines),
                    }
                )

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(
            "VCR diff report: %d matches, %d mismatches → %s",
            self._stats["diffs_matched"],
            self._stats["diffs_mismatched"],
            output_path,
        )

    def close(self) -> None:
        """Finalize recording and flush stats."""
        if self._mode == VCRMode.RECORD:
            logger.info(
                "VCR session closed: %d recordings → %s",
                self._stats["recordings"],
                self._cassette.path,
            )

    def __repr__(self) -> str:
        return f"VCRRecorder(mode={self._mode.value}, cassette={self._cassette.path.name}, entries={len(self._cassette)})"
