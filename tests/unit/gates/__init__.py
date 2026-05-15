# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Test-tree gates package — namespace redirect shim.

When pytest collects tests/unit/gates/, this __init__.py can shadow
the real src/gates/ package. This shim detects the collision and forces
sys.modules['gates'] to point to the correct source package.

Without this redirect, `from gates.tengu_j6_bridge import ...` in test
files resolves to tests/unit/gates/ (which has no tengu_j6_bridge.py),
causing ModuleNotFoundError during collection.

Ref: pytest 9.x --import-mode=importlib namespace collision fix.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Detect if we are the WRONG 'gates' package (test tree, not src tree)
_this_dir = Path(__file__).resolve().parent
_src_gates = _this_dir.parent.parent.parent / "src" / "gates"

if _src_gates.is_dir() and "tengu_j6_bridge.py" not in {
  p.name for p in _this_dir.iterdir()
}:
  # We are in the test tree — redirect to src/gates
  _src_str = str(_src_gates.parent)
  if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

  # Evict this test-tree module so the real one can load
  _stale_keys = [k for k in sys.modules if k == "gates" or k.startswith("gates.")]
  for _k in _stale_keys:
    del sys.modules[_k]

  # Import the real src/gates package
  _real = importlib.import_module("gates")
  sys.modules["gates"] = _real

  # Propagate the real package's namespace into this module frame
  # so that any cached references also resolve correctly
  globals().update({k: v for k, v in _real.__dict__.items() if not k.startswith("_")})
