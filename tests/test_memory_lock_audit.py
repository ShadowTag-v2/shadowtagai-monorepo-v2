# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
  module_path = Path(__file__).resolve().parents[1] / "scripts" / "memory_lock_audit.py"
  spec = importlib.util.spec_from_file_location("memory_lock_audit", module_path)
  module = importlib.util.module_from_spec(spec)
  assert spec is not None
  assert spec.loader is not None
  spec.loader.exec_module(module)
  return module


def test_iter_text_files_skips_heavy_dirs_and_large_files(tmp_path: Path) -> None:
  module = load_module()

  keep = tmp_path / "docs" / "keep.md"
  keep.parent.mkdir(parents=True)
  keep.write_text("ok\n", encoding="utf-8")

  archived = tmp_path / "archive" / "old.md"
  archived.parent.mkdir(parents=True)
  archived.write_text("archive\n", encoding="utf-8")

  reference = tmp_path / "reference" / "ref.md"
  reference.parent.mkdir(parents=True)
  reference.write_text("reference\n", encoding="utf-8")

  ignored_lib = tmp_path / "libs" / "ignored.md"
  ignored_lib.parent.mkdir(parents=True)
  ignored_lib.write_text("lib\n", encoding="utf-8")

  oversized = tmp_path / "docs" / "huge.md"
  oversized.write_text("x" * (module.MAX_TEXT_BYTES + 1), encoding="utf-8")

  found = {
    path.relative_to(tmp_path).as_posix() for path in module.iter_text_files(tmp_path)
  }

  assert "docs/keep.md" in found
  assert "archive/old.md" not in found
  assert "reference/ref.md" not in found
  assert "libs/ignored.md" not in found
  assert "docs/huge.md" not in found
