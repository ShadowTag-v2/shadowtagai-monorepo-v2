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

Critical: pytest.ini 'pythonpath = . src' adds BOTH paths to sys.path
BEFORE pytest_configure fires, so importlib.import_module('pnkln') will
find src/pnkln/ (which has no core/ subpackage) instead of ./pnkln/.
We solve this by using spec_from_file_location to load root pnkln
from its exact filesystem path.

Ref: pytest 9.x --import-mode=importlib namespace collision fix.
"""

from __future__ import annotations

import importlib
import importlib.util
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


def _pin_package_from_path(pkg_name: str, init_path: Path) -> None:
  """Force-register a package in sys.modules from an explicit init file.

  This bypasses importlib's normal path search, ensuring we load the
  package from the EXACT filesystem location we want, regardless of
  what's on sys.path.
  """
  if pkg_name in sys.modules:
    return

  spec = importlib.util.spec_from_file_location(
    pkg_name,
    str(init_path),
    submodule_search_locations=[str(init_path.parent)],
  )
  if spec is None or spec.loader is None:
    return

  mod = importlib.util.module_from_spec(spec)
  sys.modules[pkg_name] = mod  # Register BEFORE exec to handle circular refs
  try:
    spec.loader.exec_module(mod)
  except Exception:
    # If exec fails, remove the partial registration
    sys.modules.pop(pkg_name, None)


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

  # Pin root-level pnkln from explicit path BEFORE src/ can shadow it.
  # pytest.ini pythonpath adds src/ before this hook fires, so
  # importlib.import_module('pnkln') would find src/pnkln/ instead.
  _pin_package_from_path("pnkln", _ROOT / "pnkln" / "__init__.py")
  _pin_package_from_path("pnkln.core", _ROOT / "pnkln" / "core" / "__init__.py")
  _pin_package_from_path("pnkln.tools", _ROOT / "pnkln" / "tools" / "__init__.py")

  if src_str not in sys.path:
    sys.path.insert(0, src_str)

  # Pre-register src packages to prevent namespace collision
  for pkg_name in _SRC_PACKAGES_TO_PIN:
    if pkg_name not in sys.modules:
      try:
        importlib.import_module(pkg_name)
      except ImportError:
        pass  # Package may not exist yet — fail gracefully
