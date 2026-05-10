import json
import logging
from typing import Any

# Replacing Pinecone with Google Cloud Native: Cloud SQL (PostgreSQL + pgvector)
import asyncpg
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector

logger = logging.getLogger(__name__)


class PGVectorStore:
  """Zero-Trust RAG Implementation utilizing GCP Native Cloud SQL (pgvector).
  Replaces Pinecone to keep the data perimeter entirely within the VPC.
  """

  def __init__(self, project_id: str, location: str, db_config: dict[str, str]):
    self.project_id = project_id
    self.location = location
    self.db_config = db_config
    self.pool = None
    aiplatform.init(project=project_id, location=location)

  async def connect(self):
    """Initialize the asyncpg connection pool and register pgvector."""
    user = self.db_config.get("user")
    password = self.db_config.get("password")
    database = self.db_config.get("database")
    host = self.db_config.get("host")  # Should be the private VPC IP

    self.pool = await asyncpg.create_pool(
      user=user,
      password=password,
      database=database,
      host=host,
    )
    if self.pool is not None:
      # Register the vector type with the pool
      async with self.pool.acquire() as conn:
        await register_vector(conn)

        # Ensure the table exists
        await conn.execute("""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE TABLE IF NOT EXISTS legal_embeddings (
                        id bigserial PRIMARY KEY,
                        content text,
                        metadata jsonb,
                        embedding vector(768)
                    );
                """)

  async def add_documents(self, documents: list[dict[str, Any]]):
    """Ingest documents, generate embeddings via Vertex AI, and store in Cloud SQL.
    Documents should be of form {"content": "...", "metadata": {...}}
    """
    if not self.pool:
      await self.connect()

    # In a real implementation, we would use the Vertex AI Text Embedding API
    # from vertexai.language_models import TextEmbeddingModel
    # model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")

    if self.pool is not None:
      async with self.pool.acquire() as conn:
        for doc in documents:
          content = doc.get("content", "")
          metadata = doc.get("metadata", {})

          # Mock embedding generation (768 dimensions for Gecko)
          # embedding = model.get_embeddings([content])[0].values
          embedding = [0.0] * 768  # Placeholder

          await conn.execute(
            "INSERT INTO legal_embeddings (content, metadata, embedding) VALUES ($1, $2, $3)",
            content,
            json.dumps(metadata),
            embedding,
          )
    logger.info(
      f"Ingested {len(documents)} documents securely into Cloud SQL pgvector."
    )

  async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Perform a native cosine distance search (L2, Inner Product also supported)."""
    if not self.pool:
      await self.connect()

    # Generate query embedding
    # embedding = model.get_embeddings([query])[0].values
    query_embedding = [0.0] * 768  # Placeholder

    if self.pool is not None:
      async with self.pool.acquire() as conn:
        # Using cosine distance operator `<=>`
        rows = await conn.fetch(
          """
                    SELECT content, metadata, 1 - (embedding <=> $1) AS similarity
                    FROM legal_embeddings
                    ORDER BY embedding <=> $1
                    LIMIT $2
                    """,
          query_embedding,
          limit,
        )

        results = []
        for row in rows:
          results.append(
            {
              "content": row["content"],
              "metadata": json.loads(row["metadata"]),
              "score": row["similarity"],
            },
          )

        return results
    return []

  async def close(self):
    if self.pool:
      await self.pool.close()
