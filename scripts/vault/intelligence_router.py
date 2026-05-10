#!/usr/bin/env python3
# Copyright 2026 ShadowTagAI. All rights reserved.
"""Intelligence Router — Routes cleaned data to downstream sinks.

After the zero-trust pipeline sanitizes data, the intelligence router
determines where cleaned content should go:

  1. LanceDB → vector embeddings for semantic search
  2. Obsidian → formatted markdown notes for knowledge graph
  3. Firestore → structured data for API queries
  4. Monitor → pipeline metrics and audit trail

Usage:
    python scripts/vault/intelligence_router.py vault/serve/meeting_notes.md
    python scripts/vault/intelligence_router.py --route-all
    python scripts/vault/intelligence_router.py --dry-run vault/serve/
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [VAULT-ROUTER] %(levelname)s %(message)s",
  datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("vault.router")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_DIR = REPO_ROOT / "vault"
SERVE_DIR = VAULT_DIR / "serve"
EMBED_DIR = VAULT_DIR / "embed"
MONITOR_DIR = VAULT_DIR / "monitor"

# --- Route Classification ---------------------------------------------------


def classify_content(content: str, filename: str) -> list[str]:
  """Determine which downstream sinks a file should be routed to.

  Returns a list of route names: 'lancedb', 'obsidian', 'firestore'.
  """
  routes: list[str] = []

  # Everything gets embedded for semantic search
  routes.append("lancedb")

  # Text-heavy files go to Obsidian as knowledge notes
  word_count = len(content.split())
  if word_count > 50:
    routes.append("obsidian")

  # Structured data goes to Firestore
  if filename.endswith((".json", ".yaml", ".yml", ".csv")):
    routes.append("firestore")

  return routes


# --- Route Handlers ----------------------------------------------------------


def route_to_lancedb(path: Path, content: str, *, dry_run: bool = False) -> dict:
  """Route content to LanceDB for vector embedding.

  In production, this calls the embed_to_lancedb.py script.
  Here we prepare the embedding manifest.
  """
  manifest = {
    "source": str(path),
    "target": "lancedb",
    "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
    "word_count": len(content.split()),
    "char_count": len(content),
  }

  if not dry_run:
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = EMBED_DIR / f"{path.stem}_embed_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    logger.info("LanceDB manifest: %s", manifest_path.name)

  return {"route": "lancedb", "status": "manifested" if not dry_run else "dry-run"}


def route_to_obsidian(path: Path, content: str, *, dry_run: bool = False) -> dict:
  """Route content to Obsidian-formatted note in serve/.

  Adds YAML frontmatter and WikiLinks per the Obsidian Visual Graph Protocol.
  """
  # Generate YAML frontmatter
  now = datetime.now(timezone.utc)  # noqa: UP017
  frontmatter = f"---\ndate: {now.strftime('%Y-%m-%d')}\nsource: {path.name}\ntags: [ai-generated, vault-ingested]\n---\n\n"

  # Add WikiLinks for detected entities
  wikified = _add_wikilinks(content)
  obsidian_content = frontmatter + wikified

  if not dry_run:
    dest = SERVE_DIR / f"{path.stem}_obsidian.md"
    dest.write_text(obsidian_content, encoding="utf-8")
    logger.info("Obsidian note: %s", dest.name)

  return {"route": "obsidian", "status": "written" if not dry_run else "dry-run"}


def route_to_firestore(path: Path, content: str, *, dry_run: bool = False) -> dict:
  """Prepare structured data for Firestore ingestion.

  Does NOT write to Firestore directly (that requires MCP).
  Instead creates a Firestore-ready JSON manifest.
  """
  manifest = {
    "collection": "vault_intelligence",
    "document_id": path.stem,
    "fields": {
      "source_file": path.name,
      "ingested_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
      "content_preview": content[:500],
      "word_count": len(content.split()),
    },
  }

  if not dry_run:
    MONITOR_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MONITOR_DIR / f"{path.stem}_firestore_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    logger.info("Firestore manifest: %s", manifest_path.name)

  return {"route": "firestore", "status": "manifested" if not dry_run else "dry-run"}


# --- WikiLink Generator ------------------------------------------------------


# Entities to auto-link in Obsidian notes
_KNOWN_ENTITIES = {
  "kovelai",
  "counselconduit",
  "uphillsnowball",
  "shadowtag",
  "firestore",
  "cloud run",
  "cloud tasks",
  "firebase",
  "gemini",
  "claude",
  "openai",
  "lancedb",
  "obsidian",
  "kairos",
  "oracle studio",
  "judge 6",
  "kovel",
  "stripe",
  "gcp",
  "secret manager",
  "react",
  "next.js",
  "vite",
  "python",
  "typescript",
  "pydantic",
  "fastapi",
  "semantic kernel",
}


def _add_wikilinks(content: str) -> str:
  """Add Obsidian WikiLinks for known entities."""
  for entity in sorted(_KNOWN_ENTITIES, key=len, reverse=True):
    # Case-insensitive replace, but preserve original casing
    pattern = re.compile(re.escape(entity), re.IGNORECASE)
    # Only link first occurrence to avoid clutter
    match = pattern.search(content)
    if match:
      original = match.group()
      content = content[: match.start()] + f"[[{original}]]" + content[match.end() :]
  return content


# --- Pipeline Orchestration --------------------------------------------------


def route_file(path: Path, *, dry_run: bool = False) -> list[dict]:
  """Route a single file to all applicable sinks."""
  try:
    content = path.read_text(encoding="utf-8", errors="replace")
  except OSError as e:
    logger.error("Cannot read %s: %s", path, e)
    return [{"route": "error", "status": str(e)}]

  routes = classify_content(content, path.name)
  results: list[dict] = []

  handler_map = {
    "lancedb": route_to_lancedb,
    "obsidian": route_to_obsidian,
    "firestore": route_to_firestore,
  }

  for route in routes:
    handler = handler_map.get(route)
    if handler:
      result = handler(path, content, dry_run=dry_run)
      results.append(result)
      logger.info("Routed %s → %s (%s)", path.name, route, result["status"])

  return results


def route_all(*, dry_run: bool = False) -> list[dict]:
  """Route all files in serve/ to their downstream sinks."""
  all_results: list[dict] = []
  if not SERVE_DIR.exists():
    logger.warning("serve/ directory does not exist")
    return all_results

  for path in sorted(SERVE_DIR.iterdir()):
    if (
      path.is_file()
      and path.name != ".gitkeep"
      and not path.name.endswith("_obsidian.md")
    ):
      results = route_file(path, dry_run=dry_run)
      all_results.extend(results)

  # Write routing metrics
  if not dry_run and all_results:
    metrics = {
      "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
      "total_routes": len(all_results),
      "by_route": {},
    }
    for r in all_results:
      route = r.get("route", "unknown")
      metrics["by_route"][route] = metrics["by_route"].get(route, 0) + 1

    MONITOR_DIR.mkdir(parents=True, exist_ok=True)
    (MONITOR_DIR / "routing_metrics.json").write_text(json.dumps(metrics, indent=2))

  return all_results


# --- CLI Entry Point ---------------------------------------------------------


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Intelligence Router — Vault downstream routing"
  )
  parser.add_argument("input", nargs="?", help="File or directory to route")
  parser.add_argument(
    "--route-all", action="store_true", help="Route all files in serve/"
  )
  parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
  args = parser.parse_args()

  if args.route_all:
    results = route_all(dry_run=args.dry_run)
  elif args.input:
    path = Path(args.input)
    if path.is_dir():
      results = []
      for f in sorted(path.iterdir()):
        if f.is_file() and f.name != ".gitkeep":
          results.extend(route_file(f, dry_run=args.dry_run))
    else:
      results = route_file(path, dry_run=args.dry_run)
  else:
    parser.error("Provide input path or use --route-all")
    return 1

  logger.info("Routing complete: %d route(s) executed", len(results))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
