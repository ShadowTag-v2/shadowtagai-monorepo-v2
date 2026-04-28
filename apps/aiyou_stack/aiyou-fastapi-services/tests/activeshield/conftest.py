# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ActiveShield Medical - Local Test Configuration

This conftest overrides the global conftest to allow running
ActiveShield tests without full project configuration.
"""

import asyncio
from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
