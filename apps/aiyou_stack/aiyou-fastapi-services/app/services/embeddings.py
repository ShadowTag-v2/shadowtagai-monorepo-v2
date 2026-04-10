"""
Embeddings service for vector operations and semantic search.
"""

from typing import Any

import chromadb
import numpy as np
import structlog
from chromadb.config import Settings as ChromaSettings
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger()


class EmbeddingsService:
    """Service for generating and managing embeddings."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY, anonymized_telemetry=False
            )
        )

        logger.info(
            "Embeddings service initialized",
            model=self.model,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
        )

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            response = await self.client.embeddings.create(model=self.model, input=text)

            embedding = response.data[0].embedding

            logger.info("Embedding generated", model=self.model, dimension=len(embedding))

            return embedding
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = await self.client.embeddings.create(model=self.model, input=texts)

            embeddings = [item.embedding for item in response.data]

            logger.info("Embeddings generated", model=self.model, count=len(embeddings))

            return embeddings
        except Exception as e:
            logger.error("Embeddings generation failed", error=str(e))
            raise

    def create_collection(self, collection_name: str, metadata: dict[str, Any] | None = None):
        """Create a new vector collection."""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name, metadata=metadata or {}
            )

            logger.info("Collection created", collection_name=collection_name)
            return collection
        except Exception as e:
            logger.error("Collection creation failed", error=str(e))
            raise

    async def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadata: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ):
        """Add documents to a collection with their embeddings."""
        try:
            collection = self.chroma_client.get_or_create_collection(name=collection_name)

            # Generate embeddings
            embeddings = await self.generate_embeddings(documents)

            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadata or [{} for _ in documents],
                ids=ids,
            )

            logger.info(
                "Documents added to collection",
                collection_name=collection_name,
                count=len(documents),
            )
        except Exception as e:
            logger.error("Adding documents failed", error=str(e))
            raise

    async def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Search for similar documents in a collection."""
        try:
            collection = self.chroma_client.get_collection(name=collection_name)

            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Search
            results = collection.query(
                query_embeddings=[query_embedding], n_results=n_results, where=where
            )

            logger.info("Search completed", collection_name=collection_name, n_results=n_results)

            return results
        except Exception as e:
            logger.error("Search failed", error=str(e))
            raise

    def delete_collection(self, collection_name: str):
        """Delete a collection."""
        try:
            self.chroma_client.delete_collection(name=collection_name)
            logger.info("Collection deleted", collection_name=collection_name)
        except Exception as e:
            logger.error("Collection deletion failed", error=str(e))
            raise

    def list_collections(self) -> list[str]:
        """List all collections."""
        try:
            collections = self.chroma_client.list_collections()
            collection_names = [col.name for col in collections]

            logger.info("Collections listed", count=len(collection_names))
            return collection_names
        except Exception as e:
            logger.error("Listing collections failed", error=str(e))
            raise

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return float(dot_product / (norm_v1 * norm_v2))
