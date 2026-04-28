# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
LanceDB RAG Pipeline — Phase 6

ShadowTag-v4 Retrieval-Augmented Generation pipeline using LanceDB
as the sovereign vector store. All data stays on-device (Apple Silicon)
or in GCP (production).

Architecture:
    Document → Chunk → Embed (Gemini) → LanceDB → Retrieve → Generate

Dependencies:
    pip install lancedb sentence-transformers google-generativeai
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────

LANCEDB_PATH = os.environ.get(
    "LANCEDB_PATH",
    str(Path.home() / ".shadowtag" / "lancedb"),
)
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "64"))
TOP_K = int(os.environ.get("RAG_TOP_K", "5"))
TABLE_NAME = os.environ.get("LANCEDB_TABLE", "shadowtag_docs")


# ── Data Models ────────────────────────────────────────────────


@dataclass
class Document:
    """A source document to be ingested into the RAG pipeline."""

    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_id: str = ""

    def __post_init__(self):
        if not self.doc_id:
            self.doc_id = hashlib.sha256(
                f"{self.source}:{self.content[:100]}".encode()
            ).hexdigest()[:16]


@dataclass
class Chunk:
    """A text chunk derived from a document."""

    text: str
    doc_id: str
    chunk_index: int
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """A single retrieval result from the vector store."""

    text: str
    source: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Chunker ────────────────────────────────────────────────────


class TextChunker:
    """Split documents into overlapping chunks for embedding."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, doc: Document) -> list[Chunk]:
        """Split a document into chunks."""
        text = doc.content
        chunks = []
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            # Try to break on sentence boundary
            if end < len(text):
                for boundary in [". ", ".\n", "\n\n", "\n", " "]:
                    last_boundary = text[start:end].rfind(boundary)
                    if last_boundary > self.chunk_size // 2:
                        end = start + last_boundary + len(boundary)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        doc_id=doc.doc_id,
                        chunk_index=idx,
                        source=doc.source,
                        metadata=doc.metadata,
                    )
                )
                idx += 1

            start = end - self.overlap if end < len(text) else len(text)

        logger.info(f"Chunked '{doc.source}' into {len(chunks)} chunks")
        return chunks


# ── Embedder ───────────────────────────────────────────────────


class Embedder:
    """Generate embeddings using sentence-transformers (local) or Gemini (API)."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.warning("sentence-transformers not installed, using Gemini embeddings")
                self._model = "gemini"

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        self._load_model()

        if self._model == "gemini":
            return self._embed_gemini(texts)

        return self._model.encode(texts, show_progress_bar=False).tolist()

    def _embed_gemini(self, texts: list[str]) -> list[list[float]]:
        """Fallback: use Gemini API for embeddings."""
        try:
            import google.generativeai as genai

            result = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            raise


# ── LanceDB Vector Store ───────────────────────────────────────


class VectorStore:
    """LanceDB vector store for RAG retrieval."""

    def __init__(self, db_path: str = LANCEDB_PATH, table_name: str = TABLE_NAME):
        self.db_path = db_path
        self.table_name = table_name
        self._db = None
        self._table = None

    def _connect(self):
        """Connect to LanceDB."""
        if self._db is None:
            import lancedb

            os.makedirs(self.db_path, exist_ok=True)
            self._db = lancedb.connect(self.db_path)
            logger.info(f"Connected to LanceDB at {self.db_path}")

    def _get_or_create_table(self, sample_vector_dim: int = 384):
        """Get or create the document table."""
        self._connect()
        import pyarrow as pa

        if self.table_name in self._db.list_tables():
            self._table = self._db.open_table(self.table_name)
        else:
            schema = pa.schema(
                [
                    pa.field("vector", pa.list_(pa.float32(), sample_vector_dim)),
                    pa.field("text", pa.string()),
                    pa.field("doc_id", pa.string()),
                    pa.field("chunk_index", pa.int32()),
                    pa.field("source", pa.string()),
                    pa.field("metadata", pa.string()),
                ]
            )
            self._table = self._db.create_table(self.table_name, schema=schema)
            logger.info(f"Created table '{self.table_name}'")

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]):
        """Add chunks with their embeddings to the store."""
        import json

        self._get_or_create_table(len(embeddings[0]) if embeddings else 384)

        records = []
        for chunk, emb in zip(chunks, embeddings, strict=False):
            records.append(
                {
                    "vector": emb,
                    "text": chunk.text,
                    "doc_id": chunk.doc_id,
                    "chunk_index": chunk.chunk_index,
                    "source": chunk.source,
                    "metadata": json.dumps(chunk.metadata),
                }
            )

        self._table.add(records)
        logger.info(f"Added {len(records)} vectors to '{self.table_name}'")

    def search(self, query_vector: list[float], top_k: int = TOP_K) -> list[RetrievalResult]:
        """Search for the closest vectors."""
        import json

        self._get_or_create_table(len(query_vector))

        results = self._table.search(query_vector).limit(top_k).to_pandas()

        return [
            RetrievalResult(
                text=row["text"],
                source=row["source"],
                score=float(row.get("_distance", 0.0)),
                metadata=json.loads(row.get("metadata", "{}")),
            )
            for _, row in results.iterrows()
        ]

    def count(self) -> int:
        """Return total number of vectors in the table."""
        self._get_or_create_table()
        return self._table.count_rows()


# ── RAG Pipeline ───────────────────────────────────────────────


class RAGPipeline:
    """End-to-end RAG pipeline: ingest → retrieve → generate."""

    def __init__(
        self,
        db_path: str = LANCEDB_PATH,
        table_name: str = TABLE_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        self.chunker = TextChunker()
        self.embedder = Embedder(embedding_model)
        self.store = VectorStore(db_path, table_name)

    def ingest(self, documents: list[Document]) -> int:
        """Ingest documents into the vector store."""
        total_chunks = 0
        start = time.time()

        for doc in documents:
            chunks = self.chunker.chunk(doc)
            if not chunks:
                continue

            texts = [c.text for c in chunks]
            embeddings = self.embedder.embed(texts)
            self.store.add(chunks, embeddings)
            total_chunks += len(chunks)

        elapsed = time.time() - start
        logger.info(
            f"Ingested {len(documents)} docs → {total_chunks} chunks "
            f"in {elapsed:.1f}s ({total_chunks / max(elapsed, 0.01):.0f} chunks/s)"
        )
        return total_chunks

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[RetrievalResult]:
        """Retrieve relevant chunks for a query."""
        query_embedding = self.embedder.embed([query])[0]
        return self.store.search(query_embedding, top_k)

    def query(self, question: str, top_k: int = TOP_K) -> dict[str, Any]:
        """Full RAG: retrieve context + generate answer."""
        results = self.retrieve(question, top_k)

        context = "\n\n---\n\n".join([f"[Source: {r.source}]\n{r.text}" for r in results])

        # Generate answer using Gemini
        try:
            import google.generativeai as genai

            model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
            prompt = (
                f"Answer the following question using ONLY the provided context. "
                f"If the context doesn't contain enough information, say so.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            answer = f"[Generation failed: {e}]\n\nRetrieved context:\n{context}"

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {"source": r.source, "score": r.score, "text": r.text[:200]} for r in results
            ],
            "num_sources": len(results),
        }

    def stats(self) -> dict[str, Any]:
        """Return pipeline statistics."""
        return {
            "db_path": self.store.db_path,
            "table": self.store.table_name,
            "total_vectors": self.store.count(),
            "embedding_model": self.embedder.model_name,
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.overlap,
        }


# ── CLI Entry Point ────────────────────────────────────────────


def main():
    """CLI entry point for the RAG pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="ShadowTag LanceDB RAG Pipeline")
    sub = parser.add_subparsers(dest="command")

    # Ingest command
    ingest_cmd = sub.add_parser("ingest", help="Ingest files into the vector store")
    ingest_cmd.add_argument("files", nargs="+", help="Files to ingest")
    ingest_cmd.add_argument("--table", default=TABLE_NAME)

    # Query command
    query_cmd = sub.add_parser("query", help="Query the RAG pipeline")
    query_cmd.add_argument("question", help="Question to ask")
    query_cmd.add_argument("--top-k", type=int, default=TOP_K)

    # Stats command
    sub.add_parser("stats", help="Show pipeline statistics")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    pipeline = RAGPipeline(table_name=getattr(args, "table", TABLE_NAME))

    if args.command == "ingest":
        docs = []
        for filepath in args.files:
            path = Path(filepath)
            if path.is_file():
                content = path.read_text(errors="replace")
                docs.append(Document(content=content, source=str(path)))
            elif path.is_dir():
                for f in path.rglob("*"):
                    if f.is_file() and f.suffix in {
                        ".py",
                        ".md",
                        ".txt",
                        ".yaml",
                        ".json",
                        ".html",
                    }:
                        content = f.read_text(errors="replace")
                        docs.append(Document(content=content, source=str(f)))

        if docs:
            count = pipeline.ingest(docs)
            print(f"✅ Ingested {len(docs)} files → {count} chunks")
        else:
            print("❌ No files found to ingest")

    elif args.command == "query":
        import json

        result = pipeline.query(args.question, top_k=args.top_k)
        print(f"\n📝 Answer:\n{result['answer']}\n")
        print(f"📚 Sources ({result['num_sources']}):")
        for s in result["sources"]:
            print(f"  • {s['source']} (score: {s['score']:.4f})")

    elif args.command == "stats":
        import json

        stats = pipeline.stats()
        print(json.dumps(stats, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
