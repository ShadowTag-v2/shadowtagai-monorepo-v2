# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Intelligence Database - Local SQLite Storage
Stores scored content and metadata
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

import structlog

from ..config import STORAGE_CONFIG
from ..engines.jr_engine import JRScore

logger = structlog.get_logger(__name__)


class IntelDatabase:
  """
  Local SQLite database for intelligence storage

  Tables:
  - repositories: GitHub repo metadata and scores
  - papers: arXiv paper metadata and scores
  - briefings: Generated briefing history
  """

  def __init__(self, db_path: str | None = None):
    self.db_path = db_path or STORAGE_CONFIG["database"]["path"]
    Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    self._init_database()
    logger.info("intel_database_initialized", db_path=self.db_path)

  @contextmanager
  def _get_connection(self):
    """Context manager for database connections"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
      yield conn
      conn.commit()
    except Exception as e:
      conn.rollback()
      raise e
    finally:
      conn.close()

  def _init_database(self):
    """Initialize database schema"""
    with self._get_connection() as conn:
      cursor = conn.cursor()

      # Repositories table
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_name TEXT UNIQUE NOT NULL,
                    stars INTEGER,
                    description TEXT,
                    url TEXT,
                    topics TEXT,  -- JSON array
                    language TEXT,
                    updated_at TEXT,
                    discovered_at TEXT NOT NULL,
                    flattened_file_path TEXT,

                    -- JR Scores
                    purpose_alignment REAL,
                    technical_merit REAL,
                    adoption_potential REAL,
                    risk_assessment REAL,
                    total_score REAL,
                    tier INTEGER,
                    atp_risk_level TEXT,

                    -- Reasoning
                    purpose_reasoning TEXT,
                    technical_reasoning TEXT,
                    adoption_reasoning TEXT,
                    risk_reasoning TEXT,
                    brakes TEXT,  -- JSON array

                    -- Metadata
                    scored_at TEXT,
                    processed BOOLEAN DEFAULT 0
                )
            """)

      # Papers table
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arxiv_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT,  -- JSON array
                    abstract TEXT,
                    categories TEXT,  -- JSON array
                    primary_category TEXT,
                    published_date TEXT,
                    pdf_url TEXT,
                    discovered_at TEXT NOT NULL,
                    metadata_file_path TEXT,
                    pdf_file_path TEXT,

                    -- JR Scores
                    purpose_alignment REAL,
                    technical_merit REAL,
                    adoption_potential REAL,
                    risk_assessment REAL,
                    total_score REAL,
                    tier INTEGER,
                    atp_risk_level TEXT,

                    -- Reasoning
                    purpose_reasoning TEXT,
                    technical_reasoning TEXT,
                    adoption_reasoning TEXT,
                    risk_reasoning TEXT,
                    brakes TEXT,  -- JSON array

                    -- Metadata
                    scored_at TEXT,
                    processed BOOLEAN DEFAULT 0
                )
            """)

      # Briefings table
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS briefings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generated_at TEXT NOT NULL,
                    date_range_start TEXT,
                    date_range_end TEXT,
                    total_repos INTEGER,
                    total_papers INTEGER,
                    tier1_count INTEGER,
                    tier2_count INTEGER,
                    tier3_count INTEGER,
                    tier4_count INTEGER,
                    briefing_file_path TEXT,
                    summary TEXT
                )
            """)

      # Create indices
      cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_tier ON repositories(tier)")
      cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_repos_score ON repositories(total_score)"
      )
      cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_tier ON papers(tier)")
      cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_papers_score ON papers(total_score)"
      )

      logger.info("database_schema_initialized")

  def store_repository_score(
    self, repo_name: str, score: JRScore, metadata: dict | None = None
  ):
    """
    Store GitHub repository score

    Args:
        repo_name: Repository name (owner/repo)
        score: JRScore object
        metadata: Additional repository metadata
    """
    metadata = metadata or {}

    with self._get_connection() as conn:
      cursor = conn.cursor()

      cursor.execute(
        """
                INSERT OR REPLACE INTO repositories (
                    repo_name, stars, description, url, topics, language, updated_at,
                    discovered_at, flattened_file_path,
                    purpose_alignment, technical_merit, adoption_potential, risk_assessment,
                    total_score, tier, atp_risk_level,
                    purpose_reasoning, technical_reasoning, adoption_reasoning, risk_reasoning,
                    brakes, scored_at, processed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
          repo_name,
          metadata.get("stars"),
          metadata.get("description"),
          metadata.get("url"),
          json.dumps(metadata.get("topics", [])),
          metadata.get("language"),
          metadata.get("updated_at"),
          datetime.now().isoformat(),
          metadata.get("flattened_file_path"),
          score.purpose_alignment,
          score.technical_merit,
          score.adoption_potential,
          score.risk_assessment,
          score.total_score,
          score.tier.value,
          score.atp_risk_level,
          score.purpose_reasoning,
          score.technical_reasoning,
          score.adoption_reasoning,
          score.risk_reasoning,
          json.dumps(score.brakes),
          datetime.now().isoformat(),
          False,
        ),
      )

      logger.info(
        "repository_score_stored",
        repo_name=repo_name,
        score=score.total_score,
        tier=score.tier.value,
      )

  def store_paper_score(
    self, arxiv_id: str, score: JRScore, metadata: dict | None = None
  ):
    """
    Store arXiv paper score

    Args:
        arxiv_id: arXiv paper ID
        score: JRScore object
        metadata: Additional paper metadata
    """
    metadata = metadata or {}

    with self._get_connection() as conn:
      cursor = conn.cursor()

      cursor.execute(
        """
                INSERT OR REPLACE INTO papers (
                    arxiv_id, title, authors, abstract, categories, primary_category,
                    published_date, pdf_url, discovered_at, metadata_file_path, pdf_file_path,
                    purpose_alignment, technical_merit, adoption_potential, risk_assessment,
                    total_score, tier, atp_risk_level,
                    purpose_reasoning, technical_reasoning, adoption_reasoning, risk_reasoning,
                    brakes, scored_at, processed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
          arxiv_id,
          metadata.get("title"),
          json.dumps(metadata.get("authors", [])),
          metadata.get("abstract"),
          json.dumps(metadata.get("categories", [])),
          metadata.get("primary_category"),
          metadata.get("published_date"),
          metadata.get("pdf_url"),
          datetime.now().isoformat(),
          metadata.get("metadata_file_path"),
          metadata.get("pdf_file_path"),
          score.purpose_alignment,
          score.technical_merit,
          score.adoption_potential,
          score.risk_assessment,
          score.total_score,
          score.tier.value,
          score.atp_risk_level,
          score.purpose_reasoning,
          score.technical_reasoning,
          score.adoption_reasoning,
          score.risk_reasoning,
          json.dumps(score.brakes),
          datetime.now().isoformat(),
          False,
        ),
      )

      logger.info(
        "paper_score_stored",
        arxiv_id=arxiv_id,
        score=score.total_score,
        tier=score.tier.value,
      )

  def get_repositories_by_tier(self, tier: int) -> list[dict]:
    """Get repositories by tier"""
    with self._get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
        """
                SELECT * FROM repositories
                WHERE tier = ?
                ORDER BY total_score DESC
            """,
        (tier,),
      )

      return [dict(row) for row in cursor.fetchall()]

  def get_papers_by_tier(self, tier: int) -> list[dict]:
    """Get papers by tier"""
    with self._get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
        """
                SELECT * FROM papers
                WHERE tier = ?
                ORDER BY total_score DESC
            """,
        (tier,),
      )

      return [dict(row) for row in cursor.fetchall()]

  def get_tier_summary(self) -> dict[int, dict[str, int]]:
    """
    Get summary of content by tier

    Returns:
        Dict mapping tier number to counts
    """
    with self._get_connection() as conn:
      cursor = conn.cursor()

      summary = {}

      for tier in [1, 2, 3, 4]:
        cursor.execute("SELECT COUNT(*) FROM repositories WHERE tier = ?", (tier,))
        repo_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM papers WHERE tier = ?", (tier,))
        paper_count = cursor.fetchone()[0]

        summary[tier] = {
          "repositories": repo_count,
          "papers": paper_count,
          "total": repo_count + paper_count,
        }

      return summary

  def store_briefing(
    self,
    date_range_start: str,
    date_range_end: str,
    briefing_file_path: str,
    summary: str,
    tier_counts: dict[int, int],
  ):
    """Store briefing metadata"""
    with self._get_connection() as conn:
      cursor = conn.cursor()

      cursor.execute(
        """
                INSERT INTO briefings (
                    generated_at, date_range_start, date_range_end,
                    total_repos, total_papers,
                    tier1_count, tier2_count, tier3_count, tier4_count,
                    briefing_file_path, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
          datetime.now().isoformat(),
          date_range_start,
          date_range_end,
          sum([tier_counts.get(t, {}).get("repositories", 0) for t in [1, 2, 3, 4]]),
          sum([tier_counts.get(t, {}).get("papers", 0) for t in [1, 2, 3, 4]]),
          tier_counts.get(1, {}).get("total", 0),
          tier_counts.get(2, {}).get("total", 0),
          tier_counts.get(3, {}).get("total", 0),
          tier_counts.get(4, {}).get("total", 0),
          briefing_file_path,
          summary,
        ),
      )

      logger.info("briefing_stored", file=briefing_file_path)

  def get_all_scores(self) -> tuple[list[dict], list[dict]]:
    """
    Get all scored content

    Returns:
        Tuple of (repositories, papers)
    """
    with self._get_connection() as conn:
      cursor = conn.cursor()

      cursor.execute("SELECT * FROM repositories ORDER BY total_score DESC")
      repos = [dict(row) for row in cursor.fetchall()]

      cursor.execute("SELECT * FROM papers ORDER BY total_score DESC")
      papers = [dict(row) for row in cursor.fetchall()]

      return repos, papers
