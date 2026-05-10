# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR Fixture Manager — Deterministic API test recording and replay.

Ported from Claude Code v2.1.91 VCR cassette pattern (Reid Barber analysis).
Provides a zero-dependency fixture recorder that captures HTTP request/response
pairs for offline testing of LLM API integrations (Gemini, Anthropic, etc.).

Architecture:
    - Record mode:  Make real API call, serialize req+res to YAML/JSON fixture.
    - Replay mode:  Intercept API call, return recorded fixture. No live API.
    - Gate:         Activate only in test context (PYTEST_CURRENT_TEST set).
    - Scrub:        Auto-strip API keys and tokens before fixture serialization.

Reference: Claude Code v2.1.91 test infrastructure
Reference: strategic-testing/SKILL.md VCR section
Reference: vcrpy (Python), nock (TypeScript)
"""

from vcr_fixtures.manager import (
  CassetteMode,
  FixtureManager,
  RecordedInteraction,
  VCRContext,
  fixture_manager,
)

__all__ = [
  "CassetteMode",
  "FixtureManager",
  "RecordedInteraction",
  "VCRContext",
  "fixture_manager",
]
