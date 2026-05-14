# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pytest configuration and fixtures for shadowtag_v2 tests
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_frame():
    """Provide a sample video frame for testing"""
    # 720p RGB frame
    frame = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
    return frame


@pytest.fixture
def sample_audio():
    """Provide sample audio for testing"""
    # 1 second at 44.1kHz
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    return audio, sample_rate


@pytest.fixture
def sample_payload():
    """Provide sample payload data for testing"""
    return b"This is a test payload for steganography operations."


@pytest.fixture
def sample_receipt():
    """Provide a sample receipt for testing"""
    from shadowtag_v2.receipt_chain import Receipt
    from datetime import datetime

    return Receipt(
        operation_id="test_op_001",
        operation_type="encode",
        timestamp=datetime.utcnow().isoformat(),
        media_type="video",
        method="lsb",
        payload_hash="a" * 64,
        media_hash="b" * 64,
        metadata={"test": True},
    )
