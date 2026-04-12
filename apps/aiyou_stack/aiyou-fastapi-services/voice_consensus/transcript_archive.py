"""
Transcript Archive System
Persistent storage and indexing for all consensus queries/responses

Solves: GPT's memory fragmentation problem
- Archives every query and result
- Full-text search across all history
- Export/recovery tools
- Never lose work again
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class TranscriptArchive:
    """
    Persistent archive for consensus transcripts with full-text search.

    Features:
    - SQLite storage (local, portable, no cloud dependencies)
    - Full-text search (FTS5)
    - Tag system for organization
    - Export to JSON/Markdown
    - Conversation threading
    """

    def __init__(self, db_path: str = "~/.consensus_archive.db"):
        """Initialize archive database"""
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows

        self._initialize_database()

    def _initialize_database(self):
        """Create tables with full-text search"""
        cursor = self.conn.cursor()

        # Main transcripts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                final_output TEXT NOT NULL,
                system_type TEXT NOT NULL,  -- 'atomic', 'simple', 'message'

                -- Metadata
                thread_count INTEGER DEFAULT 0,
                models_consulted INTEGER DEFAULT 0,
                peer_reviews_conducted INTEGER DEFAULT 0,
                execution_time_seconds REAL DEFAULT 0,
                success_rate REAL DEFAULT 1.0,

                -- Raw data (JSON)
                full_result_json TEXT NOT NULL,

                -- Tags and notes
                tags TEXT DEFAULT '',
                notes TEXT DEFAULT '',

                -- Session tracking
                session_id TEXT,
                conversation_thread_id TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Full-text search virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
                user_query,
                final_output,
                tags,
                notes,
                content='transcripts',
                content_rowid='id'
            )
        """)

        # Triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcripts_ai AFTER INSERT ON transcripts BEGIN
                INSERT INTO transcripts_fts(rowid, user_query, final_output, tags, notes)
                VALUES (new.id, new.user_query, new.final_output, new.tags, new.notes);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcripts_ad AFTER DELETE ON transcripts BEGIN
                INSERT INTO transcripts_fts(transcripts_fts, rowid, user_query, final_output, tags, notes)
                VALUES('delete', old.id, old.user_query, old.final_output, old.tags, old.notes);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcripts_au AFTER UPDATE ON transcripts BEGIN
                INSERT INTO transcripts_fts(transcripts_fts, rowid, user_query, final_output, tags, notes)
                VALUES('delete', old.id, old.user_query, old.final_output, old.tags, old.notes);
                INSERT INTO transcripts_fts(rowid, user_query, final_output, tags, notes)
                VALUES (new.id, new.user_query, new.final_output, new.tags, new.notes);
            END
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON transcripts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON transcripts(session_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_thread ON transcripts(conversation_thread_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON transcripts(tags)")

        self.conn.commit()

    def archive(
        self,
        user_query: str,
        result: dict[str, Any],
        system_type: str = "simple",
        tags: list[str] = None,
        notes: str = "",
        session_id: str = None,
        conversation_thread_id: str = None,
    ) -> int:
        """
        Archive a consensus result.

        Args:
            user_query: Original user query
            result: Full result dict from orchestrator
            system_type: 'atomic', 'simple', or 'message'
            tags: List of tags for organization
            notes: Optional notes
            session_id: Optional session identifier
            conversation_thread_id: Optional thread for linking related queries

        Returns:
            Database row ID
        """
        cursor = self.conn.cursor()

        # Generate unique hash for query
        query_hash = hashlib.sha256(
            f"{user_query}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Extract metadata from result
        final_output = result.get("final_output", result.get("final_synthesis", ""))

        summary = result.get("execution_summary", {})
        thread_count = summary.get("total_threads", 0)
        models_consulted = summary.get(
            "total_models_consulted", len(result.get("layer2_responses", [])) + 2
        )
        peer_reviews = summary.get("total_peer_reviews", len(result.get("peer_reviews", [])))
        exec_time = summary.get("avg_execution_time", 0)
        success_rate = summary.get("success_rate", 1.0)

        # Prepare tags
        tags_str = ",".join(tags) if tags else ""

        # Insert
        cursor.execute(
            """
            INSERT INTO transcripts (
                query_hash, timestamp, user_query, final_output, system_type,
                thread_count, models_consulted, peer_reviews_conducted,
                execution_time_seconds, success_rate,
                full_result_json, tags, notes, session_id, conversation_thread_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                query_hash,
                datetime.utcnow().isoformat(),
                user_query,
                final_output,
                system_type,
                thread_count,
                models_consulted,
                peer_reviews,
                exec_time,
                success_rate,
                json.dumps(result),
                tags_str,
                notes,
                session_id,
                conversation_thread_id,
            ),
        )

        self.conn.commit()
        return cursor.lastrowid

    def search(
        self,
        query: str,
        limit: int = 20,
        tags: list[str] = None,
        system_type: str = None,
        date_from: str = None,
        date_to: str = None,
    ) -> list[dict[str, Any]]:
        """
        Full-text search across all transcripts.

        Args:
            query: Search query (supports SQLite FTS5 syntax)
            limit: Max results to return
            tags: Filter by tags
            system_type: Filter by system type
            date_from: ISO date string (e.g., '2025-01-01')
            date_to: ISO date string

        Returns:
            List of matching transcripts
        """
        cursor = self.conn.cursor()

        # Build WHERE clause
        where_clauses = []
        params = []

        if query:
            # Use FTS for search
            where_clauses.append(
                "id IN (SELECT rowid FROM transcripts_fts WHERE transcripts_fts MATCH ?)"
            )
            params.append(query)

        if tags:
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            where_clauses.append(f"({tag_conditions})")
            params.extend([f"%{tag}%" for tag in tags])

        if system_type:
            where_clauses.append("system_type = ?")
            params.append(system_type)

        if date_from:
            where_clauses.append("timestamp >= ?")
            params.append(date_from)

        if date_to:
            where_clauses.append("timestamp <= ?")
            params.append(date_to)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        sql = f"""
            SELECT
                id, query_hash, timestamp, user_query, final_output,
                system_type, thread_count, models_consulted, peer_reviews_conducted,
                execution_time_seconds, success_rate, tags, notes,
                session_id, conversation_thread_id
            FROM transcripts
            WHERE {where_sql}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)

        cursor.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            results.append(dict(row))

        return results

    def get_by_id(self, transcript_id: int) -> dict[str, Any] | None:
        """Get full transcript by ID including raw JSON"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transcripts WHERE id = ?
        """,
            (transcript_id,),
        )

        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["full_result"] = json.loads(result["full_result_json"])
            return result
        return None

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent transcripts"""
        return self.search(query=None, limit=limit)

    def get_by_thread(self, conversation_thread_id: str) -> list[dict[str, Any]]:
        """Get all transcripts in a conversation thread"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transcripts
            WHERE conversation_thread_id = ?
            ORDER BY timestamp ASC
        """,
            (conversation_thread_id,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        return results

    def add_tags(self, transcript_id: int, tags: list[str]):
        """Add tags to existing transcript"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT tags FROM transcripts WHERE id = ?", (transcript_id,))
        row = cursor.fetchone()

        if row:
            existing_tags = set(row["tags"].split(",")) if row["tags"] else set()
            existing_tags.update(tags)
            new_tags = ",".join(sorted(existing_tags))

            cursor.execute(
                """
                UPDATE transcripts SET tags = ? WHERE id = ?
            """,
                (new_tags, transcript_id),
            )
            self.conn.commit()

    def add_note(self, transcript_id: int, note: str):
        """Add note to transcript"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE transcripts
            SET notes = CASE
                WHEN notes = '' THEN ?
                ELSE notes || '\n\n' || ?
            END
            WHERE id = ?
        """,
            (note, note, transcript_id),
        )
        self.conn.commit()

    def export_to_json(self, output_file: str, transcript_ids: list[int] = None):
        """Export transcripts to JSON file"""
        cursor = self.conn.cursor()

        if transcript_ids:
            placeholders = ",".join("?" * len(transcript_ids))
            cursor.execute(
                f"""
                SELECT * FROM transcripts WHERE id IN ({placeholders})
                ORDER BY timestamp ASC
            """,
                transcript_ids,
            )
        else:
            cursor.execute("SELECT * FROM transcripts ORDER BY timestamp ASC")

        transcripts = []
        for row in cursor.fetchall():
            transcript = dict(row)
            transcript["full_result"] = json.loads(transcript["full_result_json"])
            del transcript["full_result_json"]
            transcripts.append(transcript)

        with open(output_file, "w") as f:
            json.dump(transcripts, f, indent=2)

        return len(transcripts)

    def export_to_markdown(self, output_file: str, transcript_ids: list[int] = None):
        """Export transcripts to Markdown file"""
        cursor = self.conn.cursor()

        if transcript_ids:
            placeholders = ",".join("?" * len(transcript_ids))
            cursor.execute(
                f"""
                SELECT * FROM transcripts WHERE id IN ({placeholders})
                ORDER BY timestamp ASC
            """,
                transcript_ids,
            )
        else:
            cursor.execute("SELECT * FROM transcripts ORDER BY timestamp ASC")

        with open(output_file, "w") as f:
            f.write("# Consensus Transcript Archive\n\n")

            for row in cursor.fetchall():
                transcript = dict(row)
                f.write(f"## Query #{transcript['id']} - {transcript['timestamp']}\n\n")
                f.write(f"**System:** {transcript['system_type']}\n\n")

                if transcript["tags"]:
                    f.write(f"**Tags:** {transcript['tags']}\n\n")

                f.write(f"### User Query\n\n{transcript['user_query']}\n\n")
                f.write(f"### Final Output\n\n{transcript['final_output']}\n\n")

                f.write("**Metadata:**\n")
                f.write(f"- Threads: {transcript['thread_count']}\n")
                f.write(f"- Models: {transcript['models_consulted']}\n")
                f.write(f"- Peer Reviews: {transcript['peer_reviews_conducted']}\n")
                f.write(f"- Execution Time: {transcript['execution_time_seconds']:.2f}s\n")
                f.write(f"- Success Rate: {transcript['success_rate'] * 100:.0f}%\n\n")

                if transcript["notes"]:
                    f.write(f"**Notes:**\n{transcript['notes']}\n\n")

                f.write("---\n\n")

    def get_stats(self) -> dict[str, Any]:
        """Get archive statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM transcripts")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT system_type, COUNT(*) as count FROM transcripts GROUP BY system_type"
        )
        by_system = {row["system_type"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("SELECT AVG(models_consulted) as avg_models FROM transcripts")
        avg_models = cursor.fetchone()["avg_models"] or 0

        cursor.execute("SELECT AVG(peer_reviews_conducted) as avg_reviews FROM transcripts")
        avg_reviews = cursor.fetchone()["avg_reviews"] or 0

        cursor.execute("SELECT SUM(execution_time_seconds) as total_time FROM transcripts")
        total_time = cursor.fetchone()["total_time"] or 0

        return {
            "total_transcripts": total,
            "by_system_type": by_system,
            "avg_models_per_query": avg_models,
            "avg_peer_reviews_per_query": avg_reviews,
            "total_execution_time_hours": total_time / 3600,
            "database_path": str(self.db_path),
            "database_size_mb": self.db_path.stat().st_size / 1024 / 1024
            if self.db_path.exists()
            else 0,
        }

    def close(self):
        """Close database connection"""
        self.conn.close()


# === CLI for archive management ===


def main():
    """CLI for searching and managing transcript archive"""
    import argparse

    parser = argparse.ArgumentParser(description="Consensus Transcript Archive")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search
    search_parser = subparsers.add_parser("search", help="Search transcripts")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    search_parser.add_argument(
        "--type", choices=["atomic", "simple", "message"], help="System type"
    )

    # Recent
    recent_parser = subparsers.add_parser("recent", help="Show recent transcripts")
    recent_parser.add_argument("--limit", type=int, default=10, help="Number to show")

    # Show
    show_parser = subparsers.add_parser("show", help="Show full transcript")
    show_parser.add_argument("id", type=int, help="Transcript ID")

    # Export
    export_parser = subparsers.add_parser("export", help="Export transcripts")
    export_parser.add_argument("output", help="Output file (.json or .md)")
    export_parser.add_argument("--ids", type=int, nargs="+", help="Specific IDs to export")

    # Stats
    subparsers.add_parser("stats", help="Show archive statistics")

    # Tag
    tag_parser = subparsers.add_parser("tag", help="Add tags to transcript")
    tag_parser.add_argument("id", type=int, help="Transcript ID")
    tag_parser.add_argument("tags", nargs="+", help="Tags to add")

    args = parser.parse_args()

    archive = TranscriptArchive()

    if args.command == "search":
        results = archive.search(
            query=args.query, limit=args.limit, tags=args.tags, system_type=args.type
        )

        print(f"\nFound {len(results)} results:\n")
        for r in results:
            print(f"[{r['id']}] {r['timestamp']} - {r['system_type']}")
            print(f"Q: {r['user_query'][:100]}...")
            print(f"Tags: {r['tags']}")
            print()

    elif args.command == "recent":
        results = archive.get_recent(limit=args.limit)

        print("\nRecent transcripts:\n")
        for r in results:
            print(f"[{r['id']}] {r['timestamp']} - {r['system_type']}")
            print(f"Q: {r['user_query'][:100]}...")
            print()

    elif args.command == "show":
        transcript = archive.get_by_id(args.id)

        if transcript:
            print(f"\n{'=' * 80}")
            print(f"Transcript #{transcript['id']} - {transcript['timestamp']}")
            print(f"{'=' * 80}\n")
            print(f"System: {transcript['system_type']}")
            print(f"Tags: {transcript['tags']}")
            print(f"\nQuery:\n{transcript['user_query']}\n")
            print(f"Final Output:\n{transcript['final_output']}\n")
            print("Metadata:")
            print(f"  Threads: {transcript['thread_count']}")
            print(f"  Models: {transcript['models_consulted']}")
            print(f"  Reviews: {transcript['peer_reviews_conducted']}")
            print(f"  Time: {transcript['execution_time_seconds']:.2f}s")
        else:
            print(f"Transcript {args.id} not found")

    elif args.command == "export":
        if args.output.endswith(".json"):
            count = archive.export_to_json(args.output, args.ids)
        elif args.output.endswith(".md"):
            archive.export_to_markdown(args.output, args.ids)
            count = len(args.ids) if args.ids else archive.get_stats()["total_transcripts"]
        else:
            print("Output file must be .json or .md")
            return

        print(f"Exported {count} transcripts to {args.output}")

    elif args.command == "stats":
        stats = archive.get_stats()

        print(f"\n{'=' * 80}")
        print("Archive Statistics")
        print(f"{'=' * 80}\n")
        print(f"Total Transcripts: {stats['total_transcripts']}")
        print(f"By System Type: {stats['by_system_type']}")
        print(f"Avg Models/Query: {stats['avg_models_per_query']:.1f}")
        print(f"Avg Reviews/Query: {stats['avg_peer_reviews_per_query']:.1f}")
        print(f"Total Execution Time: {stats['total_execution_time_hours']:.2f} hours")
        print(f"Database Size: {stats['database_size_mb']:.2f} MB")
        print(f"Database Path: {stats['database_path']}")
        print()

    elif args.command == "tag":
        archive.add_tags(args.id, args.tags)
        print(f"Added tags to transcript {args.id}: {', '.join(args.tags)}")

    else:
        parser.print_help()

    archive.close()


if __name__ == "__main__":
    main()
