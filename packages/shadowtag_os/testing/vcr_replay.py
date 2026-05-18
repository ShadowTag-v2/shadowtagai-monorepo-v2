# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""VCR Replay — Deterministic integration testing via request recording.

Records HTTP interactions during test runs and replays them for
deterministic, offline test execution. Inspired by Claude Code's
VCR record/replay and Ruby's VCR gem.

Usage:
    # Record mode — makes real HTTP calls, saves cassettes
    VCR_MODE=record pytest tests/integration/

    # Replay mode — uses saved cassettes, no network needed
    VCR_MODE=replay pytest tests/integration/

    # Passthrough — normal HTTP, no recording (default)
    pytest tests/integration/
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

CASSETTE_DIR = Path("tests/fixtures/vcr_cassettes")
VCR_MODE_ENV = "VCR_MODE"


@dataclass
class VCRInteraction:
    """A single recorded HTTP interaction.

    Attributes:
        request_method: HTTP method (GET, POST, etc.).
        request_url: Full URL of the request.
        request_headers: Request headers (sensitive ones redacted).
        request_body: Request body (if any).
        response_status: HTTP status code.
        response_headers: Response headers.
        response_body: Response body as string.
    """

    request_method: str = ""
    request_url: str = ""
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: str = ""
    response_status: int = 200
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: str = ""


@dataclass
class VCRCassette:
    """A collection of recorded HTTP interactions.

    Attributes:
        name: Cassette name (usually test function name).
        interactions: List of recorded interactions.
        record_mode: Mode used when recording ("record" or "replay").
    """

    name: str = ""
    interactions: list[VCRInteraction] = field(default_factory=list)
    record_mode: str = "passthrough"

    def save(self, directory: Path | None = None) -> Path:
        """Save cassette to disk as JSON."""
        directory = directory or CASSETTE_DIR
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.name}.json"

        data = {
            "name": self.name,
            "record_mode": self.record_mode,
            "interactions": [
                {
                    "request": {
                        "method": i.request_method,
                        "url": i.request_url,
                        "headers": i.request_headers,
                        "body": i.request_body,
                    },
                    "response": {
                        "status": i.response_status,
                        "headers": i.response_headers,
                        "body": i.response_body,
                    },
                }
                for i in self.interactions
            ],
        }

        path.write_text(json.dumps(data, indent=2, default=str))
        logger.info("VCR: saved cassette %s (%d interactions)", self.name, len(self.interactions))
        return path

    @classmethod
    def load(cls, name: str, directory: Path | None = None) -> VCRCassette:
        """Load a cassette from disk."""
        directory = directory or CASSETTE_DIR
        path = directory / f"{name}.json"

        if not path.exists():
            raise FileNotFoundError(f"VCR cassette not found: {path}")

        data = json.loads(path.read_text())
        interactions = [
            VCRInteraction(
                request_method=i["request"]["method"],
                request_url=i["request"]["url"],
                request_headers=i["request"].get("headers", {}),
                request_body=i["request"].get("body", ""),
                response_status=i["response"]["status"],
                response_headers=i["response"].get("headers", {}),
                response_body=i["response"].get("body", ""),
            )
            for i in data.get("interactions", [])
        ]

        return cls(
            name=data.get("name", name),
            interactions=interactions,
            record_mode=data.get("record_mode", "replay"),
        )


# Redacted header keys — never record these
REDACTED_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-csrf-token",
    }
)


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive headers before saving."""
    return {k: "[REDACTED]" if k.lower() in REDACTED_HEADERS else v for k, v in headers.items()}


def _request_fingerprint(method: str, url: str, body: str = "") -> str:
    """Generate a fingerprint for matching requests during replay."""
    content = f"{method}:{url}:{body}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_vcr_mode() -> str:
    """Get the current VCR mode from environment."""
    mode = os.environ.get(VCR_MODE_ENV, "passthrough").lower()
    if mode not in ("record", "replay", "passthrough"):
        logger.warning("Invalid VCR_MODE '%s', defaulting to passthrough", mode)
        return "passthrough"
    return mode


class VCRMatcher:
    """Matches incoming requests against recorded interactions."""

    def __init__(self, cassette: VCRCassette):
        self._cassette = cassette
        self._used: set[int] = set()

    def find_match(
        self,
        method: str,
        url: str,
        body: str = "",
    ) -> VCRInteraction | None:
        """Find a matching recorded interaction for the given request."""
        fingerprint = _request_fingerprint(method, url, body)

        for idx, interaction in enumerate(self._cassette.interactions):
            if idx in self._used:
                continue

            recorded_fp = _request_fingerprint(
                interaction.request_method,
                interaction.request_url,
                interaction.request_body,
            )

            if recorded_fp == fingerprint:
                self._used.add(idx)
                return interaction

        # Fallback: match by method + URL only
        for idx, interaction in enumerate(self._cassette.interactions):
            if idx in self._used:
                continue
            if interaction.request_method == method and interaction.request_url == url:
                self._used.add(idx)
                return interaction

        return None
