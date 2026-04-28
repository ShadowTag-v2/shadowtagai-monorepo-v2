# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LanceDB Local Retriever Bridge
Provides the same interface as VertexRAGRetriever but backed by local LanceDB.
Falls back to Vertex AI when local table is unavailable.

Architecture:
- Primary: LanceDB local vectordb (data/lancedb/workspace_knowledge)
- Fallback: Vertex AI text-embedding-004 (via retriever.py)
- Embedding: google-genai or sentence_transformers
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

LANCEDB_PATH = Path(__file__).resolve().parents[4] / "data" / "lancedb"
TABLE_NAME = "workspace_knowledge"


@dataclass
class RetrievedChunk:
    """Represents a retrieved text chunk with metadata."""

    text: str
    score: float
    chunk_index: int
    document_id: str
    metadata: dict | None = None


class LanceDBRetriever:
    """Local-first RAG retriever backed by LanceDB.

    Provides the same interface as VertexRAGRetriever for drop-in use.
    Uses LanceDB's built-in vector search for zero-cost local retrieval.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        table_name: str = TABLE_NAME,
        embedding_column: str = "vector",
        text_column: str = "text",
    ):
        self.db_path = Path(db_path) if db_path else LANCEDB_PATH
        self.table_name = table_name
        self.embedding_column = embedding_column
        self.text_column = text_column
        self._db = None
        self._table = None
        logger.info(
            "Initialized LanceDBRetriever: db=%s, table=%s",
            self.db_path,
            self.table_name,
        )

    @property
    def db(self):
        """Lazy-load LanceDB connection."""
        if self._db is None:
            try:
                import lancedb

                self._db = lancedb.connect(str(self.db_path))
                logger.info("Connected to LanceDB at %s", self.db_path)
            except ImportError:
                logger.error("lancedb not installed. Install with: pip install lancedb")
                raise
        return self._db

    @property
    def table(self):
        """Lazy-load LanceDB table."""
        if self._table is None:
            try:
                self._table = self.db.open_table(self.table_name)
                logger.info(
                    "Opened table '%s' (%d rows)",
                    self.table_name,
                    len(self._table),
                )
            except Exception as e:
                logger.error("Failed to open table '%s': %s", self.table_name, e)
                raise
        return self._table

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filter_sql: str | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve top-k most relevant chunks for a query.

        Uses LanceDB's built-in vector search. If the table has an
        embedding function configured, query text is auto-embedded.
        Otherwise falls back to manual embedding.

        Args:
            query: Search query text.
            k: Number of results to return.
            filter_sql: Optional SQL WHERE clause for pre-filtering.

        Returns:
            List of RetrievedChunk sorted by relevance (highest first).
        """
        try:
            search = self.table.search(query).limit(k)

            if filter_sql:
                search = search.where(filter_sql)

            results = search.to_pandas()

            chunks = []
            for i, row in results.iterrows():
                text = row.get(self.text_column, "")
                score = float(row.get("_distance", 0.0))
                doc_id = str(row.get("source", row.get("doc_id", f"row_{i}")))

                meta = {}
                for col in results.columns:
                    if col not in (
                        self.text_column,
                        self.embedding_column,
                        "_distance",
                    ):
                        val = row[col]
                        if isinstance(val, np.ndarray):
                            continue
                        meta[col] = val

                chunks.append(
                    RetrievedChunk(
                        text=str(text),
                        score=1.0 - score if score <= 1.0 else 1.0 / (1.0 + score),
                        chunk_index=int(i),
                        document_id=doc_id,
                        metadata=meta,
                    )
                )

            logger.info(
                "Retrieved %d chunks for query (top score: %.3f)",
                len(chunks),
                chunks[0].score if chunks else 0.0,
            )
            return chunks

        except Exception as e:
            logger.error("LanceDB retrieval failed: %s", e)
            raise

    def retrieve_hybrid(
        self,
        query: str,
        k: int = 5,
        fts_columns: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """Hybrid search combining vector + full-text search.

        Args:
            query: Search query text.
            k: Number of results.
            fts_columns: Columns to use for full-text search.

        Returns:
            List of RetrievedChunk with fused scores.
        """
        try:
            search = self.table.search(query, query_type="hybrid").limit(k)
            if fts_columns:
                search = search.select(fts_columns)
            results = search.to_pandas()

            chunks = []
            for i, row in results.iterrows():
                text = row.get(self.text_column, "")
                score = float(row.get("_relevance_score", row.get("_distance", 0.0)))
                doc_id = str(row.get("source", f"row_{i}"))

                chunks.append(
                    RetrievedChunk(
                        text=str(text),
                        score=score,
                        chunk_index=int(i),
                        document_id=doc_id,
                    )
                )

            return chunks

        except Exception as e:
            logger.warning("Hybrid search failed, falling back to vector: %s", e)
            return self.retrieve(query, k)

    def format_retrieved_chunks(
        self,
        chunks: list[RetrievedChunk],
        include_scores: bool = False,
        include_indices: bool = True,
    ) -> str:
        """Format chunks for LLM prompt injection."""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            header = [f"[Chunk {i}"]
            if include_indices:
                header.append(f"Source: {chunk.document_id}")
            if include_scores:
                header.append(f"Score: {chunk.score:.3f}")
            parts.append(f"{' | '.join(header)}]\n{chunk.text}")
        return "\n\n".join(parts)

    def list_tables(self) -> list[str]:
        """List all available tables in the LanceDB database."""
        result = self.db.list_tables()
        return result.tables if hasattr(result, "tables") else list(result)

    def table_stats(self) -> dict:
        """Get statistics about the current table."""
        try:
            t = self.table
            return {
                "table_name": self.table_name,
                "row_count": len(t),
                "schema": str(t.schema),
            }
        except Exception as e:
            return {"error": str(e)}


def get_retriever(prefer_local: bool = True) -> LanceDBRetriever:
    """Factory: return local LanceDB retriever if available, else Vertex AI.

    Args:
        prefer_local: If True, try LanceDB first. If False, use Vertex AI.

    Returns:
        A retriever instance with .retrieve() and .format_retrieved_chunks().
    """
    if prefer_local and LANCEDB_PATH.exists():
        try:
            retriever = LanceDBRetriever()
            _ = retriever.table  # Validate table exists
            logger.info("Using local LanceDB retriever")
            return retriever
        except Exception as e:
            logger.warning("LanceDB unavailable (%s), falling back to Vertex AI", e)

    # Fallback to Vertex AI
    from apps.aiyou_stack.aiyou_fastapi_services.src.core.retriever import (
        VertexRAGRetriever,
    )

    logger.info("Using Vertex AI retriever (fallback)")
    return VertexRAGRetriever()
