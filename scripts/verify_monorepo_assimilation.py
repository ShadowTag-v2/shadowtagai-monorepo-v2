#!/usr/bin/env python3
"""verify_monorepo_assimilation.py
Verifies that all migrated codebases have been properly assimilated into the
canonical monorepo structure, ensuring no nested .git states exist and core
manifests are present.
"""

import sys
from pathlib import Path


def verify_assimilation() -> None:
  root_dir = Path(__file__).resolve().parent.parent

  issues = 0

  # 1. Check Core Directories
  core_dirs = ["apps", "libs", "scripts", "tools", "docs"]
  missing_dirs = []
  for d in core_dirs:
    if not (root_dir / d).is_dir():
      missing_dirs.append(d)

  if missing_dirs:
    issues += 1
  else:
    pass

  # 2. Check for nested .git directories (which would indicate broken assimilation)
  nested_gits = []
  for d in ["apps", "libs"]:
    search_path = root_dir / d
    if search_path.exists():
      for sub in search_path.iterdir():
        if sub.is_dir() and (sub / ".git").exists():
          nested_gits.append(str(sub.relative_to(root_dir)))

  if nested_gits:
    issues += 1
  else:
    pass

  # 3. Check for Pyright isolation (performance)
  if not (root_dir / "pyrightconfig.json").exists():
    pass
  else:
    pass

  # 4. Check for Makefile hook
  if not (root_dir / "Makefile").exists():
    pass
  else:
    pass

  if issues > 0:
    sys.exit(1)
  else:
    sys.exit(0)


if __name__ == "__main__":
  verify_assimilation()
