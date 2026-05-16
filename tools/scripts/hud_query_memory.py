#!/usr/bin/env python3
"""
HUD Query Memory — 10X Vibe Edition
Lightweight codebase "memory" query tool for monorepo health.
Adapted for shadowtagai-monorepo-v2 (apps/, libs/, packages/, tools/, infra/)
"""

import sys
from pathlib import Path
from typing import List, Tuple

EXCLUDE_DIRS = {
  ".git",
  "node_modules",
  "dist",
  "build",
  ".next",
  ".venv",
  "__pycache__",
  "coverage",
}


def is_excluded(path: Path) -> bool:
  return any(part in EXCLUDE_DIRS for part in path.parts)


def get_loc(file_path: Path) -> int:
  try:
    return len(file_path.read_text(encoding="utf-8", errors="ignore").splitlines())
  except Exception:
    return 0


def analyze_large_files(
  threshold: int = 800, max_results: int = 25
) -> List[Tuple[str, int]]:
  """Find files over threshold LOC and suggest modular splits."""
  large_files: List[Tuple[str, int]] = []
  search_dirs = ["apps", "libs", "packages", "tools", "infra", "services"]

  for base in search_dirs:
    base_path = Path(base)
    if not base_path.exists():
      continue
    for file_path in base_path.rglob("*"):
      if file_path.is_file() and not is_excluded(file_path):
        if file_path.suffix.lower() in {
          ".py",
          ".ts",
          ".tsx",
          ".js",
          ".jsx",
          ".go",
          ".rs",
        }:
          loc = get_loc(file_path)
          if loc > threshold:
            large_files.append((str(file_path.relative_to(Path("."))), loc))

  return sorted(large_files, key=lambda x: -x[1])[:max_results]


def count_todos() -> int:
  todos = 0
  for base in ["apps", "libs", "packages", "tools"]:
    base_path = Path(base)
    if base_path.exists():
      for file_path in base_path.rglob("*"):
        if file_path.is_file() and not is_excluded(file_path):
          if file_path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}:
            try:
              content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
              todos += content.count("todo") + content.count("fixme")
            except Exception:
              pass
  return todos


def main():
  query = " ".join(sys.argv[1:]).lower() if len(sys.argv) > 1 else "default"

  print(f"# 🧠 HUD Memory Query: `{query}`\n")
  print(
    "**Monorepo:** shadowtagai-monorepo-v2  |  **Scope:** apps/ libs/ packages/ tools/ infra/\n"
  )

  if any(
    kw in query
    for kw in ["large", "800", "loc", "monolithic", "chunk", "split", "module"]
  ):
    print("## 📏 Large Files (>800 LOC) — Modularization Candidates\n")
    large = analyze_large_files()
    if large:
      for f, loc in large:
        suggestion = (
          "Split into /components/ + /hooks/ + /utils/"
          if "tsx" in f or "jsx" in f
          else "Extract service layer + domain models"
        )
        print(f"- **{f}** — {loc} lines → *{suggestion}*")
      print(f"\n**Total candidates:** {len(large)}")
    else:
      print("✅ No files over 800 LOC found. Architecture is healthy!")

  elif "todo" in query or "fixme" in query:
    todos = count_todos()
    print(f"## 📝 TODO / FIXME Count\n\n**Total:** {todos}\n")
    if todos > 50:
      print("⚠️  High technical debt — consider a dedicated cleanup sprint.")

  elif "secret" in query or "pii" in query or "credential" in query:
    print("Run `python tools/scripts/scrub_secrets.py` for secret scan.")

  else:
    # Default health snapshot
    print("## 📊 Monorepo Health Snapshot\n")
    large = analyze_large_files(threshold=600)  # slightly lower for overview
    todos = count_todos()
    print(f"- Files >600 LOC: **{len(large)}**")
    print(f"- TODO/FIXME markers: **{todos}**")
    print("- Recommended next action: `python tools/scripts/ui_consistency_auditor.py`")

  print("\n---\n*HUD Query Memory v10X — part of 10X Vibe Coding Matrix*")
  print(
    '*Tip: Pass any natural language query, e.g. `python hud_query_memory.py "find all Python services over 500 lines"`*'
  )


if __name__ == "__main__":
  main()
