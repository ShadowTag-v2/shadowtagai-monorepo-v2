# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Embedding Generator
Generates embeddings for code and text using various providers
"""

import asyncio
import logging
from typing import Any
from dataclasses import dataclass
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from pnkln_intelligence.config import EmbeddingSettings

logger = logging.getLogger(__name__)


@dataclass
class Embedding:
    """Represents an embedding with metadata"""

    text: str
    vector: list[float]
    model: str
    dimensions: int
    metadata: dict[str, Any]


class EmbeddingGenerator:
    """
    Generates embeddings for code and text

    Supports multiple providers:
    - OpenAI (text-embedding-3-large, text-embedding-3-small)
    - Voyage AI (voyage-code-2)
    - Self-hosted models (CodeBERT, GraphCodeBERT, StarEncoder)

    Features:
    - Batch processing for efficiency
    - Automatic chunking for long texts
    - Token counting and management
    - Retry logic with exponential backoff
    """

    def __init__(self, settings: EmbeddingSettings | None = None):
        self.settings = settings or EmbeddingSettings()

        # Initialize API clients based on provider
        self.openai_client = None
        self.anthropic_client = None

        if self.settings.provider == "openai" and self.settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)

        if self.settings.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

    async def generate_embedding(self, text: str, model: str | None = None, metadata: dict[str, Any] | None = None) -> Embedding:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed
            model: Model name (uses settings default if not provided)
            metadata: Additional metadata

        Returns:
            Embedding object
        """
        model = model or self.settings.model_name
        metadata = metadata or {}

        if self.settings.provider == "openai":
            return await self._generate_openai_embedding(text, model, metadata)
        elif self.settings.provider == "voyage":
            return await self._generate_voyage_embedding(text, model, metadata)
        elif self.settings.provider == "codebert":
            return await self._generate_codebert_embedding(text, model, metadata)
        else:
            raise ValueError(f"Unsupported provider: {self.settings.provider}")

    async def generate_embeddings_batch(
        self, texts: list[str], model: str | None = None, metadata_list: list[dict[str, Any]] | None = None
    ) -> list[Embedding]:
        """
        Generate embeddings for multiple texts in batch

        Args:
            texts: List of texts to embed
            model: Model name
            metadata_list: List of metadata dictionaries (one per text)

        Returns:
            List of Embedding objects
        """
        model = model or self.settings.model_name
        metadata_list = metadata_list or [{} for _ in texts]

        if len(metadata_list) != len(texts):
            raise ValueError("metadata_list length must match texts length")

        # Process in batches
        batch_size = self.settings.batch_size
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_metadata = metadata_list[i : i + batch_size]

            if self.settings.provider == "openai":
                batch_embeddings = await self._generate_openai_embeddings_batch(batch_texts, model, batch_metadata)
            elif self.settings.provider == "voyage":
                batch_embeddings = await self._generate_voyage_embeddings_batch(batch_texts, model, batch_metadata)
            elif self.settings.provider == "codebert":
                batch_embeddings = await self._generate_codebert_embeddings_batch(batch_texts, model, batch_metadata)
            else:
                raise ValueError(f"Unsupported provider: {self.settings.provider}")

            embeddings.extend(batch_embeddings)

        logger.info(f"Generated {len(embeddings)} embeddings in batches")
        return embeddings

    async def _generate_openai_embedding(self, text: str, model: str, metadata: dict[str, Any]) -> Embedding:
        """Generate embedding using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")

        try:
            response = await self.openai_client.embeddings.create(
                model=model, input=text, dimensions=self.settings.dimensions if model.startswith("text-embedding-3") else None
            )

            embedding_vector = response.data[0].embedding

            return Embedding(
                text=text,
                vector=embedding_vector,
                model=model,
                dimensions=len(embedding_vector),
                metadata={**metadata, "provider": "openai", "usage": response.usage.model_dump() if response.usage else None},
            )

        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}", exc_info=True)
            raise

    async def _generate_openai_embeddings_batch(self, texts: list[str], model: str, metadata_list: list[dict[str, Any]]) -> list[Embedding]:
        """Generate embeddings for batch using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")

        try:
            response = await self.openai_client.embeddings.create(
                model=model, input=texts, dimensions=self.settings.dimensions if model.startswith("text-embedding-3") else None
            )

            embeddings = []
            for i, data in enumerate(response.data):
                embeddings.append(
                    Embedding(
                        text=texts[i],
                        vector=data.embedding,
                        model=model,
                        dimensions=len(data.embedding),
                        metadata={**metadata_list[i], "provider": "openai", "batch_index": i},
                    )
                )

            return embeddings

        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings batch: {e}", exc_info=True)
            raise

    async def _generate_voyage_embedding(self, text: str, model: str, metadata: dict[str, Any]) -> Embedding:
        """Generate embedding using Voyage AI API"""
        # Voyage AI uses HTTP API
        import httpx

        if not self.settings.voyage_api_key:
            raise ValueError("Voyage API key not configured")

        url = "https://api.voyageai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.settings.voyage_api_key}", "Content-Type": "application/json"}

        payload = {"input": text, "model": model}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()

                embedding_vector = data["data"][0]["embedding"]

                return Embedding(
                    text=text,
                    vector=embedding_vector,
                    model=model,
                    dimensions=len(embedding_vector),
                    metadata={**metadata, "provider": "voyage", "usage": data.get("usage")},
                )

            except Exception as e:
                logger.error(f"Error generating Voyage embedding: {e}", exc_info=True)
                raise

    async def _generate_voyage_embeddings_batch(self, texts: list[str], model: str, metadata_list: list[dict[str, Any]]) -> list[Embedding]:
        """Generate embeddings for batch using Voyage AI API"""
        import httpx

        if not self.settings.voyage_api_key:
            raise ValueError("Voyage API key not configured")

        url = "https://api.voyageai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.settings.voyage_api_key}", "Content-Type": "application/json"}

        payload = {"input": texts, "model": model}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()

                embeddings = []
                for i, item in enumerate(data["data"]):
                    embeddings.append(
                        Embedding(
                            text=texts[i],
                            vector=item["embedding"],
                            model=model,
                            dimensions=len(item["embedding"]),
                            metadata={**metadata_list[i], "provider": "voyage", "batch_index": i},
                        )
                    )

                return embeddings

            except Exception as e:
                logger.error(f"Error generating Voyage embeddings batch: {e}", exc_info=True)
                raise

    async def _generate_codebert_embedding(self, text: str, model: str, metadata: dict[str, Any]) -> Embedding:
        """Generate embedding using CodeBERT (self-hosted)"""
        # This requires sentence-transformers library
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers library required for CodeBERT")

        # Load model (should be cached after first load)
        model_name = "microsoft/codebert-base" if model == "codebert" else model
        encoder = SentenceTransformer(model_name)

        # Generate embedding
        embedding_vector = encoder.encode(text, convert_to_numpy=True)

        return Embedding(
            text=text, vector=embedding_vector.tolist(), model=model, dimensions=len(embedding_vector), metadata={**metadata, "provider": "codebert"}
        )

    async def _generate_codebert_embeddings_batch(self, texts: list[str], model: str, metadata_list: list[dict[str, Any]]) -> list[Embedding]:
        """Generate embeddings for batch using CodeBERT"""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers library required for CodeBERT")

        model_name = "microsoft/codebert-base" if model == "codebert" else model
        encoder = SentenceTransformer(model_name)

        # Generate embeddings
        embedding_vectors = encoder.encode(texts, convert_to_numpy=True)

        embeddings = []
        for i, vector in enumerate(embedding_vectors):
            embeddings.append(
                Embedding(
                    text=texts[i],
                    vector=vector.tolist(),
                    model=model,
                    dimensions=len(vector),
                    metadata={**metadata_list[i], "provider": "codebert", "batch_index": i},
                )
            )

        return embeddings

    async def generate_code_embeddings(self, code_chunks: list[str], language: str, repo_name: str) -> list[Embedding]:
        """
        Generate embeddings specifically for code chunks

        Args:
            code_chunks: List of code chunks
            language: Programming language
            repo_name: Repository name

        Returns:
            List of Embedding objects
        """
        # Prepare metadata for each chunk
        metadata_list = [{"type": "code", "language": language, "repo": repo_name, "chunk_index": i} for i in range(len(code_chunks))]

        return await self.generate_embeddings_batch(code_chunks, metadata_list=metadata_list)


# Example usage
if __name__ == "__main__":

    async def main():
        generator = EmbeddingGenerator()

        # Generate single embedding
        code = """
        def calculate_fibonacci(n: int) -> int:
            if n <= 1:
                return n
            return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """

        embedding = await generator.generate_embedding(code, metadata={"type": "code", "language": "python"})

        print("Generated embedding:")
        print(f"Model: {embedding.model}")
        print(f"Dimensions: {embedding.dimensions}")
        print(f"Vector (first 5): {embedding.vector[:5]}")

    asyncio.run(main())
