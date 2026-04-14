"""LLM Memory Persistence System

Cross-device context synchronization via Git

Components:
- Conversation extraction (Cursor/Claude/Codex)
- Metadata generation (Gemini Flash 2.0)
- Git versioning (semantic versioning)
- Device sync (GCS/GitHub)

Cost: $0.45 setup + $0.02/mo
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ConversationContext:
    id: str
    summary: str
    timestamp: float
    platform: str


class MemoryPersistence:
    """Git-backed cross-device memory (Local JSON implementation)"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.memory_file = f"{repo_path}/memory.json"
        self._ensure_repo()

    def _ensure_repo(self):
        import os

        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path, exist_ok=True)

    def load_context(self, limit: int = 5) -> list[ConversationContext]:
        """Load recent context items"""
        import json
        import os

        if not os.path.exists(self.memory_file):
            return []

        try:
            with open(self.memory_file) as f:
                data = json.load(f)
                # Parse back into objects
                items = [ConversationContext(**item) for item in data]
                # Return most recent first
                items.sort(key=lambda x: x.timestamp, reverse=True)
                return items[:limit]
        except Exception as e:
            print(f"Error loading memory: {e}")
            return []

    def save_context(self, context: ConversationContext):
        """Save context to local JSON (append)"""
        import json
        import os
        from dataclasses import asdict

        current_data = []
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file) as f:
                    current_data = json.load(f)
            except Exception:
                current_data = []

        # Append new context
        current_data.append(asdict(context))

        # Write back
        with open(self.memory_file, "w") as f:
            json.dump(current_data, f, indent=2)

    def sync(self):
        # Git pull/push logic (Stub for now)
        pass


class ConversationExtractor:
    """Extracts from various platforms"""

    def extract_cursor(self, db_path: str) -> list[dict[str, Any]]:
        return []

    def extract_claude(self, json_path: str) -> list[dict[str, Any]]:
        """Extract conversations from Claude JSON export"""
        import json
        import os

        if not os.path.exists(json_path):
            return []

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle various formats (list of convos, or dict with 'sources')
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # Try to find a list in common keys
                for key in ["conversations", "chat_history", "sources"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # If specific 'sources' structure from extraction script
                if "sources" in data and isinstance(data["sources"], dict):
                    # Combine all sources
                    all_items = []
                    for _source, content in data["sources"].items():
                        if isinstance(content, dict) and "data" in content:
                            if isinstance(content["data"], list):
                                all_items.extend(content["data"])
                            elif isinstance(content["data"], dict):
                                all_items.extend(content["data"].values())
                    return all_items

            return []
        except Exception as e:
            print(f"Error extracting Claude JSON: {e}")
            return []
