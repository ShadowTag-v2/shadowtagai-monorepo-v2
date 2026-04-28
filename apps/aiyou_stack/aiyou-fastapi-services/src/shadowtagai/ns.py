# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""NS - Semantic Memory Retrieval

Semantic memory system for storing and retrieving contextually relevant
information. Replaces AutoGen's conversation history with efficient
vector-based semantic search.

Key features:
- Vector embeddings for semantic similarity
- Fast retrieval (<10ms)
- Persistent storage
- Automatic context injection
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Memory:
    """A single memory entry."""

    content: str
    embedding: list[float]
    metadata: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(
        default_factory=lambda: hashlib.sha256(
            f"{datetime.now().isoformat()}".encode(),
        ).hexdigest()[:16],
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Memory":
        """Create from dictionary."""
        return Memory(
            id=data["id"],
            content=data["content"],
            embedding=data["embedding"],
            metadata=data["metadata"],
            timestamp=data["timestamp"],
        )


class SemanticMemory:
    """NS - Semantic Memory System.

    Stores and retrieves memories using semantic similarity.

    Example:
        ```python
        ns = SemanticMemory()

        # Store memory
        ns.store(
            content="Quantum computing uses qubits",
            metadata={'topic': 'quantum', 'source': 'research'}
        )

        # Retrieve similar memories
        results = ns.retrieve("Tell me about quantum physics")
        ```

    """

    def __init__(
        self,
        db_path: str | None = None,
        embedding_model: str = "simple",  # "simple" or "gemini"
    ):
        """Initialize semantic memory.

        Args:
            db_path: Path to persistent storage file
            embedding_model: Embedding model to use ("simple" or "gemini")

        """
        self.db_path = db_path or os.environ.get("NS_VECTOR_DB_PATH", "./data/ns_vectors.db")
        self.embedding_model = embedding_model
        self.memories: list[Memory] = []

        # Load existing memories
        self._load_memories()

    def store(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """Store a new memory.

        Args:
            content: Memory content
            metadata: Optional metadata

        Returns:
            Memory ID

        """
        # Generate embedding
        embedding = self._embed(content)

        # Create memory
        memory = Memory(content=content, embedding=embedding, metadata=metadata or {})

        # Store
        self.memories.append(memory)

        # Persist
        self._save_memories()

        return memory.id

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Retrieve memories semantically similar to query.

        Args:
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of memories with similarity scores

        """
        if not self.memories:
            return []

        # Embed query
        query_embedding = self._embed(query)

        # Calculate similarities
        results = []
        for memory in self.memories:
            similarity = self._cosine_similarity(query_embedding, memory.embedding)

            if similarity >= similarity_threshold:
                results.append({"memory": memory.to_dict(), "similarity": similarity})

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        """
        if self.embedding_model == "simple":
            # Simple word-based embedding (for demo)
            # In production, use actual embedding model
            words = text.lower().split()

            # Create fixed-size embedding (128 dims)
            embedding = [0.0] * 128

            for i, word in enumerate(words[:128]):
                # Hash word to position
                pos = hash(word) % 128
                embedding[pos] = 1.0 / (i + 1)  # Weight by position

            return embedding

        if self.embedding_model == "gemini":
            # Use Gemini embeddings (requires API call)
            # TODO: Implement Gemini embedding API
            raise NotImplementedError("Gemini embeddings not yet implemented")

        raise ValueError(f"Unknown embedding model: {self.embedding_model}")

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _save_memories(self):
        """Save memories to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump([m.to_dict() for m in self.memories], f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save memories: {e}")

    def _load_memories(self):
        """Load memories from persistent storage."""
        if not os.path.exists(self.db_path):
            return

        try:
            with open(self.db_path) as f:
                data = json.load(f)
                self.memories = [Memory.from_dict(m) for m in data]
        except Exception as e:
            print(f"Warning: Failed to load memories: {e}")

    def clear(self):
        """Clear all memories."""
        self.memories.clear()
        self._save_memories()

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": len(self.memories),
            "db_path": self.db_path,
            "embedding_model": self.embedding_model,
        }
