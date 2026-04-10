"""
Atomic Chat Manager - OPORD-Based Context Management

Manages per-agent atomic contexts using Army Operations Order format.
Every chat thread follows the 5-paragraph OPORD structure for uniformity.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OPORDContext:
    """Army Operations Order format for atomic chat threads."""

    opord_number: int
    task_title: str

    # 1. SITUATION
    enemy_forces: str  # Blockers, technical debt
    friendly_forces: str  # Available resources
    attachments: str  # Dependencies
    civil_considerations: str  # User impact

    # 2. MISSION
    who: str  # Agent IDs
    what: str  # Specific task
    when: str  # Deadline
    where: str  # File paths
    why: str  # Business objective

    # 3. EXECUTION
    commanders_intent: str  # End state vision
    concept_of_operations: str  # High-level approach
    tasks_to_subordinates: dict[str, str]  # Squad assignments
    coordinating_instructions: dict[str, str]  # Phase lines, checkpoints

    # 4. SERVICE SUPPORT
    logistics: list[str]  # Dependencies, APIs
    personnel: list[str]  # Agent assignments
    medical: str  # Error handling, rollback

    # 5. COMMAND & SIGNAL
    command: str  # Authority chain
    signal: str  # Communication channels
    succession: list[str]  # Fallback agents

    # Metadata
    agent_id: str
    shift_number: int
    created_at: str
    updated_at: str
    status: str  # "active", "completed", "archived"
    acknowledgments: list[str]  # Agent signatures
    tags: list[str]


class AtomicChatManager:
    """
    Manages atomic chat contexts with OPORD format.

    Integrates with minion for shift-based memory isolation.
    """

    def __init__(self, db_path: str = "data/context_index.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.opord_counter = self._get_next_opord_number()

    def _init_db(self):
        """Initialize SQLite database with OPORD schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opord_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opord_number INTEGER UNIQUE NOT NULL,
                task_title TEXT NOT NULL,

                -- SITUATION
                enemy_forces TEXT,
                friendly_forces TEXT,
                attachments TEXT,
                civil_considerations TEXT,

                -- MISSION
                who TEXT,
                what TEXT,
                when_deadline TEXT,
                where_location TEXT,
                why_objective TEXT,

                -- EXECUTION
                commanders_intent TEXT,
                concept_of_operations TEXT,
                tasks_to_subordinates TEXT,  -- JSON
                coordinating_instructions TEXT,  -- JSON

                -- SERVICE SUPPORT
                logistics TEXT,  -- JSON array
                personnel TEXT,  -- JSON array
                medical TEXT,

                -- COMMAND & SIGNAL
                command TEXT,
                signal TEXT,
                succession TEXT,  -- JSON array

                -- Metadata
                agent_id TEXT,
                shift_number INTEGER,
                created_at TEXT,
                updated_at TEXT,
                status TEXT,
                acknowledgments TEXT,  -- JSON array
                tags TEXT  -- JSON array
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_id ON opord_contexts(agent_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_shift ON opord_contexts(shift_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON opord_contexts(status)
        """)

        conn.commit()
        conn.close()
        logger.info(f"Initialized OPORD context database at {self.db_path}")

    def _get_next_opord_number(self) -> int:
        """Get next OPORD number (global counter)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(opord_number) FROM opord_contexts")
        result = cursor.fetchone()[0]
        conn.close()
        return (result or 0) + 1

    def create_opord(
        self,
        task_title: str,
        agent_id: str,
        shift_number: int,
        mission: dict[str, str],
        situation: dict[str, str] | None = None,
        execution: dict[str, Any] | None = None,
        service_support: dict[str, Any] | None = None,
        command_signal: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> int:
        """
        Create new OPORD-formatted atomic chat context.

        Args:
            task_title: Brief task description
            agent_id: Primary agent ID
            shift_number: 0, 1, or 2
            mission: Dict with keys: who, what, when, where, why
            situation: Optional dict with: enemy_forces, friendly_forces, etc.
            execution: Optional dict with: commanders_intent, concept, tasks, etc.
            service_support: Optional dict with: logistics, personnel, medical
            command_signal: Optional dict with: command, signal, succession
            tags: Optional list of tags

        Returns:
            OPORD number
        """
        opord_num = self.opord_counter
        self.opord_counter += 1

        now = datetime.now(UTC).isoformat()

        # Defaults
        situation = situation or {}
        execution = execution or {}
        service_support = service_support or {}
        command_signal = command_signal or {}
        tags = tags or []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO opord_contexts (
                opord_number, task_title,
                enemy_forces, friendly_forces, attachments, civil_considerations,
                who, what, when_deadline, where_location, why_objective,
                commanders_intent, concept_of_operations,
                tasks_to_subordinates, coordinating_instructions,
                logistics, personnel, medical,
                command, signal, succession,
                agent_id, shift_number, created_at, updated_at, status,
                acknowledgments, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                opord_num,
                task_title,
                situation.get("enemy_forces", ""),
                situation.get("friendly_forces", ""),
                situation.get("attachments", ""),
                situation.get("civil_considerations", ""),
                mission.get("who", ""),
                mission.get("what", ""),
                mission.get("when", ""),
                mission.get("where", ""),
                mission.get("why", ""),
                execution.get("commanders_intent", ""),
                execution.get("concept_of_operations", ""),
                json.dumps(execution.get("tasks_to_subordinates", {})),
                json.dumps(execution.get("coordinating_instructions", {})),
                json.dumps(service_support.get("logistics", [])),
                json.dumps(service_support.get("personnel", [])),
                service_support.get("medical", ""),
                command_signal.get("command", "SwarmOrchestrator"),
                command_signal.get("signal", "Context Index"),
                json.dumps(command_signal.get("succession", [])),
                agent_id,
                shift_number,
                now,
                now,
                "active",
                json.dumps([]),  # acknowledgments
                json.dumps(tags),
            ),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"Created OPORD {opord_num:05d}: {task_title} (Agent: {agent_id}, Shift: {shift_number})"
        )
        return opord_num

    def acknowledge_opord(self, opord_number: int, agent_id: str) -> bool:
        """Agent acknowledges receipt of OPORD."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT acknowledgments FROM opord_contexts WHERE opord_number = ?", (opord_number,)
        )
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False

        acks = json.loads(result[0])
        if agent_id not in acks:
            acks.append(agent_id)
            cursor.execute(
                "UPDATE opord_contexts SET acknowledgments = ?, updated_at = ? WHERE opord_number = ?",
                (json.dumps(acks), datetime.now(UTC).isoformat(), opord_number),
            )
            conn.commit()
            logger.info(f"Agent {agent_id} acknowledged OPORD {opord_number:05d}")

        conn.close()
        return True

    def complete_opord(self, opord_number: int, summary: str, decisions: list[str]) -> bool:
        """Mark OPORD as completed with summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE opord_contexts SET status = ?, updated_at = ? WHERE opord_number = ?",
            ("completed", datetime.now(UTC).isoformat(), opord_number),
        )

        # TODO: Store summary and decisions in separate table

        conn.commit()
        conn.close()
        logger.info(f"Completed OPORD {opord_number:05d}")
        return True

    def get_shift_opords(self, shift_number: int, status: str = "active") -> list[dict]:
        """Get all OPORDs for a specific shift."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM opord_contexts WHERE shift_number = ? AND status = ? ORDER BY opord_number DESC",
            (shift_number, status),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def clear_shift_memory(self, shift_number: int) -> int:
        """Archive completed OPORDs for shift rotation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE opord_contexts SET status = ? WHERE shift_number = ? AND status = ?",
            ("archived", shift_number, "completed"),
        )

        archived_count = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Archived {archived_count} OPORDs for Shift {shift_number}")
        return archived_count

    def search_opords(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        agent_id: str | None = None,
        date_range: tuple | None = None,
    ) -> list[dict]:
        """Search OPORDs by various criteria."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM opord_contexts WHERE 1=1"
        params = []

        if query:
            sql += " AND (task_title LIKE ? OR what LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        if agent_id:
            sql += " AND agent_id = ?"
            params.append(agent_id)

        if date_range:
            sql += " AND created_at BETWEEN ? AND ?"
            params.extend(date_range)

        sql += " ORDER BY opord_number DESC LIMIT 100"

        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Filter by tags if provided
        if tags:
            results = [
                r for r in results if any(tag in json.loads(r.get("tags", "[]")) for tag in tags)
            ]

        return results
