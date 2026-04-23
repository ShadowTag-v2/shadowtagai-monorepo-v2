"""Conftest for labs/uphillsnowball/tests.

Forces the lab's ``src/`` package to take precedence over the monorepo
root ``src/`` by pre-importing the lab's ``src`` before test modules load.

This is required because ``--import-mode=importlib`` with ``pythonpath=.``
in the root ``pytest.ini`` causes Python to resolve ``src`` to the root
``src/`` package first.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Ensure labs/uphillsnowball is at the front of sys.path
_LAB_ROOT = Path(__file__).resolve().parent.parent
_lab_root_str = str(_LAB_ROOT)

# Remove the existing `src` module from cache so we can replace it
if "src" in sys.modules:
    del sys.modules["src"]
# Also remove all src.* submodules
for key in list(sys.modules.keys()):
    if key.startswith("src."):
        del sys.modules[key]

# Insert lab root at front so `src` resolves to the lab's package
if _lab_root_str in sys.path:
    sys.path.remove(_lab_root_str)
sys.path.insert(0, _lab_root_str)

# Force re-import src from the lab root
if "src" in sys.modules:
    importlib.reload(sys.modules["src"])
