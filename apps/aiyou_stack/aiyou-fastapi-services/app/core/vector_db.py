"""Vector database wrapper using ChromaDB."""

import asyncio
from functools import partial
from typing import Any
from uuid import UUID

import chromadb
from chromadb.config import Settings

from app.config import settings as app_settings


class VectorDB:
    """ChromaDB wrapper for semantic search."""

    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path=app_settings.vector_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        self._conversations_collection = None
        self._memory_collection = None

    async def initialize(self):
        """Initialize collections."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_collections)

    def _init_collections(self):
        """Initialize collections (sync method)."""
        # Get or create conversations collection
        self._conversations_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Conversation messages for semantic search"},
        )

        # Get or create memory collection
        self._memory_collection = self.client.get_or_create_collection(
            name="memory",
            metadata={"description": "Memory entries for context retrieval"},
        )

    @property
    def conversations(self):
        """Get conversations collection."""
        if not self._conversations_collection:
            raise RuntimeError("VectorDB not initialized. Call initialize() first.")
        return self._conversations_collection

    @property
    def memory(self):
        """Get memory collection."""
        if not self._memory_collection:
            raise RuntimeError("VectorDB not initialized. Call initialize() first.")
        return self._memory_collection

    async def add_message(
        self,
        message_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        """Add a message to the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(
                self.conversations.add,
                ids=[message_id],
                documents=[content],
                metadatas=[metadata],
            ),
        )

    async def add_messages_bulk(
        self,
        message_ids: list[str],
        contents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Add multiple messages to the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(
                self.conversations.add,
                ids=message_ids,
                documents=contents,
                metadatas=metadatas,
            ),
        )

    async def search_conversations(
        self,
        query: str,
        project_id: UUID | None = None,
        top_k: int = 5,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search conversations semantically."""
        loop = asyncio.get_event_loop()

        # Build where filter
        where = {}
        if project_id:
            where["project_id"] = str(project_id)

        # Perform search
        results = await loop.run_in_executor(
            None,
            partial(
                self.conversations.query,
                query_texts=[query],
                n_results=top_k,
                where=where if where else None,
            ),
        )

        # Format results
        formatted_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, message_id in enumerate(results["ids"][0]):
                score = 1.0 - results["distances"][0][i]  # Convert distance to similarity
                if min_score and score < min_score:
                    continue

                formatted_results.append(
                    {
                        "id": message_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": score,
                    }
                )

        return formatted_results

    async def add_memory_entry(
        self,
        memory_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        """Add a memory entry to the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(
                self.memory.add,
                ids=[memory_id],
                documents=[content],
                metadatas=[metadata],
            ),
        )

    async def search_memory(
        self,
        query: str,
        project_id: UUID | None = None,
        category: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search memory entries semantically."""
        loop = asyncio.get_event_loop()

        # Build where filter
        where = {"active": True}
        if project_id:
            where["project_id"] = str(project_id)
        if category:
            where["category"] = category

        # Perform search
        results = await loop.run_in_executor(
            None,
            partial(
                self.memory.query,
                query_texts=[query],
                n_results=top_k,
                where=where,
            ),
        )

        # Format results
        formatted_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, memory_id in enumerate(results["ids"][0]):
                score = 1.0 - results["distances"][0][i]

                formatted_results.append(
                    {
                        "id": memory_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": score,
                    }
                )

        return formatted_results

    async def delete_message(self, message_id: str) -> None:
        """Delete a message from the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(self.conversations.delete, ids=[message_id]),
        )

    async def delete_memory_entry(self, memory_id: str) -> None:
        """Delete a memory entry from the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(self.memory.delete, ids=[memory_id]),
        )

    async def update_memory_entry(
        self,
        memory_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        """Update a memory entry in the vector database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(
                self.memory.update,
                ids=[memory_id],
                documents=[content],
                metadatas=[metadata],
            ),
        )


# Global vector database instance
vector_db = VectorDB()
