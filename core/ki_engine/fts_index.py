# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
"""
SQLite FTS5 Index — Item 10: Full-text search index over KI artifacts.

Creates a derived SQLite index with FTS5 for fast keyword search.
File-first: the index is always rebuildable from markdown/JSON files.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.ki_engine.schema import KIMetadata
import contextlib


DB_NAME = ".ki-index.db"


def _db_path(ki_dir: Path) -> Path:
  return ki_dir / DB_NAME


def init_index(ki_dir: Path) -> sqlite3.Connection:
  """Initialize the SQLite FTS5 index.

  Creates tables:
    - ki_meta: Structured metadata
    - ki_fts: FTS5 virtual table for full-text search
  """
  db = _db_path(ki_dir)
  conn = sqlite3.connect(str(db))

  conn.executescript("""
        CREATE TABLE IF NOT EXISTS ki_meta (
            name TEXT PRIMARY KEY,
            ki_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            confidence REAL NOT NULL DEFAULT 1.0,
            ttl_days INTEGER,
            classification TEXT NOT NULL DEFAULT 'team',
            created TEXT,
            updated TEXT,
            tags TEXT,  -- JSON array
            summary TEXT,
            agent_id TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS ki_fts USING fts5(
            name,
            summary,
            tags,
            content,
            tokenize='porter'
        );

        CREATE TABLE IF NOT EXISTS ki_artifacts (
            ki_name TEXT NOT NULL,
            artifact_path TEXT NOT NULL,
            content TEXT,
            PRIMARY KEY (ki_name, artifact_path),
            FOREIGN KEY (ki_name) REFERENCES ki_meta(name)
        );
    """)

  conn.commit()
  return conn


def index_ki(
  conn: sqlite3.Connection,
  ki: KIMetadata,
  artifact_content: str | None = None,
) -> None:
  """Index a single KI into SQLite.

  Args:
      conn: SQLite connection.
      ki: KI metadata to index.
      artifact_content: Optional artifact text content.
  """
  ki_type = ki.ki_type.value if hasattr(ki.ki_type, "value") else str(ki.ki_type)
  status = ki.status.value if hasattr(ki.status, "value") else str(ki.status)
  classification = (
    ki.classification.value
    if hasattr(ki.classification, "value")
    else str(ki.classification)
  )
  tags_json = json.dumps(ki.tags)

  # Upsert metadata
  conn.execute(
    """INSERT OR REPLACE INTO ki_meta
           (name, ki_type, status, confidence, ttl_days, classification,
            created, updated, tags, summary, agent_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (
      ki.name,
      ki_type,
      status,
      ki.confidence,
      ki.ttl_days,
      classification,
      ki.created,
      ki.updated,
      tags_json,
      ki.summary,
      ki.agent_id,
    ),
  )

  # FTS index — delete existing entry then insert
  tags_text = " ".join(ki.tags)
  content = artifact_content or ""
  conn.execute("DELETE FROM ki_fts WHERE name = ?", (ki.name,))
  conn.execute(
    "INSERT INTO ki_fts(name, summary, tags, content) VALUES (?, ?, ?, ?)",
    (ki.name, ki.summary, tags_text, content),
  )

  conn.commit()


def search_fts(
  conn: sqlite3.Connection,
  query: str,
  limit: int = 20,
) -> list[tuple[str, float]]:
  """Search the FTS5 index using BM25 ranking.

  Args:
      conn: SQLite connection.
      query: Search query.
      limit: Maximum results.

  Returns:
      List of (ki_name, bm25_score) tuples, highest score first.
  """
  rows = conn.execute(
    """SELECT ki_fts.name, bm25(ki_fts) as score
           FROM ki_fts
           WHERE ki_fts MATCH ?
           ORDER BY score
           LIMIT ?""",
    (query, limit),
  ).fetchall()

  # BM25 returns negative scores (more negative = better match)
  return [(row[0], -row[1]) for row in rows]


def reindex_all(ki_dir: Path) -> int:
  """Rebuild the entire index from file system.

  This is the file-first principle: delete index, rebuild from files.

  Returns:
      Number of KIs indexed.
  """
  db = _db_path(ki_dir)
  if db.exists():
    db.unlink()

  conn = init_index(ki_dir)
  count = 0

  for ki_path in sorted(ki_dir.iterdir()):
    if not ki_path.is_dir():
      continue

    metadata_file = ki_path / "metadata.json"
    if not metadata_file.exists():
      continue

    try:
      ki = KIMetadata.load(metadata_file)

      # Read artifact content for FTS
      artifact_text = ""
      artifacts_dir = ki_path / "artifacts"
      if artifacts_dir.exists():
        for artifact in artifacts_dir.iterdir():
          if artifact.suffix in (".md", ".txt"):
            with contextlib.suppress(OSError):
              artifact_text += " " + artifact.read_text(errors="replace")

      index_ki(conn, ki, artifact_text)
      count += 1

    except json.JSONDecodeError, OSError:
      continue

  conn.close()
  return count
