"""Vertex AI RAG Retriever Implementation
Based on SELF-ROUTE research paper specifications

Key Features:
- 300-word chunks with configurable overlap
- Dense retrieval using Vertex AI embeddings
- Cosine similarity-based ranking
- Integration with Vertex AI Matching Engine
"""

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """Represents a retrieved text chunk with metadata"""

    text: str
    score: float
    chunk_index: int
    document_id: str
    metadata: dict = None


class VertexRAGRetriever:
    """Production-ready RAG retriever using Vertex AI

    Architecture:
    - Chunk Size: 300 words (empirically validated)
    - Embedding: Vertex AI text-embedding-004 or textembedding-gecko@003
    - Retrieval: Dense retrieval with cosine similarity
    - Top-k: Default k=5 (optimal cost-performance balance)
    """

    def __init__(
        self,
        embedding_model: str = "textembedding-gecko@003",
        chunk_size: int = 300,
        overlap: int = 50,
        project_id: str | None = None,
        location: str = "us-central1",
    ):
        """Initialize the RAG retriever

        Args:
            embedding_model: Vertex AI embedding model name
            chunk_size: Number of words per chunk (default: 300)
            overlap: Word overlap between chunks (default: 50)
            project_id: GCP project ID
            location: GCP region for Vertex AI

        """
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI clients (lazy loading)
        self._embedder = None
        self._index = None

        # Cache for document chunks
        self.chunk_cache: dict[str, list[str]] = {}

        logger.info(
            f"Initialized VertexRAGRetriever: model={embedding_model}, "
            f"chunk_size={chunk_size}, overlap={overlap}",
        )

    @property
    def embedder(self):
        """Lazy load embedding model"""
        if self._embedder is None:
            try:
                import vertexai
                from vertexai.language_models import TextEmbeddingModel

                if self.project_id:
                    vertexai.init(project=self.project_id, location=self.location)

                self._embedder = TextEmbeddingModel.from_pretrained(self.embedding_model)
                logger.info(f"Loaded embedding model: {self.embedding_model}")
            except ImportError:
                logger.error(
                    "vertexai package not installed. Install with: pip install google-cloud-aiplatform",
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

        return self._embedder

    def chunk_document(
        self,
        text: str,
        document_id: str = "default",
        preserve_cache: bool = True,
    ) -> list[str]:
        """Split document into 300-word chunks with configurable overlap

        Args:
            text: Input document text
            document_id: Unique identifier for the document
            preserve_cache: Whether to cache chunks

        Returns:
            List of text chunks

        """
        # Check cache
        if preserve_cache and document_id in self.chunk_cache:
            logger.debug(f"Retrieved {len(self.chunk_cache[document_id])} chunks from cache")
            return self.chunk_cache[document_id]

        # Split into words
        words = text.split()
        chunks = []

        # Create overlapping chunks
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i : i + self.chunk_size]

            # Skip very small final chunks
            if len(chunk_words) < 50:  # Minimum chunk size
                break

            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)

        # Handle edge case: document shorter than chunk size
        if len(chunks) == 0 and len(words) > 0:
            chunks.append(" ".join(words))

        # Cache if requested
        if preserve_cache:
            self.chunk_cache[document_id] = chunks

        logger.info(
            f"Chunked document '{document_id}': {len(words)} words -> "
            f"{len(chunks)} chunks (avg {len(words) / len(chunks):.0f} words/chunk)",
        )

        return chunks

    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for text chunks using Vertex AI

        Args:
            texts: List of text strings to embed

        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)

        """
        try:
            # Vertex AI embedding API
            embeddings_result = self.embedder.get_embeddings(texts)

            # Extract embedding vectors
            embeddings = np.array([emb.values for emb in embeddings_result])

            logger.debug(
                f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}",
            )
            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def cosine_similarity(
        self,
        query_embedding: np.ndarray,
        chunk_embeddings: np.ndarray,
    ) -> np.ndarray:
        """Compute cosine similarity between query and chunks

        Args:
            query_embedding: Query embedding vector (1D array)
            chunk_embeddings: Chunk embedding matrix (n_chunks, embedding_dim)

        Returns:
            Similarity scores (n_chunks,)

        """
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        chunk_norms = chunk_embeddings / np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)

        # Compute cosine similarity
        similarities = np.dot(chunk_norms, query_norm)

        return similarities

    def retrieve(
        self,
        query: str,
        document_text: str | None = None,
        document_id: str = "default",
        k: int = 5,
        _return_scores: bool = True,
    ) -> list[RetrievedChunk]:
        """Retrieve top-k most relevant chunks for a query

        Args:
            query: Search query
            document_text: Document to search (will be chunked)
            document_id: Document identifier
            k: Number of chunks to retrieve
            return_scores: Whether to include similarity scores

        Returns:
            List of RetrievedChunk objects sorted by relevance

        """
        # Chunk document if provided
        if document_text:
            chunks = self.chunk_document(document_text, document_id)
        elif document_id in self.chunk_cache:
            chunks = self.chunk_cache[document_id]
        else:
            raise ValueError("Must provide document_text or have document_id in cache")

        # Generate embeddings
        logger.debug(f"Retrieving from {len(chunks)} chunks with k={k}")

        # Embed query
        query_embedding = self.get_embeddings([query])[0]

        # Embed chunks (batch processing for efficiency)
        chunk_embeddings = self.get_embeddings(chunks)

        # Compute similarities
        similarities = self.cosine_similarity(query_embedding, chunk_embeddings)

        # Get top-k indices
        top_k_indices = np.argsort(similarities)[::-1][:k]

        # Create RetrievedChunk objects
        retrieved_chunks = [
            RetrievedChunk(
                text=chunks[idx],
                score=float(similarities[idx]),
                chunk_index=idx,
                document_id=document_id,
                metadata={"total_chunks": len(chunks)},
            )
            for idx in top_k_indices
        ]

        logger.info(
            f"Retrieved {len(retrieved_chunks)} chunks. "
            f"Top score: {retrieved_chunks[0].score:.3f}, "
            f"Bottom score: {retrieved_chunks[-1].score:.3f}",
        )

        return retrieved_chunks

    def retrieve_with_indices(
        self,
        query: str,
        document_text: str,
        document_id: str = "default",
        k: int = 5,
    ) -> tuple[list[str], list[int], list[float]]:
        """Retrieve chunks with explicit indices (for prompt formatting)

        Returns:
            Tuple of (chunk_texts, chunk_indices, scores)

        """
        retrieved = self.retrieve(query, document_text, document_id, k)

        texts = [chunk.text for chunk in retrieved]
        indices = [chunk.chunk_index for chunk in retrieved]
        scores = [chunk.score for chunk in retrieved]

        return texts, indices, scores

    def format_retrieved_chunks(
        self,
        chunks: list[RetrievedChunk],
        include_scores: bool = False,
        include_indices: bool = True,
    ) -> str:
        """Format retrieved chunks for prompt input

        Args:
            chunks: List of retrieved chunks
            include_scores: Whether to show similarity scores
            include_indices: Whether to show chunk indices

        Returns:
            Formatted string ready for LLM prompt

        """
        formatted_parts = []

        for i, chunk in enumerate(chunks, 1):
            header_parts = [f"[Chunk {i}"]

            if include_indices:
                header_parts.append(f"Index: {chunk.chunk_index}")

            if include_scores:
                header_parts.append(f"Score: {chunk.score:.3f}")

            header = " | ".join(header_parts) + "]"
            formatted_parts.append(f"{header}\n{chunk.text}")

        return "\n\n".join(formatted_parts)

    def clear_cache(self, document_id: str | None = None):
        """Clear chunk cache for specific document or all documents"""
        if document_id:
            if document_id in self.chunk_cache:
                del self.chunk_cache[document_id]
                logger.info(f"Cleared cache for document: {document_id}")
        else:
            self.chunk_cache.clear()
            logger.info("Cleared all chunk cache")

    def get_cache_stats(self) -> dict:
        """Get statistics about cached documents"""
        stats = {"total_documents": len(self.chunk_cache), "documents": {}}

        for doc_id, chunks in self.chunk_cache.items():
            stats["documents"][doc_id] = {
                "num_chunks": len(chunks),
                "total_words": sum(len(chunk.split()) for chunk in chunks),
            }

        return stats
