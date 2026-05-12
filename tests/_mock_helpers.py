# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Centralized mock client factories for test suites.

Provides factory functions that bypass ``__init__`` via ``__new__`` while
properly initialising all mandatory attributes.  This prevents
``AttributeError`` regressions that arise when ``__init__`` is skipped.

Factories
---------
- :func:`make_mock_interactions_client` — ``InteractionsClient``
- :func:`make_mock_deep_research_client` — ``DeepResearchClient``
- :func:`make_mock_vcr_replay` — ``VCRReplay``
"""

from __future__ import annotations

from gemini_interactions.client import InteractionsClient
from gemini_interactions.telemetry import NullTelemetry


# ---------------------------------------------------------------------------
# InteractionsClient
# ---------------------------------------------------------------------------


def make_mock_interactions_client(
    *,
    api_key: str = "test-key",
    model: str = "gemini-3-flash-preview",
) -> InteractionsClient:
    """Create a minimally-configured InteractionsClient without calling __init__.

    Properly initializes ``_telemetry`` with :class:`NullTelemetry` to avoid
    the ``AttributeError`` that arises when ``__init__`` is bypassed via
    ``__new__``.
    """
    client = InteractionsClient.__new__(InteractionsClient)
    client._api_key = api_key
    client._default_model = model
    client._telemetry = NullTelemetry()
    return client


# ---------------------------------------------------------------------------
# DeepResearchClient
# ---------------------------------------------------------------------------


def make_mock_deep_research_client(
    *,
    api_key: str = "test-key",
    agent: str = "deep-research-preview-04-2026",
) -> DeepResearchClient:
    """Create a minimally-configured DeepResearchClient without calling __init__.

    Sets ``_api_key``, ``_agent``, and ``_client`` (to ``None`` for lazy init)
    so attribute access never raises ``AttributeError``.
    """
    from gemini_deep_research.client import DeepResearchClient

    client = DeepResearchClient.__new__(DeepResearchClient)
    client._api_key = api_key
    client._agent = agent
    client._client = None
    return client


# ---------------------------------------------------------------------------
# VCRReplay
# ---------------------------------------------------------------------------


def make_mock_vcr_replay(
    *,
    cassette_dir: str = "/dev/null",
    recording: bool = False,
    replaying: bool = False,
) -> VCRReplay:
    """Create a minimally-configured VCRReplay without calling __init__.

    Bypasses filesystem operations (``os.makedirs``) and env-var parsing
    that ``__init__`` performs, while setting all three required attributes.
    """
    from agnt_vcr.vcr import VCRReplay

    vcr = VCRReplay.__new__(VCRReplay)
    vcr.cassette_dir = cassette_dir
    vcr.recording = recording
    vcr.replaying = replaying
    return vcr
