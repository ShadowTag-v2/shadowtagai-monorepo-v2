"""conftest.py — Force-resolve 'main' to the service-local main.py.

Pytest with --import-mode=importlib and pythonpath=. at the monorepo root
causes `import main` to resolve to src/main.py instead of the local main.py.
This conftest removes the stale module and forces the correct import.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_service_dir = str(Path(__file__).parent)

# Ensure the service directory is at the front of sys.path
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

# Evict any previously cached 'main' module that isn't ours
if "main" in sys.modules:
    existing = getattr(sys.modules["main"], "__file__", "")
    if existing and not str(existing).startswith(_service_dir):
        del sys.modules["main"]

# Force re-import from the correct location
import main as _local_main  # noqa: E402, F811

if not hasattr(_local_main, "_event_counts"):
    # The wrong module was loaded; force reimport
    if "main" in sys.modules:
        del sys.modules["main"]
    spec = importlib.util.spec_from_file_location("main", Path(_service_dir) / "main.py")
    _local_main = importlib.util.module_from_spec(spec)
    sys.modules["main"] = _local_main
    spec.loader.exec_module(_local_main)
