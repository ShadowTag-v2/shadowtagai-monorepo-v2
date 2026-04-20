"""E2E test configuration — auto-applies pytest.mark.e2e to all tests in this directory."""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Automatically mark all tests in tests/e2e/ with @pytest.mark.e2e."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
