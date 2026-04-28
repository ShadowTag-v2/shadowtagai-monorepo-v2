# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Intelligence Database - Local SQLite Storage
Stores scored content, metadata, and IntelEvents from Gemini normalization

Enhanced with intel_events table for structured Gemini-extracted events.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from ..config import STORAGE_CONFIG
from ..engines.jr_engine import JRScore

if TYPE_CHECKING:
    from app.models.intel_event import IntelEvent

logger = structlog.get_logger(__name__)


class IntelDatabase:
    """Local SQLite database for intelligence storage

    Tables:
    - repositories: GitHub repo metadata and scores
    - papers: arXiv paper metadata and scores
    - intel_events: Structured IntelEvents from Gemini normalization
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

            # Intel Events table (Gemini normalization output)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS intel_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    source_url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    jurisdiction TEXT,
                    effective_date TEXT,
                    publication_date TEXT,
                    title TEXT,
                    topic_tags TEXT,  -- JSON array
                    change_type TEXT,
                    summary TEXT,
                    impacts TEXT,  -- JSON array
                    risk_tags TEXT,  -- JSON array

                    -- JR Hints from Gemini
                    jr_hints TEXT,  -- JSON object
                    suggested_tier INTEGER,
                    urgency_score REAL,

                    -- Provenance
                    raw_text_hash TEXT,
                    gemini_model TEXT,
                    gemini_confidence REAL,
                    extraction_version TEXT,
                    raw_storage_path TEXT,

                    -- Delta tracking
                    previous_version_id TEXT,
                    delta_summary TEXT,

                    -- JR Scoring (filled after scoring)
                    jr_total_score REAL,
                    jr_tier INTEGER,
                    jr_atp_risk_level TEXT,
                    jr_scored_at TEXT,

                    -- Timestamps
                    created_at TEXT NOT NULL,
                    updated_at TEXT,

                    -- Processing status
                    processed BOOLEAN DEFAULT 0
                )
            """)

            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_tier ON repositories(tier)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_repos_score ON repositories(total_score)",
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_tier ON papers(tier)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_score ON papers(total_score)")

            # Intel events indices
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_source_type ON intel_events(source_type)",
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_jurisdiction ON intel_events(jurisdiction)",
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_effective_date ON intel_events(effective_date)",
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_tier ON intel_events(jr_tier)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_urgency ON intel_events(urgency_score)",
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_created ON intel_events(created_at)",
            )

            logger.info("database_schema_initialized")

    def store_repository_score(self, repo_name: str, score: JRScore, metadata: dict | None = None):
        """Store GitHub repository score

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

    def store_paper_score(self, arxiv_id: str, score: JRScore, metadata: dict | None = None):
        """Store arXiv paper score

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
        """Get summary of content by tier

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
        """Get all scored content

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

    # ========== IntelEvent Storage Methods ==========

    def store_intel_event(self, event: "IntelEvent", score: JRScore | None = None):
        """Store an IntelEvent from Gemini normalization

        Args:
            event: IntelEvent object from Gemini normalizer
            score: Optional JRScore if already scored

        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO intel_events (
                    event_id, source_url, source_type, jurisdiction,
                    effective_date, publication_date, title, topic_tags,
                    change_type, summary, impacts, risk_tags,
                    jr_hints, suggested_tier, urgency_score,
                    raw_text_hash, gemini_model, gemini_confidence,
                    extraction_version, raw_storage_path,
                    previous_version_id, delta_summary,
                    jr_total_score, jr_tier, jr_atp_risk_level, jr_scored_at,
                    created_at, updated_at, processed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.id,
                    event.source_url,
                    event.source_type.value,
                    event.jurisdiction,
                    event.effective_date.isoformat() if event.effective_date else None,
                    event.publication_date.isoformat() if event.publication_date else None,
                    event.title,
                    json.dumps(event.topic_tags),
                    event.change_type.value,
                    event.summary,
                    json.dumps([i.model_dump() for i in event.impacts]),
                    json.dumps([t.value for t in event.risk_tags]),
                    json.dumps(event.jr_hints.model_dump()),
                    event.jr_hints.suggested_tier,
                    event.jr_hints.urgency_score,
                    event.raw_text_hash,
                    event.gemini_model,
                    event.gemini_confidence,
                    event.extraction_version,
                    event.raw_storage_path,
                    event.previous_version_id,
                    event.delta_summary,
                    score.total_score if score else None,
                    score.tier.value if score else None,
                    score.atp_risk_level if score else None,
                    datetime.now().isoformat() if score else None,
                    event.created_at.isoformat(),
                    datetime.now().isoformat(),
                    False,
                ),
            )

            logger.info(
                "intel_event_stored",
                event_id=event.id,
                source_type=event.source_type.value,
                jurisdiction=event.jurisdiction,
            )

    def store_intel_events_batch(self, events: list["IntelEvent"]):
        """Store multiple IntelEvents"""
        for event in events:
            try:
                self.store_intel_event(event)
            except Exception as e:
                logger.error("intel_event_store_error", event_id=event.id, error=str(e))

        logger.info("intel_events_batch_stored", count=len(events))

    def update_intel_event_score(self, event_id: str, score: JRScore):
        """Update JR score for an existing IntelEvent"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE intel_events SET
                    jr_total_score = ?,
                    jr_tier = ?,
                    jr_atp_risk_level = ?,
                    jr_scored_at = ?,
                    updated_at = ?,
                    processed = 1
                WHERE event_id = ?
            """,
                (
                    score.total_score,
                    score.tier.value,
                    score.atp_risk_level,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    event_id,
                ),
            )

            logger.info(
                "intel_event_score_updated",
                event_id=event_id,
                score=score.total_score,
                tier=score.tier.value,
            )

    def get_intel_events_by_tier(self, tier: int) -> list[dict]:
        """Get IntelEvents by JR tier"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM intel_events
                WHERE jr_tier = ?
                ORDER BY urgency_score DESC, jr_total_score DESC
            """,
                (tier,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_intel_events_by_jurisdiction(self, jurisdiction: str) -> list[dict]:
        """Get IntelEvents by jurisdiction"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM intel_events
                WHERE jurisdiction = ?
                ORDER BY effective_date ASC, urgency_score DESC
            """,
                (jurisdiction,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_intel_events_by_source_type(self, source_type: str) -> list[dict]:
        """Get IntelEvents by source type"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM intel_events
                WHERE source_type = ?
                ORDER BY created_at DESC
            """,
                (source_type,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_effective_dates(self, days_ahead: int = 90) -> list[dict]:
        """Get IntelEvents with upcoming effective dates"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM intel_events
                WHERE effective_date IS NOT NULL
                AND effective_date >= date('now')
                AND effective_date <= date('now', ? || ' days')
                ORDER BY effective_date ASC
            """,
                (str(days_ahead),),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_high_urgency_events(self, min_urgency: float = 0.7) -> list[dict]:
        """Get high urgency IntelEvents"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM intel_events
                WHERE urgency_score >= ?
                ORDER BY urgency_score DESC, jr_total_score DESC
            """,
                (min_urgency,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_intel_event_summary(self) -> dict:
        """Get summary statistics for IntelEvents"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total counts
            cursor.execute("SELECT COUNT(*) FROM intel_events")
            total = cursor.fetchone()[0]

            # By source type
            cursor.execute("""
                SELECT source_type, COUNT(*) as count
                FROM intel_events
                GROUP BY source_type
            """)
            by_source = {row[0]: row[1] for row in cursor.fetchall()}

            # By jurisdiction
            cursor.execute("""
                SELECT jurisdiction, COUNT(*) as count
                FROM intel_events
                WHERE jurisdiction IS NOT NULL
                GROUP BY jurisdiction
            """)
            by_jurisdiction = {row[0]: row[1] for row in cursor.fetchall()}

            # By tier
            cursor.execute("""
                SELECT jr_tier, COUNT(*) as count
                FROM intel_events
                WHERE jr_tier IS NOT NULL
                GROUP BY jr_tier
            """)
            by_tier = {row[0]: row[1] for row in cursor.fetchall()}

            # Avg urgency
            cursor.execute("SELECT AVG(urgency_score) FROM intel_events")
            avg_urgency = cursor.fetchone()[0] or 0

            return {
                "total_events": total,
                "by_source_type": by_source,
                "by_jurisdiction": by_jurisdiction,
                "by_tier": by_tier,
                "avg_urgency_score": round(avg_urgency, 3),
            }
