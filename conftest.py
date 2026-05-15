# conftest.py — Root-level pytest configuration
# Ensures monorepo-root is on sys.path for imports like:
#   from apps.counselconduit.module import symbol
#   from gates.tengu_j6_bridge import enforce_zta_handoff
"""Root conftest.py for UphillSnowball Monorepo test suite.

Uses pytest_configure hook to inject paths AND pre-register src/
packages in sys.modules BEFORE importlib-mode collection begins.

Without pre-registration, tests/unit/gates/__init__.py creates a
'gates' package from the test tree, shadowing src/gates/. Pre-importing
from src/ pins the correct modules first.

Ref: pytest 9.x --import-mode=importlib namespace collision fix.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"

# Packages under src/ that share names with test directories.
# These MUST be pre-registered to prevent test-tree shadowing.
_SRC_PACKAGES_TO_PIN = [
  "governance",  # dep of gates.tengu_j6_bridge — load first
  "gates",
]


def pytest_configure(config):  # noqa: ARG001
  """Inject repo root and src/ into sys.path before collection.

  Also pre-import src/ packages that collide with test directory names
  (e.g. src/gates vs tests/unit/gates) so that sys.modules pins the
  correct module BEFORE pytest's assertion rewriter or importlib-mode
  collector can shadow them.
  """
  root_str = str(_ROOT)
  src_str = str(_SRC)
  if root_str not in sys.path:
    sys.path.insert(0, root_str)
  if src_str not in sys.path:
    sys.path.insert(0, src_str)

  # Pre-register src packages to prevent namespace collision
  for pkg_name in _SRC_PACKAGES_TO_PIN:
    if pkg_name not in sys.modules:
      try:
        importlib.import_module(pkg_name)
      except ImportError:
        pass  # Package may not exist yet — fail gracefully
