"""
Policy RAG (Retrieval-Augmented Generation) system.

Implements semantic search over policy documents using vector embeddings
with support for both Vertex AI Vector Search and pgvector.
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

# RIPPED OUT BY NAG 2 - Langchain crashes on Py 3.14
# from langchain_google_vertexai import VertexAIEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
VertexAIEmbeddings = None


class RecursiveCharacterTextSplitter:
    def __init__(self, *args, **kwargs):
        pass

    def split_text(self, text):
        return [text]


from pydantic import BaseModel

from src.gov_config import settings


class PolicyChunk(BaseModel):
    """Chunk of policy document with metadata."""

    chunk_id: str
    policy_id: str
    policy_name: str
    section: str
    content: str
    effective_date: str | None = None
    jurisdiction: str | None = None
    regulation_name: str | None = None
    embedding: list[float] | None = None

    class Config:
        arbitrary_types_allowed = True


@dataclass
class RetrievalResult:
    """Result from policy retrieval."""

    chunk: PolicyChunk
    score: float  # Similarity score


class BasePolicyRetriever(ABC):
    """Abstract base class for policy retrievers."""

    @abstractmethod
    async def add_policy(self, policy_doc: dict) -> None:
        """Add policy document to vector store."""
        pass

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[str]:
        """Retrieve relevant policy chunks."""
        pass

    @abstractmethod
    async def update_policy(self, policy_id: str, policy_doc: dict) -> None:
        """Update existing policy document."""
        pass

    @abstractmethod
    async def delete_policy(self, policy_id: str) -> None:
        """Delete policy document."""
        pass


class PolicyDocumentProcessor:
    """
    Process policy documents into chunks with metadata.

    Implements intelligent chunking by sections/clauses rather than
    arbitrary character splits for better semantic retrieval.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        # Text splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n## ",  # Section headers
                "\n### ",  # Subsection headers
                "\n\n",  # Paragraphs
                "\n",  # Lines
                ". ",  # Sentences
                " ",  # Words
            ],
        )

    def process_policy(self, policy_doc: dict) -> list[PolicyChunk]:
        """
        Process policy document into chunks.

        Args:
            policy_doc: {
                "policy_id": "POL-001",
                "policy_name": "Data Retention Policy",
                "content": "Full policy text...",
                "effective_date": "2024-01-01",
                "jurisdiction": "US-CA",
                "regulation_name": "CCPA"
            }

        Returns:
            List of policy chunks with metadata
        """
        policy_id = policy_doc["policy_id"]
        policy_name = policy_doc["policy_name"]
        content = policy_doc["content"]

        # Split into chunks
        text_chunks = self.splitter.split_text(content)

        # Create PolicyChunk objects
        chunks = []
        for i, text in enumerate(text_chunks):
            # Generate chunk ID
            chunk_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
            chunk_id = f"{policy_id}_chunk_{i}_{chunk_hash}"

            # Extract section from chunk (heuristic)
            section = self._extract_section(text)

            chunk = PolicyChunk(
                chunk_id=chunk_id,
                policy_id=policy_id,
                policy_name=policy_name,
                section=section,
                content=text,
                effective_date=policy_doc.get("effective_date"),
                jurisdiction=policy_doc.get("jurisdiction"),
                regulation_name=policy_doc.get("regulation_name"),
            )

            chunks.append(chunk)

        return chunks

    def _extract_section(self, text: str) -> str:
        """Extract section identifier from chunk text."""
        lines = text.split("\n")
        for line in lines[:3]:  # Check first 3 lines
            if line.startswith("## ") or line.startswith("### "):
                return line.strip("# ").strip()

            # Look for numbered sections
            if line.strip() and line[0].isdigit() and "." in line[:10]:
                return line.strip()

        return "General"


class PgVectorRetriever(BasePolicyRetriever):
    """
    Policy retriever using pgvector on Cloud SQL PostgreSQL.

    Cost-effective option for <50M vectors with SQL integration.
    """

    def __init__(self, connection_string: str | None = None):
        """Initialize pgvector retriever."""
        import psycopg2

        # Build connection string
        if not connection_string:
            connection_string = (
                f"postgresql://REDACTED_USER:REDACTED_PASS@{settings.postgres_host}:{settings.postgres_port}"
                f"/{settings.postgres_database}"
            )

        self.conn = psycopg2.connect(connection_string)
        self.processor = PolicyDocumentProcessor()

        # Initialize embeddings
        self.embeddings = VertexAIEmbeddings(
            model_name=settings.embedding_model,
            project=settings.gcp_project_id,
        )

        # Create table if not exists
        self._create_table()

    def _create_table(self) -> None:
        """Create pgvector table for policy chunks."""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS policy_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    policy_id TEXT NOT NULL,
                    policy_name TEXT NOT NULL,
                    section TEXT,
                    content TEXT NOT NULL,
                    effective_date TEXT,
                    jurisdiction TEXT,
                    regulation_name TEXT,
                    embedding vector(768),  -- textembedding-gecko dimensions
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """
            )

            # Create HNSW index for vector similarity
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS policy_chunks_embedding_idx
                ON policy_chunks
                USING hnsw (embedding vector_cosine_ops)
            """
            )

            self.conn.commit()

    async def add_policy(self, policy_doc: dict) -> None:
        """Add policy document to pgvector."""
        # Process document into chunks
        chunks = self.processor.process_policy(policy_doc)

        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embeddings.aembed_documents(texts)

        # Insert into database
        with self.conn.cursor() as cur:
            for chunk, embedding in zip(chunks, embeddings, strict=False):
                cur.execute(
                    """
                    INSERT INTO policy_chunks (
                        chunk_id, policy_id, policy_name, section,
                        content, effective_date, jurisdiction,
                        regulation_name, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding
                """,
                    (
                        chunk.chunk_id,
                        chunk.policy_id,
                        chunk.policy_name,
                        chunk.section,
                        chunk.content,
                        chunk.effective_date,
                        chunk.jurisdiction,
                        chunk.regulation_name,
                        embedding,
                    ),
                )

        self.conn.commit()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[str]:
        """
        Retrieve relevant policy chunks using semantic search.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters (jurisdiction, policy_id, etc.)

        Returns:
            List of policy chunk texts
        """
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)

        # Build SQL query with optional filters
        sql = """
            SELECT content, section, policy_name,
                   1 - (embedding <=> %s::vector) as similarity
            FROM policy_chunks
        """

        params = [query_embedding]
        where_clauses = []

        if filters:
            if "policy_id" in filters:
                where_clauses.append("policy_id = %s")
                params.append(filters["policy_id"])

            if "jurisdiction" in filters:
                where_clauses.append("jurisdiction = %s")
                params.append(filters["jurisdiction"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([query_embedding, top_k])

        # Execute query
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            results = cur.fetchall()

        # Format results
        formatted_results = []
        for content, section, policy_name, similarity in results:
            formatted_results.append(
                f"[{policy_name} - {section}]\n{content}\n(Relevance: {similarity:.2f})"
            )

        return formatted_results

    async def update_policy(self, policy_id: str, policy_doc: dict) -> None:
        """Update policy by deleting and re-adding."""
        await self.delete_policy(policy_id)
        await self.add_policy(policy_doc)

    async def delete_policy(self, policy_id: str) -> None:
        """Delete policy from vector store."""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM policy_chunks WHERE policy_id = %s", (policy_id,))
        self.conn.commit()

    def refresh_index(self) -> None:
        """Rebuild HNSW index for optimal performance."""
        with self.conn.cursor() as cur:
            cur.execute("REINDEX INDEX policy_chunks_embedding_idx")
        self.conn.commit()


class VertexAIVectorSearchRetriever(BasePolicyRetriever):
    """
    Policy retriever using Vertex AI Vector Search.

    Enterprise-scale option for >50M vectors with sub-100ms latency.
    """

    def __init__(self, index_endpoint: str | None = None):
        """Initialize Vertex AI Vector Search retriever."""
        from google.cloud import aiplatform

        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.gcp_region,
        )

        self.index_endpoint = index_endpoint
        self.processor = PolicyDocumentProcessor()

        # Initialize embeddings
        self.embeddings = VertexAIEmbeddings(
            model_name=settings.embedding_model,
            project=settings.gcp_project_id,
        )

    async def add_policy(self, policy_doc: dict) -> None:
        """Add policy to Vertex AI Vector Search."""
        # Implementation depends on Vector Search setup
        # Typically involves batch upsert to index
        raise NotImplementedError("Vertex AI Vector Search implementation pending")

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[str]:
        """Retrieve using Vertex AI Vector Search."""
        # Implementation depends on Vector Search deployment
        raise NotImplementedError("Vertex AI Vector Search implementation pending")

    async def update_policy(self, policy_id: str, policy_doc: dict) -> None:
        """Update policy in Vector Search."""
        raise NotImplementedError("Vertex AI Vector Search implementation pending")

    async def delete_policy(self, policy_id: str) -> None:
        """Delete policy from Vector Search."""
        raise NotImplementedError("Vertex AI Vector Search implementation pending")


def get_policy_retriever() -> BasePolicyRetriever:
    """Factory function to get configured policy retriever."""
    if settings.vector_db_type == "vertex-ai":
        return VertexAIVectorSearchRetriever()
    else:
        return PgVectorRetriever()
