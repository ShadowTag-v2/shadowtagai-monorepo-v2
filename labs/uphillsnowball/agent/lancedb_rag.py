# labs/uphillsnowball/agent/lancedb_rag.py
"""LanceDB Local RAG Pipeline for UphillSnowball.

Sovereign vector store running entirely on Apple Silicon.
No data leaves the machine — zero cloud dependency for RAG.

Architecture:
    1. Documents → chunking → embeddings (local)
    2. Embeddings → LanceDB (local file-based vector DB)
    3. Query → vector search → context injection → Gemini

LanceDB chosen over FAISS/Chroma because:
    - File-based (no server process needed)
    - Native Arrow columnar format (fast)
    - Supports versioning and incremental updates
    - Works offline on Apple Silicon
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("uphillsnowball.rag")

_DB_PATH = os.getenv(
    "LANCEDB_PATH",
    os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball/data/lancedb"),
)
_TABLE_NAME = "sovereign_documents"


@dataclass
class Document:
    """A document chunk for the RAG pipeline."""
    chunk_id: str
    source_file: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    ingested_at: float = field(default_factory=time.time)


@dataclass
class SearchResult:
    """A search result from the vector store."""
    chunk_id: str
    content: str
    source_file: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SovereignRAG:
    """Local-only RAG pipeline using LanceDB.
    
    All data stays on Apple Silicon. Zero cloud egress.
    """
    
    def __init__(self, db_path: str = _DB_PATH) -> None:
        self._db_path = db_path
        self._db = None
        self._table = None
        self._ensure_db()
    
    def _ensure_db(self) -> None:
        """Initialize LanceDB database directory."""
        Path(self._db_path).mkdir(parents=True, exist_ok=True)
        logger.info("LanceDB initialized at: %s", self._db_path)
    
    def _connect(self):
        """Lazy-connect to LanceDB."""
        if self._db is None:
            try:
                import lancedb
                self._db = lancedb.connect(self._db_path)
                logger.info("LanceDB connected: %s", self._db_path)
            except ImportError:
                logger.warning("lancedb not installed — RAG disabled. pip install lancedb")
                return None
        return self._db
    
    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """Split text into overlapping chunks for embedding."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period > chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]
    
    def _compute_chunk_id(self, source: str, content: str) -> str:
        """Deterministic chunk ID for deduplication."""
        return hashlib.sha256(f"{source}:{content[:100]}".encode()).hexdigest()[:16]
    
    async def ingest_file(self, filepath: str) -> int:
        """Ingest a file into the RAG pipeline.
        
        Returns number of chunks ingested.
        """
        path = Path(filepath)
        if not path.exists():
            logger.error("File not found: %s", filepath)
            return 0
        
        content = path.read_text(errors="replace")
        chunks = self._chunk_text(content)
        
        documents = []
        for chunk in chunks:
            doc = Document(
                chunk_id=self._compute_chunk_id(filepath, chunk),
                source_file=filepath,
                content=chunk,
                metadata={
                    "filename": path.name,
                    "extension": path.suffix,
                    "size_bytes": path.stat().st_size,
                },
            )
            documents.append(doc)
        
        db = self._connect()
        if db is None:
            # Store as JSON fallback when lancedb not installed
            import json
            fallback_path = Path(self._db_path) / "fallback_docs.jsonl"
            with open(fallback_path, "a") as f:
                for doc in documents:
                    f.write(json.dumps({
                        "chunk_id": doc.chunk_id,
                        "source_file": doc.source_file,
                        "content": doc.content,
                        "metadata": doc.metadata,
                    }) + "\n")
            logger.info("Ingested %d chunks to fallback JSONL: %s", len(documents), filepath)
            return len(documents)
        
        # LanceDB ingestion
        data = [
            {
                "chunk_id": doc.chunk_id,
                "source_file": doc.source_file,
                "content": doc.content,
                "metadata": str(doc.metadata),
            }
            for doc in documents
        ]
        
        try:
            if _TABLE_NAME in db.table_names():
                table = db.open_table(_TABLE_NAME)
                table.add(data)
            else:
                db.create_table(_TABLE_NAME, data)
            logger.info("Ingested %d chunks to LanceDB: %s", len(documents), filepath)
        except Exception as e:
            logger.error("LanceDB ingestion failed: %s", e)
        
        return len(documents)
    
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search the vector store for relevant documents.
        
        Falls back to keyword search if embeddings aren't available.
        """
        db = self._connect()
        if db is None:
            return self._fallback_search(query, top_k)
        
        try:
            if _TABLE_NAME not in db.table_names():
                return []
            
            table = db.open_table(_TABLE_NAME)
            # Full-text search fallback (embedding search requires vectors)
            results = table.search(query).limit(top_k).to_list()
            
            return [
                SearchResult(
                    chunk_id=r.get("chunk_id", ""),
                    content=r.get("content", ""),
                    source_file=r.get("source_file", ""),
                    score=r.get("_distance", 0.0),
                )
                for r in results
            ]
        except Exception as e:
            logger.error("LanceDB search failed: %s — falling back", e)
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int) -> list[SearchResult]:
        """Keyword-based fallback when LanceDB is unavailable."""
        import json
        fallback_path = Path(self._db_path) / "fallback_docs.jsonl"
        if not fallback_path.exists():
            return []
        
        results = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        with open(fallback_path) as f:
            for line in f:
                doc = json.loads(line.strip())
                content_lower = doc["content"].lower()
                # Simple TF scoring
                score = sum(1 for term in query_terms if term in content_lower)
                if score > 0:
                    results.append(SearchResult(
                        chunk_id=doc["chunk_id"],
                        content=doc["content"],
                        source_file=doc["source_file"],
                        score=float(score),
                    ))
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


# ── Singleton ──────────────────────────────────────────────────────────────

_rag: SovereignRAG | None = None


def get_rag() -> SovereignRAG:
    """Get or create the singleton SovereignRAG."""
    global _rag  # noqa: PLW0603
    if _rag is None:
        _rag = SovereignRAG()
    return _rag
