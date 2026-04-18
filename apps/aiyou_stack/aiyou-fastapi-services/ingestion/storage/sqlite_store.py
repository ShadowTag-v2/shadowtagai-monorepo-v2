"""PNKLN Core Stack - SQLite Ingest Store

Lightweight local persistence for ingested items and job state.
Replaces PostgreSQL/GCS until cloud infra is provisioned.
Thread-safe via check_same_thread=False + WAL mode.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from ..classification.tier_classifier import IngestedItem

logger = structlog.get_logger(__name__)

DEFAULT_DB = Path("data/web_ingest/ingest.db")


class IngestStore:
    """SQLite-backed store for ingested items and pipeline job records."""

    def __init__(self, db_path: Path = DEFAULT_DB) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._create_tables()
        logger.info("ingest_store_ready", path=str(db_path))

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id          TEXT PRIMARY KEY,
                source      TEXT NOT NULL,
                title       TEXT,
                content     TEXT,
                url         TEXT,
                published_at TEXT,
                author      TEXT,
                metadata    TEXT,
                tier        INTEGER DEFAULT 3,
                ingested_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_items_source   ON items(source);
            CREATE INDEX IF NOT EXISTS idx_items_tier     ON items(tier);
            CREATE INDEX IF NOT EXISTS idx_items_ingested ON items(ingested_at);

            CREATE TABLE IF NOT EXISTS jobs (
                job_id         TEXT PRIMARY KEY,
                status         TEXT NOT NULL,
                start_time     TEXT NOT NULL,
                end_time       TEXT,
                items_collected INTEGER DEFAULT 0,
                sources_active  INTEGER DEFAULT 0,
                errors         TEXT DEFAULT '[]'
            );
        """)
        self._conn.commit()

    # ── items ──────────────────────────────────────────────────────────────────

    def save_item(self, item: IngestedItem, tier: int = 3) -> bool:
        """Insert or ignore (dedup by id). Returns True if new row."""
        try:
            cur = self._conn.execute(
                """INSERT OR IGNORE INTO items
                   (id, source, title, content, url, published_at, author, metadata, tier, ingested_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    item.id,
                    item.source,
                    item.title,
                    item.content,
                    item.url,
                    item.published_at.isoformat() if item.published_at else None,
                    item.author,
                    json.dumps(item.metadata),
                    tier,
                    datetime.now().isoformat(),
                ),
            )
            self._conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error("save_item_failed", item_id=item.id, error=str(e))
            return False

    def query_items(
        self,
        tier: int | None = None,
        source: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return items as dicts matching optional filters."""
        clauses: list[str] = []
        params: list[Any] = []

        if tier is not None:
            clauses.append("tier = ?")
            params.append(tier)
        if source:
            clauses.append("source LIKE ?")
            params.append(f"%{source}%")
        if since:
            clauses.append("ingested_at >= ?")
            params.append(since.isoformat())

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        params += [limit, offset]

        rows = self._conn.execute(
            f"SELECT * FROM items {where} ORDER BY ingested_at DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()

        cols = [d[0] for d in self._conn.execute("SELECT * FROM items LIMIT 0").description]
        return [dict(zip(cols, row, strict=False)) for row in rows]

    def count_items(self, since: datetime | None = None) -> dict[str, int]:
        """Return item counts grouped by tier."""
        where = "WHERE ingested_at >= ?" if since else ""
        params = [since.isoformat()] if since else []
        rows = self._conn.execute(
            f"SELECT tier, COUNT(*) FROM items {where} GROUP BY tier",
            params,
        ).fetchall()
        counts: dict[str, int] = {f"tier_{t}": int(c) for t, c in rows}
        counts["total"] = sum(counts.values())
        return counts

    # ── jobs ───────────────────────────────────────────────────────────────────

    def create_job(self, job_id: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO jobs (job_id, status, start_time) VALUES (?,?,?)",
            (job_id, "running", datetime.now().isoformat()),
        )
        self._conn.commit()

    def complete_job(
        self,
        job_id: str,
        items_collected: int,
        sources_active: int,
        errors: list[str],
    ) -> None:
        self._conn.execute(
            """UPDATE jobs SET status=?, end_time=?, items_collected=?,
               sources_active=?, errors=? WHERE job_id=?""",
            (
                "completed",
                datetime.now().isoformat(),
                items_collected,
                sources_active,
                json.dumps(errors),
                job_id,
            ),
        )
        self._conn.commit()

    def fail_job(self, job_id: str, error: str) -> None:
        self._conn.execute(
            "UPDATE jobs SET status=?, end_time=?, errors=? WHERE job_id=?",
            ("failed", datetime.now().isoformat(), json.dumps([error]), job_id),
        )
        self._conn.commit()

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        cols = [d[0] for d in self._conn.execute("SELECT * FROM jobs LIMIT 0").description]
        d = dict(zip(cols, row, strict=False))
        d["errors"] = json.loads(d["errors"] or "[]")
        return d

    def latest_job(self) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT * FROM jobs ORDER BY start_time DESC LIMIT 1").fetchone()
        if not row:
            return None
        cols = [d[0] for d in self._conn.execute("SELECT * FROM jobs LIMIT 0").description]
        d = dict(zip(cols, row, strict=False))
        d["errors"] = json.loads(d["errors"] or "[]")
        return d

    def close(self) -> None:
        self._conn.close()
