"""Embedding service for vector generation and similarity search."""

import asyncio
import logging
import numpy as np
from typing import List, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing vector embeddings."""

    def __init__(self):
        """Initialize the embedding service."""
        self.model_name = settings.embedding_model
        self.dimension = settings.vector_dimension
        self._model: SentenceTransformer | None = None
        self._index: faiss.IndexFlatIP | None = None

    async def initialize(self):
        """Initialize the embedding model (async wrapper)."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                SentenceTransformer,
                self.model_name
            )
            logger.info("Embedding model loaded successfully")

    def _ensure_model(self):
        """Ensure model is loaded (sync)."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")

    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as numpy array
        """
        await self.initialize()
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            self._model.encode,
            text,
            True  # normalize_embeddings
        )
        return embedding

    async def generate_embeddings_batch(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Array of embeddings
        """
        await self.initialize()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            self._model.encode,
            texts,
            True,  # normalize_embeddings
            True   # show_progress_bar
        )
        return embeddings

    def create_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Create FAISS index for fast similarity search.

        Args:
            embeddings: Array of embeddings to index

        Returns:
            FAISS index
        """
        if embeddings.shape[1] != self.dimension:
            logger.warning(
                f"Embedding dimension {embeddings.shape[1]} != {self.dimension}. "
                "Updating dimension."
            )
            self.dimension = embeddings.shape[1]

        # Use Inner Product for cosine similarity (since embeddings are normalized)
        index = faiss.IndexFlatIP(self.dimension)
        index.add(embeddings.astype('float32'))
        return index

    def search(
        self,
        index: faiss.IndexFlatIP,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for similar embeddings.

        Args:
            index: FAISS index
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            Tuple of (distances, indices)
        """
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_embedding, top_k)
        return distances[0], indices[0]

    async def compute_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        embeddings = await self.generate_embeddings_batch([text1, text2])
        similarity = np.dot(embeddings[0], embeddings[1])
        return float(similarity)

    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """Convert embedding to bytes for database storage."""
        return embedding.astype('float32').tobytes()

    def bytes_to_embedding(self, data: bytes) -> np.ndarray:
        """Convert bytes to embedding numpy array."""
        return np.frombuffer(data, dtype='float32')


# Global singleton instance
embedding_service = EmbeddingService()
