# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Conftest for deprecated test archive.

Tests in this directory are superseded by their v2 equivalents in tests/.
They are excluded from collection to prevent import errors from legacy
module paths (e.g. packages.agnt_tools.speculation_engine).

Active replacement: tests/test_speculation_engine_v2.py
"""

collect_ignore_glob = ["test_*.py"]
