# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add src/ to path for direct imports (gemini_ingestion_layer, judges, etc.)
# Add scripts/ for test_github_app_auth which imports scripts/utils/
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "scripts"))
sys.path.insert(0, str(_root / "src"))

import pytest
import asyncio
from collections.abc import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_decision_context():
    """Sample decision context for testing."""
    return """
    DECISION CONTEXT: Military Equipment Procurement

    Authority: Battalion Commander
    Decision: Approve $2.5M equipment purchase
    Timeline: 2024-01-15 (48 hours past authorized deadline)
    Stakeholders: Logistics consulted, Finance NOT consulted (required)
    Justification: Urgent operational need

    POTENTIAL ISSUES:
    1. Decision made 48 hours past authorized timeline (ATP 5-19-3.4)
    2. Required stakeholder (Finance) not consulted (ATP 5-19-2.8)
    3. Purchase amount exceeds Battalion Commander authority limit of $1M (ATP 5-19-1.2)
    4. Missing conflict of interest disclosure (ATP 5-19-5.1)

    CONTEXT: Equipment vendor is owned by Commander's former unit colleague.
    """


@pytest.fixture
def sample_clean_context():
    """Sample decision context with no violations."""
    return """
    DECISION CONTEXT: Routine Supply Request

    Authority: Supply Officer
    Decision: Approve $500 supply order
    Timeline: Within authorized 24-hour window
    Stakeholders: All required parties consulted
    Justification: Routine operational supply replenishment

    All ATP 5-19 requirements met.
    """
