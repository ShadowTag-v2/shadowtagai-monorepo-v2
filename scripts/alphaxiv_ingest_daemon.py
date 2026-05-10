#!/usr/bin/env python3
"""scripts/alphaxiv_ingest_daemon.py
Connects to the alphaXiv SSE MCP server to pull academic papers
on core financial/strategic concepts (Zero Trust, QSBS, Valuation).
Writes them to the RAG Intelligence Layer and triggers the loop.
"""

import asyncio
import json
import logging
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

# Optional: Use the official MCP SDK if installed
try:
  from mcp.client.session import ClientSession
  from mcp.client.sse import sse_client

  MCP_INSTALLED = True
except ImportError:
  MCP_INSTALLED = False

logging.basicConfig(
  level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("alphaxiv_ingest")

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data/alphaxiv"
DB_PATH = DATA_DIR / "ingest.db"
JSONL_PATH = DATA_DIR / "extractions.jsonl"

TARGET_CONCEPTS = [
  "NIST SP 800-53 LLM",
  "Zero Trust Architecture",
  "AI Alignment",
  "QSBS IRC 1202",
  "Quantitative Valuation Models",
]


def init_db():
  DATA_DIR.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS extractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            class TEXT,
            name TEXT,
            text TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
  conn.commit()
  return conn


async def run_alpha_xiv_mcp() -> None:
  if not MCP_INSTALLED:
    logger.error("mcp SDK not found. Install via: pip install mcp")
    logger.info("Writing placeholder schema. Run this script again post-install.")
    return

  logger.info("Connecting to AlphaXiv MCP (https://api.alphaxiv.org/mcp/v1)")

  conn = init_db()
  c = conn.cursor()

  async with (
    sse_client("https://api.alphaxiv.org/mcp/v1") as streams,
    ClientSession(streams[0], streams[1]) as session,
  ):
    await session.initialize()

    for concept in TARGET_CONCEPTS:
      logger.info(f"Querying alphaXiv for: {concept}")

      # Use the agentic_paper_retrieval tool exposed by the MCP
      result = await session.call_tool(
        "agentic_paper_retrieval", arguments={"query": concept, "top_k": 3}
      )

      papers = (
        json.loads(result.text)
        if hasattr(result, "text")
        else getattr(result, "content", [])
      )

      # Store extractions
      with open(JSONL_PATH, "a") as jsonl:
        for paper in papers:
          paper_id = paper.get("url", paper.get("id", f"alphaxiv_{time.time()}"))
          title = paper.get("title", f"Paper on {concept}")
          text = paper.get("abstract", "") + "\n" + paper.get("content", "")

          if not text.strip():
            continue

          # Insert SQL
          c.execute(
            "INSERT INTO extractions (file_id, class, name, text, status) VALUES (?, ?, ?, ?, ?)",
            (paper_id, "academic_paper", title, text, "ok"),
          )

          # JSONL append for LanceDB sync
          record = {
            "file_id": paper_id,
            "class": "academic_paper",
            "name": title,
            "text": text,
            "source": "alphaxiv",
          }
          jsonl.write(json.dumps(record) + "\n")

      conn.commit()
      await asyncio.sleep(2)  # rate limit

  conn.close()

  # ── Post-Ingest Trigger ───────────────────────────────────────────────────
  logger.info("Ingestion batch complete. Firing RAG Intelligence Layer...")
  try:
    subprocess.run(
      [sys.executable, "core/rag_evolve.py", "--post-ingest", "alphaxiv"],
      cwd=REPO_ROOT,
      check=False,
    )
  except Exception as e:
    logger.exception(f"Intelligence loop trigger failed: {e}")


if __name__ == "__main__":
  asyncio.run(run_alpha_xiv_mcp())
