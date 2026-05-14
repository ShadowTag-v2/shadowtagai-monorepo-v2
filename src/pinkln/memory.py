# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
LLM Memory Persistence System

Cross-device context synchronization via Git

Components:
- Conversation extraction (Cursor/Claude/Codex)
- Metadata generation (Gemini Flash 2.0)
- Git versioning (semantic versioning)
- Device sync (GCS/GitHub)

Cost: $0.45 setup + $0.02/mo
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import time


@dataclass
class Conversation:
    """Extracted conversation"""

    id: str
    timestamp: float
    messages: list[dict[str, str]]
    source: str  # cursor, claude, codex
    metadata: dict[str, Any] | None = None


@dataclass
class ConversationMetadata:
    """Gemini-generated metadata"""

    tags: list[str]
    quality_score: float  # 0.0-1.0
    difficulty: str  # beginner, intermediate, advanced
    project: str | None
    summary: str


class ConversationExtractor:
    """
    Extract conversations from IDE databases

    Supported:
    - Cursor IDE (sqlite3)
    - Claude Code history
    - VS Code Codex
    """

    def __init__(self):
        self.extractors = {
            "cursor": self._extract_cursor,
            "claude": self._extract_claude,
        }

    def extract_all(self, sources: list[str]) -> list[Conversation]:
        """
        Extract from multiple sources

        Args:
            sources: List of source types ('cursor', 'claude', etc.)

        Returns:
            List of Conversation objects
        """
        all_conversations = []

        for source in sources:
            if source in self.extractors:
                conversations = self.extractors[source]()
                all_conversations.extend(conversations)

        return all_conversations

    def _extract_cursor(self) -> list[Conversation]:
        """Extract from Cursor IDE database"""
        # Placeholder: In production, parse Cursor sqlite3 database
        # Located at: ~/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb

        return [
            Conversation(
                id=self._generate_id("cursor_example"),
                timestamp=time.time(),
                messages=[
                    {"role": "user", "content": "Implement Pinkln kernel chain"},
                    {"role": "assistant", "content": "I'll implement the kernel chain..."},
                ],
                source="cursor",
            )
        ]

    def _extract_claude(self) -> list[Conversation]:
        """Extract from Claude Code history"""
        # Placeholder: In production, parse ~/.claude-code/history

        return [
            Conversation(
                id=self._generate_id("claude_example"),
                timestamp=time.time(),
                messages=[
                    {"role": "user", "content": "Review Glicko-2 implementation"},
                    {"role": "assistant", "content": "The Glicko-2 implementation looks good..."},
                ],
                source="claude",
            )
        ]

    def _generate_id(self, content: str) -> str:
        """Generate BLAKE3 hash ID"""
        # In production: use blake3.blake3(content).hexdigest()
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class MemoryPersistence:
    """
    Git-backed memory persistence

    Workflow:
    1. Extract conversations
    2. Generate metadata (Gemini)
    3. Commit to Git with semantic versioning
    4. Sync across devices (GCS/GitHub)
    """

    def __init__(self, repo_path: Path):
        """
        Initialize memory persistence

        Args:
            repo_path: Path to Git repository
        """
        self.repo_path = repo_path
        self.memory_file = repo_path / "memory" / "conversations.json"
        self.version_file = repo_path / "memory" / "version.json"

    def save_conversations(
        self,
        conversations: list[Conversation],
        version: str = "1.0.0",
    ):
        """
        Save conversations with versioning

        Args:
            conversations: List of Conversation objects
            version: Semantic version (major.minor.patch)
        """
        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save
        data = {
            "version": version,
            "timestamp": time.time(),
            "conversations": [
                {
                    "id": conv.id,
                    "timestamp": conv.timestamp,
                    "messages": conv.messages,
                    "source": conv.source,
                    "metadata": conv.metadata,
                }
                for conv in conversations
            ],
        }

        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)

        # Update version file
        with open(self.version_file, "w") as f:
            json.dump({"version": version, "updated_at": time.time()}, f, indent=2)

    def load_conversations(self) -> list[Conversation]:
        """Load conversations from file"""
        if not self.memory_file.exists():
            return []

        with open(self.memory_file) as f:
            data = json.load(f)

        conversations = []
        for conv_data in data["conversations"]:
            conversations.append(
                Conversation(
                    id=conv_data["id"],
                    timestamp=conv_data["timestamp"],
                    messages=conv_data["messages"],
                    source=conv_data["source"],
                    metadata=conv_data.get("metadata"),
                )
            )

        return conversations

    def generate_metadata(
        self,
        conversation: Conversation,
    ) -> ConversationMetadata:
        """
        Generate metadata using Gemini Flash 2.0

        In production: Call Gemini API
        Cost: ~$0.001 per conversation

        Args:
            conversation: Conversation to analyze

        Returns:
            ConversationMetadata
        """
        # Placeholder: In production, call Gemini API

        # Extract tags from content
        content = " ".join(m["content"] for m in conversation.messages)
        tags = []

        tag_keywords = {
            "pnkln": ["kernel", "judge", "shadowtag", "jr"],
            "glicko": ["rating", "glicko", "elo"],
            "dte": ["evolution", "dte", "self-improve"],
            "memory": ["memory", "persistence", "git"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in content.lower() for kw in keywords):
                tags.append(tag)

        # Assess quality based on message length and depth
        total_chars = sum(len(m["content"]) for m in conversation.messages)
        quality_score = min(1.0, total_chars / 5000)  # Simple heuristic

        # Difficulty based on technical terms
        technical_terms = ["algorithm", "optimization", "kernel", "architecture"]
        tech_count = sum(1 for term in technical_terms if term in content.lower())
        difficulty = "beginner" if tech_count < 2 else "intermediate" if tech_count < 5 else "advanced"

        return ConversationMetadata(
            tags=tags,
            quality_score=quality_score,
            difficulty=difficulty,
            project="pnkln",
            summary=conversation.messages[0]["content"][:100] if conversation.messages else "",
        )

    def sync_to_git(self, commit_message: str):
        """
        Commit and push to Git

        In production: Execute git commands

        Args:
            commit_message: Commit message
        """
        # Placeholder: In production, use subprocess to run git commands
        # git add memory/
        # git commit -m "commit_message"
        # git push -u origin main
        pass
