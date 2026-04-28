# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CRM Analytics - Track quality scores and re-loop effectiveness

SQLite-based tracking for:
- Run history
- Re-loop analysis
- Cost trends
"""

import os
import sqlite3
from datetime import datetime


def init_db(db_path: str):
    """Initialize the analytics database"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Run history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id TEXT UNIQUE,
            timestamp TEXT,
            success INTEGER,
            crm_score REAL,
            total_cost REAL,
            cycles INTEGER,
            relooped INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Re-loop analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reloops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id TEXT,
            before_score REAL,
            after_score REAL,
            improvement REAL,
            tools_used TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES runs(query_id)
        )
    """)

    # Cost breakdown table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id TEXT,
            layer TEXT,
            cost REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES runs(query_id)
        )
    """)

    conn.commit()
    conn.close()


def log_run(
    db_path: str,
    query_id: str,
    success: bool,
    crm_score: float,
    total_cost: float,
    cycles: int,
    relooped: bool,
):
    """Log a pipeline run"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO runs
        (query_id, timestamp, success, crm_score, total_cost, cycles, relooped)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            query_id,
            datetime.now().isoformat(),
            1 if success else 0,
            crm_score,
            total_cost,
            cycles,
            1 if relooped else 0,
        ),
    )

    conn.commit()
    conn.close()


def log_reloop(
    db_path: str,
    query_id: str,
    before_score: float,
    after_score: float,
    tools_used: str,
):
    """Log a re-loop event"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    improvement = after_score - before_score

    cursor.execute(
        """
        INSERT INTO reloops
        (query_id, before_score, after_score, improvement, tools_used)
        VALUES (?, ?, ?, ?, ?)
    """,
        (query_id, before_score, after_score, improvement, tools_used),
    )

    conn.commit()
    conn.close()


def log_cost(db_path: str, query_id: str, layer: str, cost: float):
    """Log cost for a specific layer"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO costs (query_id, layer, cost)
        VALUES (?, ?, ?)
    """,
        (query_id, layer, cost),
    )

    conn.commit()
    conn.close()


def get_stats(db_path: str, days: int = 7) -> dict:
    """Get aggregate statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total runs
    cursor.execute("SELECT COUNT(*) FROM runs")
    total_runs = cursor.fetchone()[0]

    # Success rate
    cursor.execute("SELECT AVG(success) FROM runs")
    success_rate = cursor.fetchone()[0] or 0

    # Average CRM score
    cursor.execute("SELECT AVG(crm_score) FROM runs WHERE success = 1")
    avg_crm = cursor.fetchone()[0] or 0

    # Average cost
    cursor.execute("SELECT AVG(total_cost) FROM runs")
    avg_cost = cursor.fetchone()[0] or 0

    # Re-loop effectiveness
    cursor.execute("SELECT AVG(improvement) FROM reloops")
    avg_reloop_improvement = cursor.fetchone()[0] or 0

    # Re-loop rate
    cursor.execute("SELECT AVG(relooped) FROM runs")
    reloop_rate = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_runs": total_runs,
        "success_rate": success_rate,
        "avg_crm_score": avg_crm,
        "avg_cost": avg_cost,
        "reloop_rate": reloop_rate,
        "avg_reloop_improvement": avg_reloop_improvement,
    }


def get_cost_breakdown(db_path: str) -> dict[str, float]:
    """Get cost breakdown by layer"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT layer, SUM(cost) as total_cost
        FROM costs
        GROUP BY layer
        ORDER BY total_cost DESC
    """)

    breakdown = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return breakdown


def get_recent_runs(db_path: str, limit: int = 10) -> list[dict]:
    """Get recent run history"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM runs
        ORDER BY created_at DESC
        LIMIT ?
    """,
        (limit,),
    )

    runs = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return runs
