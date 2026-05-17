"""Step 4 — Gap Analyzer.

Three gap types from the match tables:

  Type A — Documented, not implemented (biz/arch doc with no code match above 0.7)
  Type B — Implemented, not documented (code file with no doc match above 0.6)
  Type C — Stale docs (doc matches code that was deleted or significantly changed)

Output: crossref.db → table gap_matrix
"""

import argparse
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "intelligence_pipeline" / "crossref.db"

TYPE_A_THRESHOLD = 0.7
TYPE_B_THRESHOLD = 0.6


def init_gap_table(conn: sqlite3.Connection) -> None:
  """Create gap_matrix table."""
  conn.execute(
    """CREATE TABLE IF NOT EXISTS gap_matrix (
            gap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            gap_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            source_title TEXT,
            best_match_id TEXT,
            best_similarity REAL,
            domain TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'open',
            analyzed_at TEXT NOT NULL
        )""",
  )
  conn.commit()


def analyze_type_a(conn: sqlite3.Connection) -> int:
  """Type A: Documented features not implemented in code."""
  cursor = conn.execute(
    """SELECT d.doc_id, d.title, d.domain,
                  COALESCE(MAX(m.similarity), 0) AS best_sim,
                  m.code_path
           FROM doc_domains d
           LEFT JOIN doc_code_matches m ON d.doc_id = m.doc_id
           WHERE d.domain IN ('biz', 'arch', 'skills')
           GROUP BY d.doc_id
           HAVING best_sim < ?""",
    (TYPE_A_THRESHOLD,),
  )
  count = 0
  now = datetime.now(timezone.utc).isoformat()
  for row in cursor:
    conn.execute(
      """INSERT INTO gap_matrix (gap_type, source_id, source_title, best_match_id,
               best_similarity, domain, priority, analyzed_at)
               VALUES ('A', ?, ?, ?, ?, ?, 'high', ?)""",
      (row[0], row[1], row[4], row[3], row[2], now),
    )
    count += 1
  conn.commit()
  logger.info(f"Type A gaps: {count}")
  return count


def analyze_type_b(conn: sqlite3.Connection) -> int:
  """Type B: Code implemented but not documented."""
  cursor = conn.execute(
    """SELECT DISTINCT m.code_path,
                  COALESCE(MAX(m.similarity), 0) AS best_sim
           FROM doc_code_matches m
           GROUP BY m.code_path
           HAVING best_sim < ?""",
    (TYPE_B_THRESHOLD,),
  )
  count = 0
  now = datetime.now(timezone.utc).isoformat()
  for row in cursor:
    conn.execute(
      """INSERT INTO gap_matrix (gap_type, source_id, source_title, best_similarity,
               domain, priority, analyzed_at)
               VALUES ('B', ?, ?, ?, 'tech', 'medium', ?)""",
      (row[0], row[0], row[1], now),
    )
    count += 1
  conn.commit()
  logger.info(f"Type B gaps: {count}")
  return count


def analyze_type_c(conn: sqlite3.Connection) -> int:
  """Type C: Stale docs — matched code no longer exists."""
  count = 0
  now = datetime.now(timezone.utc).isoformat()
  cursor = conn.execute(
    """SELECT m.doc_id, d.title, m.code_path, m.similarity
           FROM doc_code_matches m
           JOIN doc_domains d ON m.doc_id = d.doc_id
           WHERE m.rank = 1 AND m.similarity > 0.5""",
  )
  for row in cursor:
    code_path = REPO_ROOT / row[2]
    if not code_path.exists():
      conn.execute(
        """INSERT INTO gap_matrix (gap_type, source_id, source_title, best_match_id,
                   best_similarity, domain, priority, analyzed_at)
                   VALUES ('C', ?, ?, ?, ?, 'tech', 'low', ?)""",
        (row[0], row[1], row[2], row[3], now),
      )
      count += 1
  conn.commit()
  logger.info(f"Type C gaps: {count}")
  return count


def run_gap_analyzer(cfg=None) -> dict:
  """Execute Step 4: Gap Analyzer."""
  logger.info("Gap Analyzer — Step 4")

  conn = sqlite3.connect(str(DB_PATH))
  init_gap_table(conn)

  # Clear previous gaps
  conn.execute("DELETE FROM gap_matrix")
  conn.commit()

  a = analyze_type_a(conn)
  b = analyze_type_b(conn)
  c = analyze_type_c(conn)

  total = conn.execute("SELECT COUNT(*) FROM gap_matrix").fetchone()[0]
  conn.close()

  stats = {"type_a": a, "type_b": b, "type_c": c, "total": total}
  logger.info(f"Gap Analyzer complete: {stats}")
  return stats


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Gap Analyzer — Step 4")
  parser.parse_args()
  run_gap_analyzer()
