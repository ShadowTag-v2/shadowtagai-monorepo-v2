#!/usr/bin/env python3
"""tools/memory-mcp-server/server.py — Continuous Agentic Memory MCP Server.

Exposes the 4-stage memory loop + LanceDB semantic search + BQ Graph queries
as MCP tools for Cline (Plane 2) and any stdio-connected agent.

Tools:
  - memory_inject: Get persistent memory XML for system prompt injection
  - memory_stats: Get memory system health stats
  - memory_reflect: Trigger a reflection pass over beads trail
  - memory_search: Semantic search over the 1,094-doc Drive corpus via LanceDB
  - memory_graph_query: GQL query over BigQuery Property Graph
  - memory_add_fact: Add a fact to the persistent memory store
  - memory_add_correction: Log a correction to prevent future mistakes
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# FastMCP import — requires mcp[cli] or fastmcp
try:
  from mcp.server.fastmcp import FastMCP
except ImportError:
  print(
    "ERROR: mcp package not installed. Run: pip install 'mcp[cli]'", file=sys.stderr
  )
  sys.exit(1)

REPO = Path(__file__).parent.parent.parent
MEMORY = REPO / ".ai-memory.md"
BEADS = REPO / ".beads" / "issues.jsonl"
LANCE_DB = REPO / "data" / "lance_corpus"
GRAPH_JSON = REPO / "data" / "memory" / "knowledge_graph.json"
REFLECTIONS = REPO / "data" / "memory" / "reflections.jsonl"
BQ_PROJECT = "shadowtag-omega-v4"
BQ_DATASET = "drive_corpus"
BQ_GRAPH = "doc_graph"

mcp = FastMCP(
  "Agentic Memory",
  version="1.0.0",
  description="Continuous Agentic Memory — Compounding Context for AI agents",
)


@mcp.tool()
def memory_inject() -> str:
  """Get the persistent memory XML block for system prompt injection.

  Returns the <persistent_memory> XML that should be prepended to
  agent system prompts for session continuity.
  """
  if not MEMORY.exists():
    return "<persistent_memory>No memory file found.</persistent_memory>"
  mem = MEMORY.read_text("utf-8")
  parts = ["<persistent_memory>", "Facts from previous sessions:"]
  for ln in mem.split("\n"):
    if ln.strip().startswith("- "):
      parts.append(ln.strip())
  parts.append("</persistent_memory>")
  return "\n".join(parts)


@mcp.tool()
def memory_stats() -> str:
  """Get health stats for the agentic memory system.

  Returns counts of facts, beads, reflections, KIs, and graph size.
  """
  mem = MEMORY.read_text("utf-8") if MEMORY.exists() else ""
  facts = mem.count("\n- ")
  beads = 0
  if BEADS.exists():
    beads = sum(1 for _ in BEADS.open(encoding="utf-8"))
  reflections = 0
  if REFLECTIONS.exists():
    reflections = sum(1 for _ in REFLECTIONS.open(encoding="utf-8"))
  ki_dir = Path.home() / ".gemini/antigravity/knowledge"
  kis = (
    sum(1 for d in ki_dir.iterdir() if d.is_dir() and not d.name.startswith("_"))
    if ki_dir.exists()
    else 0
  )
  gn = ge = 0
  if GRAPH_JSON.exists():
    g = json.loads(GRAPH_JSON.read_text())
    gn = len(g.get("nodes", {}))
    ge = len(g.get("edges", []))
  lance_exists = LANCE_DB.exists()
  return json.dumps(
    {
      "facts": facts,
      "beads": beads,
      "reflections": reflections,
      "knowledge_items": kis,
      "graph_nodes": gn,
      "graph_edges": ge,
      "memory_size_bytes": len(mem),
      "lance_db_exists": lance_exists,
    },
    indent=2,
  )


@mcp.tool()
def memory_reflect() -> str:
  """Trigger a reflection pass over the beads trail.

  Extracts preferences and prohibitions from recent task completions
  and updates the knowledge graph.
  """
  result = subprocess.run(
    [sys.executable, str(REPO / "scripts/memory_reflection_daemon.py"), "--reflect"],
    capture_output=True,
    text=True,
    cwd=str(REPO),
  )
  return result.stdout.strip() or result.stderr.strip() or "Reflection complete."


@mcp.tool()
def memory_search(query: str, top_k: int = 5) -> str:
  """Semantic search over the Drive corpus using LanceDB vector embeddings.

  Args:
      query: Natural language search query.
      top_k: Number of results to return (default 5, max 20).
  """
  top_k = min(max(1, top_k), 20)
  try:
    import lancedb
    from sentence_transformers import SentenceTransformer
  except ImportError:
    return json.dumps({"error": "lancedb or sentence-transformers not installed"})

  if not LANCE_DB.exists():
    return json.dumps({"error": f"LanceDB not found at {LANCE_DB}"})

  model = SentenceTransformer("all-MiniLM-L6-v2")
  qvec = model.encode(query).tolist()
  db = lancedb.connect(str(LANCE_DB))
  table = db.open_table("drive_docs")
  results = table.search(qvec).limit(top_k).to_pandas()
  hits = []
  for _, row in results.iterrows():
    hits.append(
      {
        "document_id": row.get("document_id", ""),
        "source_file": row.get("source_file", ""),
        "content_preview": str(row.get("raw_content", ""))[:500],
        "distance": float(row.get("_distance", 0)),
      }
    )
  return json.dumps({"query": query, "results": hits}, indent=2)


@mcp.tool()
def memory_graph_query(search_term: str) -> str:
  """Query the BigQuery Property Graph (GQL) for documents matching a search term.

  Args:
      search_term: Term to search for in document IDs and source filenames.
  """
  gql = f"""
GRAPH {BQ_DATASET}.{BQ_GRAPH}
MATCH (doc)
WHERE doc.source_file LIKE '%{search_term}%' OR doc.document_id LIKE '%{search_term}%'
RETURN doc.document_id, doc.source_file, doc.byte_size
ORDER BY doc.byte_size DESC
NEXT
RETURN * LIMIT 20;
"""
  result = subprocess.run(
    [
      "bq",
      "query",
      "--project_id",
      BQ_PROJECT,
      "--use_legacy_sql=false",
      "--format=json",
      gql,
    ],
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return json.dumps({"error": result.stderr.strip()})
  try:
    return json.dumps(
      {"search_term": search_term, "results": json.loads(result.stdout)}, indent=2
    )
  except json.JSONDecodeError:
    return json.dumps({"search_term": search_term, "raw": result.stdout.strip()})


@mcp.tool()
def memory_add_fact(section: str, fact: str) -> str:
  """Add a fact to the persistent memory store (.ai-memory.md).

  Args:
      section: Section name (e.g., 'Coding Style', 'Architecture Decisions').
      fact: The fact to add (will be prefixed with '- ').
  """
  if not MEMORY.exists():
    return json.dumps({"error": "Memory file not found"})
  content = MEMORY.read_text("utf-8")
  marker = f"### {section}"
  if marker not in content:
    return json.dumps(
      {
        "error": f"Section '{section}' not found in memory. Available sections: "
        + ", ".join(m.group(1) for m in __import__("re").finditer(r"### (.+)", content))
      }
    )
  idx = content.index(marker)
  next_section = content.find("\n### ", idx + len(marker))
  if next_section == -1:
    next_section = content.find("\n## ", idx + len(marker))
  if next_section == -1:
    next_section = len(content)
  insert_pos = content.rfind("\n", idx, next_section) + 1
  new_content = content[:insert_pos] + f"- {fact}\n" + content[insert_pos:]
  MEMORY.write_text(new_content, "utf-8")
  return json.dumps({"status": "added", "section": section, "fact": fact})


@mcp.tool()
def memory_add_correction(correction: str) -> str:
  """Log a correction to prevent future mistakes.

  Args:
      correction: Description of the mistake and correct behavior.
  """
  if not MEMORY.exists():
    return json.dumps({"error": "Memory file not found"})
  content = MEMORY.read_text("utf-8")
  marker = "## 📋 Correction Log"
  if marker not in content:
    return json.dumps({"error": "Correction Log section not found"})
  from datetime import datetime, timezone

  ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
  idx = content.index(marker)
  next_section = content.find("\n## ", idx + len(marker))
  if next_section == -1:
    next_section = len(content)
  insert_pos = content.find("\n\n", idx) + 1
  if insert_pos == 0 or insert_pos > next_section:
    insert_pos = idx + len(marker) + 1
  new_content = content[:insert_pos] + f"\n- {ts}: {correction}" + content[insert_pos:]
  MEMORY.write_text(new_content, "utf-8")
  return json.dumps({"status": "logged", "date": ts, "correction": correction})


if __name__ == "__main__":
  mcp.run(transport="stdio")
