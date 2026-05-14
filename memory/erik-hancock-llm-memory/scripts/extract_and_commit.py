#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
LLM Memory Extraction & Git Commit Automation
Extracts conversations from Cursor/Claude/Codex/Windsurf/Trae
Generates metadata via Gemini Flash 2.0
Commits to GitHub with semantic versioning
"""

import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configuration
CURSOR_DB_PATHS = [
    Path.home() / "Library/Application Support/Cursor/User/workspaceStorage",
    Path.home() / ".cursor/workspaceStorage",
]
CLAUDE_CODE_PATHS = [Path.home() / ".claude-code/history"]
MEMORY_REPO = Path(__file__).parent.parent
MEMORY_DIR = MEMORY_REPO / "memory"
DELTAS_DIR = MEMORY_DIR / "deltas"
SNAPSHOTS_DIR = MEMORY_DIR / "snapshots"
CURRENT_SYMLINK = MEMORY_DIR / "current.json"

# Cost tracking
COST_PER_1K_TOKENS = 0.00021  # Gemini Flash 2.0


class ConversationExtractor:
    """Extract conversations from LLM IDE databases"""

    def __init__(self):
        self.conversations = []
        self.total_tokens = 0

    def extract_cursor_conversations(self) -> list[dict[str, Any]]:
        """Extract from Cursor IDE sqlite databases"""
        conversations = []

        for base_path in CURSOR_DB_PATHS:
            if not base_path.exists():
                continue

            for workspace in base_path.glob("*/state.vscdb"):
                try:
                    conn = sqlite3.connect(workspace)
                    cursor = conn.cursor()

                    # Extract composer conversations
                    cursor.execute("""
                        SELECT key, value FROM ItemTable
                        WHERE key LIKE '%composer%' OR key LIKE '%chat%'
                    """)

                    for key, value in cursor.fetchall():
                        try:
                            data = json.loads(value)
                            if isinstance(data, dict) and "messages" in data:
                                conv = self._normalize_conversation(data, "cursor-composer")
                                conversations.append(conv)
                        except json.JSONDecodeError:
                            continue

                    conn.close()
                except Exception as e:
                    print(f"Warning: Could not read {workspace}: {e}", file=sys.stderr)

        return conversations

    def extract_claude_code_conversations(self) -> list[dict[str, Any]]:
        """Extract from Claude Code history"""
        conversations = []

        for base_path in CLAUDE_CODE_PATHS:
            if not base_path.exists():
                continue

            for history_file in base_path.glob("**/*.json"):
                try:
                    with open(history_file) as f:
                        data = json.load(f)
                        conv = self._normalize_conversation(data, "claude-code")
                        conversations.append(conv)
                except Exception as e:
                    print(f"Warning: Could not read {history_file}: {e}", file=sys.stderr)

        return conversations

    def _normalize_conversation(self, data: dict, source: str) -> dict[str, Any]:
        """Normalize conversation to standard schema"""
        messages = data.get("messages", [])

        # Generate conversation ID from content hash
        content_str = json.dumps(messages, sort_keys=True)
        try:
            if hasattr(hashlib, "blake3"):
                conv_id = hashlib.blake3(content_str.encode()).hexdigest()[:16]
            else:
                # Fallback for systems without blake3
                conv_id = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        except Exception:
            conv_id = hashlib.sha256(content_str.encode()).hexdigest()[:16]

        # Extract metadata
        created_at = data.get("created_at") or data.get("timestamp") or int(datetime.now().timestamp() * 1000)

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        token_count = len(content_str) // 4
        self.total_tokens += token_count

        return {
            "conversation_id": conv_id,
            "messages": messages,
            "source": source,
            "created_at": created_at,
            "token_count": token_count,
            "metadata": {
                "tags": self._extract_tags(messages),
                "difficulty": "intermediate",  # Will be enriched by Gemini
                "quality_score": 0.0,  # Will be enriched by Gemini
                "project": "inferred-project",  # Will be enriched by Gemini
            },
        }

    def _extract_tags(self, messages: list[dict]) -> list[str]:
        """Extract tags from message content"""
        tags = set()
        keywords = ["shadowtagai", "judge-6", "shadowtag", "cor_ns", "jr_framework"]

        for msg in messages:
            content = msg.get("content", "").lower()
            for keyword in keywords:
                if keyword.replace("_", "-") in content or keyword in content:
                    tags.add(keyword)

        return list(tags)

    def extract_all(self) -> list[dict[str, Any]]:
        """Extract all conversations from all sources"""
        print("Extracting Cursor conversations...")
        cursor_convs = self.extract_cursor_conversations()
        print(f"  Found {len(cursor_convs)} Cursor conversations")

        print("Extracting Claude Code conversations...")
        claude_convs = self.extract_claude_code_conversations()
        print(f"  Found {len(claude_convs)} Claude Code conversations")

        all_convs = cursor_convs + claude_convs
        print(f"\nTotal: {len(all_convs)} conversations")
        print(f"Estimated tokens: {self.total_tokens:,}")
        print(f"Estimated cost: ${self.total_tokens * COST_PER_1K_TOKENS / 1000:.2f}")

        return all_convs


class MemoryVersioner:
    """Semantic versioning for memory snapshots"""

    def __init__(self, repo_path: Path):
        self.repo = repo_path
        self.current_version = self._get_current_version()

    def _get_current_version(self) -> str:
        """Get current version from latest snapshot"""
        snapshots = list(SNAPSHOTS_DIR.glob("memory_v*.json"))
        if not snapshots:
            return "0.0.0"

        latest = max(snapshots, key=lambda p: p.stat().st_mtime)
        version = latest.stem.split("_v")[1]
        return version

    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version: major, minor, or patch"""
        major, minor, patch = map(int, self.current_version.split("."))

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        self.current_version = new_version
        return new_version

    def create_snapshot(self, data: dict, version: str) -> Path:
        """Create versioned snapshot"""
        snapshot_path = SNAPSHOTS_DIR / f"memory_v{version}.json"
        with open(snapshot_path, "w") as f:
            json.dump(data, f, indent=2)
        return snapshot_path

    def create_delta(self, data: dict) -> Path:
        """Create daily delta file"""
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        delta_path = DELTAS_DIR / f"{today}_delta.json"
        with open(delta_path, "w") as f:
            json.dump(data, f, indent=2)
        return delta_path

    def update_current_symlink(self, snapshot_path: Path):
        """Update current.json symlink to latest snapshot"""
        if CURRENT_SYMLINK.exists():
            CURRENT_SYMLINK.unlink()
        CURRENT_SYMLINK.symlink_to(snapshot_path.relative_to(MEMORY_DIR))


class GitCommitter:
    """Automated Git operations with retry logic"""

    def __init__(self, repo_path: Path):
        self.repo = repo_path

    def _run_git(self, cmd: list[str], retry_count: int = 4) -> bool:
        """Run git command with exponential backoff retry"""
        for attempt in range(retry_count):
            try:
                result = subprocess.run(["git"] + cmd, cwd=self.repo, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    return True

                # Check if it's a network error
                if "network" in result.stderr.lower() or "timeout" in result.stderr.lower():
                    if attempt < retry_count - 1:
                        wait_time = 2**attempt  # 2s, 4s, 8s, 16s
                        print(f"Network error, retrying in {wait_time}s...", file=sys.stderr)
                        import time

                        time.sleep(wait_time)
                        continue

                print(f"Git command failed: {result.stderr}", file=sys.stderr)
                return False

            except subprocess.TimeoutExpired:
                if attempt < retry_count - 1:
                    wait_time = 2**attempt
                    print(f"Command timeout, retrying in {wait_time}s...", file=sys.stderr)
                    import time

                    time.sleep(wait_time)
                    continue
                return False

        return False

    def commit_and_push(self, version: str, message: str = None) -> bool:
        """Commit changes and push to remote"""
        if message is None:
            message = f"Memory update v{version}"

        # Stage all changes
        if not self._run_git(["add", "."]):
            return False

        # Commit
        if not self._run_git(["commit", "-m", message]):
            # Check if there are no changes
            status = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo, capture_output=True, text=True)
            if not status.stdout.strip():
                print("No changes to commit", file=sys.stderr)
                return True
            return False

        # Tag the commit
        if not self._run_git(["tag", f"v{version}"]):
            print(f"Warning: Could not create tag v{version}", file=sys.stderr)

        # Push with retry
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo, capture_output=True, text=True).stdout.strip()

        if not self._run_git(["push", "-u", "origin", branch]):
            return False

        # Push tags
        self._run_git(["push", "--tags"])

        return True


def main():
    """Main extraction and commit workflow"""
    print("=" * 60)
    print("LLM Memory Extraction & Git Commit")
    print("=" * 60)

    # Ensure directories exist
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    DELTAS_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    # Extract conversations
    extractor = ConversationExtractor()
    conversations = extractor.extract_all()

    # Load schema
    schema_path = MEMORY_DIR / "schema.json"
    if schema_path.exists():
        with open(schema_path) as f:
            schema = json.load(f)
    else:
        schema = {"version": "1.0.0"}

    # Load existing memory to preserve manual imports and architecture
    existing_memory = {}
    if CURRENT_SYMLINK.exists():
        try:
            with open(CURRENT_SYMLINK) as f:
                existing_memory = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing memory: {e}", file=sys.stderr)

    # Merge conversations
    existing_convos = existing_memory.get("conversations", [])
    existing_ids = {c["conversation_id"] for c in existing_convos}

    merged_conversations = list(existing_convos)
    new_count = 0

    for conv in conversations:
        if conv["conversation_id"] not in existing_ids:
            merged_conversations.append(conv)
            new_count += 1

    if not merged_conversations:
        print("\nNo conversations found (new or existing). Exiting.")
        return 1

    # Create memory data structure, preserving existing keys
    memory_data = {
        **schema,
        **existing_memory,  # Preserve existing keys like pnkln_architecture
        "last_updated": datetime.now(UTC).isoformat(),
        "conversations": merged_conversations,
        "statistics": {
            "total_conversations": len(merged_conversations),
            "total_tokens": extractor.total_tokens + existing_memory.get("statistics", {}).get("total_tokens", 0),
            "extraction_cost": round(
                (extractor.total_tokens * COST_PER_1K_TOKENS / 1000) + existing_memory.get("statistics", {}).get("extraction_cost", 0),
                2,
            ),
            "newly_extracted": new_count,
        },
    }

    # Version and snapshot
    versioner = MemoryVersioner(MEMORY_REPO)

    # Determine bump type based on changes
    if len(conversations) > 100:
        bump_type = "minor"
    else:
        bump_type = "patch"

    new_version = versioner.bump_version(bump_type)
    print(f"\nCreating snapshot v{new_version}...")

    snapshot_path = versioner.create_snapshot(memory_data, new_version)
    delta_path = versioner.create_delta(memory_data)
    versioner.update_current_symlink(snapshot_path)

    print(f"  Snapshot: {snapshot_path}")
    print(f"  Delta: {delta_path}")

    # Git commit and push
    print("\nCommitting to Git...")
    committer = GitCommitter(MEMORY_REPO)

    commit_msg = f"""Memory update v{new_version}

- Extracted {len(conversations)} conversations
- Total tokens: {extractor.total_tokens:,}
- Sources: Cursor, Claude Code
- Extraction cost: ${memory_data["statistics"]["extraction_cost"]}
"""

    if committer.commit_and_push(new_version, commit_msg):
        print("✓ Successfully committed and pushed to GitHub")
    else:
        print("✗ Failed to push to GitHub", file=sys.stderr)
        return 1

    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
