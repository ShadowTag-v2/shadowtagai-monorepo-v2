# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def build_code_graph(repo_root: str) -> dict[str, Any]:
  root = Path(repo_root)
  files = []
  symbols = {}
  edges = []
  for path in root.rglob("*"):
    if not path.is_file():
      continue
    if any(
      part in {".git", "build", "dist", "__pycache__", ".venv"} for part in path.parts
    ):
      continue
    if (
      path.suffix.lower() not in {".py", ".m", ".h", ".c", ".cc", ".cpp", ".md"}
      and path.name.lower() != "makefile"
    ):
      continue
    rel = str(path.relative_to(root))
    files.append(rel)
    try:
      text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
      text = ""
    syms = []
    for i, line in enumerate(text.splitlines(), start=1):
      for pat in [
        r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*[-+]\s*\([^)]*\)\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*(?:static\s+)?(?:inline\s+)?[A-Za-z_][\w\s\*]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
      ]:
        m = re.search(pat, line)
        if m:
          syms.append({"name": m.group(1), "line": i})
    symbols[rel] = syms
    for inc in re.findall(r'#include\s+"([^"]+)"', text):
      edges.append({"src": rel, "dst": inc, "type": "include"})
  return {"files": files, "symbols": symbols, "edges": edges}


def validate_reference(graph: dict[str, Any], query: str) -> dict[str, Any]:
  q = query.lower()
  file_hits = [f for f in graph.get("files", []) if q in f.lower()]
  sym_hits = []
  for rel, syms in graph.get("symbols", {}).items():
    for s in syms:
      if q in s["name"].lower():
        sym_hits.append({"rel_path": rel, "symbol": s["name"], "line": s["line"]})
  return {
    "query": query,
    "file_hits": file_hits[:20],
    "symbol_hits": sym_hits[:20],
    "validated": bool(file_hits or sym_hits),
  }
