# conftest.py — Root-level pytest configuration
# Ensures monorepo-root is on sys.path for imports like:
#   from apps.counselconduit.module import symbol
"""Root conftest.py for UphillSnowball Monorepo test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to sys.path so `apps.counselconduit.*` imports resolve
_root = str(Path(__file__).resolve().parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
