# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pytest configuration and fixtures."""

import asyncio
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# Ensure repo root is on sys.path for monorepo imports (apps.counselconduit.*)
_repo_root = str(Path(__file__).resolve().parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


# Test Database Configuration
# Use in-memory SQLite for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"


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


@pytest.fixture
def mock_shadowtag_verifier(mocker):
    """Mock ShadowTag verifier.

    Returns mock for cryptographic signing.
    """
    mock = mocker.Mock()

    mock.sign.return_value = {
        "signature": "test_signature_base64_encoded",
        "id": "test_verification_chain_id",
        "timestamp": "2024-01-01T00:00:00Z",
    }

    mock.verify.return_value = True

    return mock


# Test Data Factories


@pytest.fixture
def sample_image_file(tmp_path):
    """
    Create sample image file for upload tests

    Returns:
        Path to temporary test image
    """

    from PIL import Image

    # Create simple test image
    img = Image.new("RGB", (100, 100), color="red")
    img_path = tmp_path / "test_image.jpg"
    img.save(img_path)

    return img_path


@pytest.fixture
def sample_video_file(tmp_path):
    """
    Create sample video file for upload tests

    Returns:
        Path to temporary test video
    """
    # Create minimal test video file
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(b"fake video data for testing")

    return video_path
