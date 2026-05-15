# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Repo Oracle — Core workspace indexer and query engine.

Scans the monorepo structure and maintains an in-memory index of:
    - Packages (packages/*)
    - Scripts (scripts/*)
    - Skills (.agents/skills/* and global skills)
    - Apps (apps/*)
    - Libs (libs/*)
    - Tools (tools/*)
    - Manifest truth (monorepo_manifest.yaml)

This index enables fast "does X exist?" queries that prevent agents
from reinventing existing infrastructure.
"""

from __future__ import annotations

import datetime
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RepoOracle:
  """Indexes the monorepo and answers existence/pattern queries.

  Args:
      repo_root: Absolute path to the monorepo root.
  """

  def __init__(self, repo_root: Path) -> None:
    self._root = repo_root.resolve()
    self._packages: set[str] = set()
    self._scripts: set[str] = set()
    self._skills: set[str] = set()
    self._apps: set[str] = set()
    self._libs: set[str] = set()
    self._manifest: dict[str, Any] = {}
    self._indexed = False

  def index(self) -> None:
    """Scan the monorepo and build the in-memory index."""
    self._index_dir("packages", self._packages)
    self._index_dir("scripts", self._scripts, suffix_strip=True)
    self._index_dir(".agents/skills", self._skills)
    self._index_dir("apps", self._apps)
    self._index_dir("libs", self._libs)
    self._load_manifest()
    self._indexed = True
    logger.info(
      "RepoOracle indexed: %d packages, %d scripts, %d skills, %d apps, %d libs",
      len(self._packages),
      len(self._scripts),
      len(self._skills),
      len(self._apps),
      len(self._libs),
    )

  def _index_dir(
    self, relpath: str, target: set[str], suffix_strip: bool = False
  ) -> None:
    """Index immediate children of a directory."""
    dirpath = self._root / relpath
    if not dirpath.is_dir():
      return
    for child in dirpath.iterdir():
      if child.name.startswith(".") or child.name.startswith("_"):
        continue
      name = child.stem if suffix_strip else child.name
      target.add(name)

  def _load_manifest(self) -> None:
    """Load monorepo_manifest.yaml into memory."""
    manifest_path = self._root / "monorepo_manifest.yaml"
    if not manifest_path.exists():
      logger.warning("monorepo_manifest.yaml not found at %s", manifest_path)
      return

    try:
      import yaml  # type: ignore[import-untyped]

      self._manifest = yaml.safe_load(manifest_path.read_text()) or {}
    except ImportError:
      # Fallback: parse version line only
      first_line = manifest_path.read_text().split("\n", 1)[0]
      self._manifest = {"version_line": first_line}
    except Exception:
      logger.exception("Failed to load manifest")

  def _ensure_indexed(self) -> None:
    """Auto-index on first query if not yet indexed."""
    if not self._indexed:
      self.index()

  # --- Query API ---

  def has_package(self, name: str) -> bool:
    """Check if a package exists in packages/."""
    self._ensure_indexed()
    return name in self._packages

  def has_script(self, name: str) -> bool:
    """Check if a script exists in scripts/ (name without extension)."""
    self._ensure_indexed()
    return name in self._scripts

  def has_skill(self, name: str) -> bool:
    """Check if a skill exists in .agents/skills/."""
    self._ensure_indexed()
    return name in self._skills

  def has_app(self, name: str) -> bool:
    """Check if an app exists in apps/."""
    self._ensure_indexed()
    return name in self._apps

  def has_lib(self, name: str) -> bool:
    """Check if a lib exists in libs/."""
    self._ensure_indexed()
    return name in self._libs

  def grep_pattern(self, pattern: str, max_results: int = 10) -> list[str]:
    """Search for a text pattern across the repo using ripgrep.

    Returns a list of matching file paths (relative to repo root).
    """
    self._ensure_indexed()
    try:
      result = subprocess.run(
        [
          "rg",
          "--files-with-matches",
          "--max-count",
          "1",
          "--glob",
          "!external_repos/",
          "--glob",
          "!node_modules/",
          "--glob",
          "!.venv/",
          "--glob",
          "!archive/",
          "--glob",
          "!*.pyc",
          pattern,
        ],
        capture_output=True,
        text=True,
        cwd=str(self._root),
        timeout=10,
      )
      if result.returncode == 0:
        return result.stdout.strip().splitlines()[:max_results]
    except (FileNotFoundError, subprocess.TimeoutExpired):
      logger.warning("ripgrep not available or timed out")

    return []

  def get_manifest_value(self, key: str) -> Any:
    """Get a top-level value from the monorepo manifest."""
    self._ensure_indexed()
    return self._manifest.get(key)

  def summary(self) -> dict[str, int]:
    """Return a summary of the indexed workspace."""
    self._ensure_indexed()
    return {
      "packages": len(self._packages),
      "scripts": len(self._scripts),
      "skills": len(self._skills),
      "apps": len(self._apps),
      "libs": len(self._libs),
      "manifest_keys": len(self._manifest),
    }


def _log_evidence(repo_root: Path, query: str, match_count: int) -> None:
  """Append a repo.oracle.query event to the evidence flight recorder."""
  evidence_dir = repo_root / ".agent" / "evidence"
  evidence_file = evidence_dir / "index.ndjson"
  try:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    event = {
      "event": "repo.oracle.query",
      "query": query,
      "matches": match_count,
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }
    with open(evidence_file, "a") as f:
      f.write(json.dumps(event) + "\n")
  except OSError:
    logger.warning("Failed to write evidence to %s", evidence_file)


def main() -> None:
  """CLI entrypoint for scripts/repo-oracle delegation."""
  if len(sys.argv) < 2:
    print("Usage: python oracle.py <query> [--json]")
    sys.exit(1)

  query = sys.argv[1]
  json_output = "--json" in sys.argv

  repo_root = Path(__file__).resolve().parent.parent.parent
  oracle = RepoOracle(repo_root)
  oracle.index()

  results = oracle.grep_pattern(query, max_results=25)
  summary = oracle.summary()

  # Log to evidence flight recorder
  _log_evidence(repo_root, query, len(results))

  if json_output:
    print(
      json.dumps({"query": query, "matches": results, "summary": summary}, indent=2)
    )
  else:
    print("═══════════════════════════════════════════")
    print(f"  Repo Oracle — Searching: {query}")
    print("═══════════════════════════════════════════")
    for r in results:
      print(f"  ✓ {r}")
    print("  ─────────────────────────────────────────")
    print(f"  Matches found: {len(results)}")
    print("═══════════════════════════════════════════")
    if results:
      print("  ⚠ Existing implementations detected. Review before creating new code.")
    print(
      f"  Index: {summary['packages']}pkg {summary['scripts']}scr {summary['skills']}skl {summary['apps']}app {summary['libs']}lib"
    )


if __name__ == "__main__":
  main()
