"""Claude Code Memory Integration
Extracts patterns from transcript archive and persists to ~/.claude-code/memory.md

Architecture:
1. Reads transcript archive database
2. Uses Gemini Flash to extract patterns/learnings
3. Persists to ~/.claude-code/memory.md
4. Auto-syncs via GitHub for cross-device availability
"""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class ClaudeCodeMemory:
    """Memory persistence for Claude Code integration.

    Extracts learnings from consensus queries and makes them available
    to Claude Code sessions via ~/.claude-code/memory.md
    """

    def __init__(
        self,
        archive_db: str = "~/.consensus_archive.db",
        memory_file: str = "~/.claude-code/memory.md",
    ):
        self.archive_db = Path(archive_db).expanduser()
        self.memory_file = Path(memory_file).expanduser()

        # Ensure memory directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize Gemini for pattern extraction
        self.google_key = os.environ.get("GOOGLE_API_KEY")
        self.gemini_model = None

        if self.google_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.google_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
            except ImportError:
                print("[WARNING] google-generativeai not installed")

    def extract_recent_learnings(self, days: int = 7) -> list[dict]:
        """Extract recent transcripts from archive for pattern learning.

        Args:
            days: Number of days of history to analyze

        Returns:
            List of transcript dictionaries with query, result, tags

        """
        if not self.archive_db.exists():
            print(f"[WARNING] Archive database not found: {self.archive_db}")
            return []

        conn = sqlite3.connect(str(self.archive_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get transcripts from last N days
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        cursor.execute(
            """
            SELECT
                id,
                user_query,
                result,
                tags,
                timestamp,
                system_type,
                cost
            FROM transcripts
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """,
            (cutoff_str,),
        )

        transcripts = []
        for row in cursor.fetchall():
            transcripts.append(
                {
                    "id": row["id"],
                    "query": row["user_query"],
                    "result": row["result"],
                    "tags": row["tags"].split(",") if row["tags"] else [],
                    "timestamp": row["timestamp"],
                    "system_type": row["system_type"],
                    "cost": row["cost"],
                },
            )

        conn.close()
        return transcripts

    def extract_patterns_with_gemini(self, transcripts: list[dict]) -> str:
        """Use Gemini Flash to extract patterns and learnings from transcripts.

        Args:
            transcripts: List of transcript dictionaries

        Returns:
            Markdown formatted memory content

        """
        if not self.gemini_model:
            return self._fallback_pattern_extraction(transcripts)

        # Build context from recent transcripts
        context = self._build_transcript_context(transcripts)

        extraction_prompt = f"""You are analyzing a user's recent AI consensus queries to extract patterns and learnings.

RECENT QUERIES AND RESULTS:
{context}

Your task: Extract key patterns, preferences, and learnings that would be useful for future Claude Code sessions.

Generate a concise memory file with these sections:

## User Preferences
- Coding style preferences
- Tool/framework preferences
- Architecture patterns they favor

## Domain Knowledge
- Technical domains they work in
- Recurring problem types
- Key technologies used

## Patterns Observed
- Common query types
- Problem-solving approaches
- Decision-making patterns

## Context for Future Sessions
- Active projects
- Recent focus areas
- Important constraints/requirements

Keep it concise (max 500 words). Focus on actionable insights.
Format as clean Markdown."""

        try:
            response = self.gemini_model.generate_content(extraction_prompt)
            return response.text
        except Exception as e:
            print(f"[WARNING] Gemini pattern extraction failed: {e}")
            return self._fallback_pattern_extraction(transcripts)

    def _build_transcript_context(self, transcripts: list[dict], max_chars: int = 8000) -> str:
        """Build context string from transcripts (limited length)"""
        context = ""

        for t in transcripts[:20]:  # Max 20 recent
            query_summary = t["query"][:200]  # First 200 chars
            result_summary = str(t["result"])[:400]  # First 400 chars

            entry = f"""
---
Query: {query_summary}
Result: {result_summary}
Tags: {", ".join(t["tags"])}
Type: {t["system_type"]}
---
"""
            if len(context) + len(entry) > max_chars:
                break
            context += entry

        return context

    def _fallback_pattern_extraction(self, transcripts: list[dict]) -> str:
        """Fallback pattern extraction without Gemini"""
        content = "# Claude Code Memory (Auto-generated)\n\n"
        content += f"*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
        content += "## Recent Activity\n\n"
        content += f"- **Total queries**: {len(transcripts)}\n"

        # Extract common tags
        all_tags = []
        for t in transcripts:
            all_tags.extend(t.get("tags", []))

        if all_tags:
            from collections import Counter

            top_tags = Counter(all_tags).most_common(5)
            content += f"- **Common topics**: {', '.join([tag for tag, _ in top_tags])}\n"

        # Recent queries
        content += "\n## Recent Queries\n\n"
        for t in transcripts[:5]:
            content += f"- {t['query'][:100]}...\n"

        content += "\n## Notes\n\n"
        content += "*Install Gemini API for enhanced pattern extraction*\n"

        return content

    def update_memory_file(self, content: str):
        """Write memory content to ~/.claude-code/memory.md

        Args:
            content: Markdown formatted memory content

        """
        # Add metadata header
        header = f"""<!-- Auto-generated by Consensus System -->
<!-- Last Updated: {datetime.utcnow().isoformat()} -->
<!-- Source: {self.archive_db} -->

"""

        full_content = header + content

        # Write to file
        self.memory_file.write_text(full_content)
        print(f"[Memory] Updated: {self.memory_file}")
        print(f"[Memory] Size: {len(full_content)} chars")

    def sync_memory(self, days: int = 7):
        """Full sync: Extract patterns from archive and update memory file.

        Args:
            days: Number of days of history to analyze

        """
        print(f"\n{'=' * 60}")
        print("CLAUDE CODE MEMORY SYNC")
        print(f"{'=' * 60}\n")

        # Step 1: Extract recent transcripts
        print(f"[1/3] Extracting transcripts from last {days} days...")
        transcripts = self.extract_recent_learnings(days=days)
        print(f"       Found {len(transcripts)} transcripts\n")

        if not transcripts:
            print("[WARNING] No transcripts found. Run some queries first.\n")
            return

        # Step 2: Extract patterns with Gemini
        print("[2/3] Extracting patterns with Gemini Flash...")
        memory_content = self.extract_patterns_with_gemini(transcripts)
        print(f"       Extracted {len(memory_content)} chars\n")

        # Step 3: Update memory file
        print(f"[3/3] Writing to {self.memory_file}...")
        self.update_memory_file(memory_content)
        print("       ✓ Complete\n")

        print(f"{'=' * 60}")
        print("MEMORY SYNC COMPLETE")
        print(f"{'=' * 60}\n")
        print("Claude Code will auto-load this memory on next session.")
        print("To sync across devices, commit to GitHub:\n")
        print("  cd ~")
        print("  git add .claude-code/memory.md")
        print("  git commit -m 'Update Claude Code memory'")
        print("  git push\n")

    def read_memory(self) -> str | None:
        """Read current memory file content"""
        if self.memory_file.exists():
            return self.memory_file.read_text()
        return None

    def get_memory_stats(self) -> dict:
        """Get statistics about current memory file"""
        if not self.memory_file.exists():
            return {"exists": False, "size": 0, "last_updated": None}

        stat = self.memory_file.stat()
        content = self.memory_file.read_text()

        return {
            "exists": True,
            "size": len(content),
            "size_kb": stat.st_size / 1024,
            "last_updated": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "lines": len(content.splitlines()),
        }


# === CLI ===


def main():
    """CLI interface for Claude Code memory management"""
    import sys

    memory = ClaudeCodeMemory()

    if len(sys.argv) < 2:
        print("Claude Code Memory Manager")
        print("\nCommands:")
        print("  sync [days]    - Sync memory from transcript archive (default: 7 days)")
        print("  stats          - Show memory file statistics")
        print("  read           - Display current memory content")
        print("  help           - Show this help")
        return

    command = sys.argv[1].lower()

    if command == "sync":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        memory.sync_memory(days=days)

    elif command == "stats":
        stats = memory.get_memory_stats()
        print("\nMemory File Statistics:")
        print(f"  Exists: {stats['exists']}")
        if stats["exists"]:
            print(f"  Size: {stats['size']} chars ({stats['size_kb']:.2f} KB)")
            print(f"  Lines: {stats['lines']}")
            print(f"  Last Updated: {stats['last_updated']}")
        print()

    elif command == "read":
        content = memory.read_memory()
        if content:
            print("\nCurrent Memory Content:")
            print("=" * 60)
            print(content)
            print("=" * 60)
        else:
            print("\nNo memory file found. Run 'sync' first.\n")

    elif command == "help":
        print("\nClaude Code Memory Integration")
        print("=" * 60)
        print("\nThis tool extracts patterns from your consensus query archive")
        print("and creates a memory file for Claude Code to auto-load.\n")
        print("Usage:")
        print("  python claude_code_memory.py sync [days]")
        print("  python claude_code_memory.py stats")
        print("  python claude_code_memory.py read\n")
        print("Setup:")
        print("  1. Run queries with atomic_consensus_orchestrator.py")
        print("  2. Run 'python claude_code_memory.py sync'")
        print("  3. Commit ~/.claude-code/memory.md to git")
        print("  4. Claude Code will auto-load on next session\n")

    else:
        print(f"Unknown command: {command}")
        print("Run 'python claude_code_memory.py help' for usage.")


if __name__ == "__main__":
    main()
