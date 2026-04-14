"""Vertex AI RAG Corpus Manager
Handles creation, management, and querying of policy document corpora
"""

import structlog
from google.cloud import aiplatform
from vertexai.preview import rag

from pnkln_file_search.config.settings import get_settings
from pnkln_file_search.config.verticals import VerticalConfig, get_vertical_config

logger = structlog.get_logger(__name__)


class CorpusManager:
    """Manages Vertex AI RAG corpora for policy documents

    Each vertical gets its own corpus with regulatory documents.
    Supports creating, importing, and querying document corpora.
    """

    def __init__(self):
        """Initialize corpus manager with settings"""
        self.settings = get_settings()
        self._initialized = False
        self._corpus_cache: dict[str, str] = {}  # vertical_name -> corpus_name

    async def initialize(self) -> None:
        """Initialize Vertex AI platform"""
        if self._initialized:
            return

        try:
            aiplatform.init(
                project=self.settings.gcp_project_id,
                location=self.settings.vertex_ai_location,
                staging_bucket=self.settings.gcp_storage_bucket,
            )
            self._initialized = True
            logger.info(
                "corpus_manager_initialized",
                project=self.settings.gcp_project_id,
                location=self.settings.vertex_ai_location,
            )
        except Exception as e:
            logger.error("corpus_manager_init_failed", error=str(e))
            raise

    async def create_corpus(
        self, vertical_config: VerticalConfig, force_recreate: bool = False,
    ) -> str:
        """Create a RAG corpus for a specific vertical

        Args:
            vertical_config: Configuration for the vertical
            force_recreate: If True, delete existing corpus and recreate

        Returns:
            Corpus name (resource ID)

        """
        await self.initialize()

        corpus_display_name = f"pnkln_{vertical_config.name}_policies"

        # Check cache first
        if not force_recreate and vertical_config.name in self._corpus_cache:
            logger.info("corpus_found_in_cache", vertical=vertical_config.name)
            return self._corpus_cache[vertical_config.name]

        try:
            # Create corpus
            corpus = rag.create_corpus(
                display_name=corpus_display_name,
                description=f"{vertical_config.display_name}: {vertical_config.description}. "
                f"Regulations: {', '.join(vertical_config.regulations)}",
            )

            corpus_name = corpus.name
            self._corpus_cache[vertical_config.name] = corpus_name

            logger.info(
                "corpus_created",
                vertical=vertical_config.name,
                corpus_name=corpus_name,
                regulations=vertical_config.regulations,
            )

            return corpus_name

        except Exception as e:
            logger.error(
                "corpus_creation_failed",
                vertical=vertical_config.name,
                error=str(e),
            )
            raise

    async def import_files(
        self,
        corpus_name: str,
        file_paths: list[str],
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """Import files into a corpus

        Args:
            corpus_name: Target corpus resource name
            file_paths: List of GCS URIs (gs://bucket/path/file.pdf)
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap

        """
        await self.initialize()

        chunk_size = chunk_size or self.settings.file_search_chunk_size
        chunk_overlap = chunk_overlap or self.settings.file_search_chunk_overlap

        try:
            # Import files (Google handles chunking and embedding)
            rag.import_files(
                corpus_name=corpus_name,
                paths=file_paths,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            logger.info(
                "files_imported",
                corpus_name=corpus_name,
                file_count=len(file_paths),
                chunk_size=chunk_size,
            )

        except Exception as e:
            logger.error(
                "file_import_failed",
                corpus_name=corpus_name,
                error=str(e),
            )
            raise

    async def setup_vertical(self, vertical_name: str, document_paths: list[str]) -> str:
        """Complete setup for a vertical: create corpus and import documents

        Args:
            vertical_name: Name of the vertical
            document_paths: List of GCS URIs to policy documents

        Returns:
            Corpus name

        """
        vertical_config = get_vertical_config(vertical_name)

        # Create corpus
        corpus_name = await self.create_corpus(vertical_config)

        # Import documents if provided
        if document_paths:
            await self.import_files(corpus_name, document_paths)

        return corpus_name

    async def list_corpora(self) -> list[dict[str, str]]:
        """List all corpora in the project

        Returns:
            List of corpus metadata dicts

        """
        await self.initialize()

        try:
            corpora = rag.list_corpora()
            result = [
                {
                    "name": corpus.name,
                    "display_name": corpus.display_name,
                    "description": corpus.description or "",
                }
                for corpus in corpora
            ]

            logger.info("corpora_listed", count=len(result))
            return result

        except Exception as e:
            logger.error("corpus_list_failed", error=str(e))
            raise

    async def delete_corpus(self, corpus_name: str) -> None:
        """Delete a corpus

        Args:
            corpus_name: Corpus resource name to delete

        """
        await self.initialize()

        try:
            rag.delete_corpus(name=corpus_name)

            # Remove from cache
            self._corpus_cache = {k: v for k, v in self._corpus_cache.items() if v != corpus_name}

            logger.info("corpus_deleted", corpus_name=corpus_name)

        except Exception as e:
            logger.error("corpus_deletion_failed", corpus_name=corpus_name, error=str(e))
            raise

    def get_corpus_name(self, vertical_name: str) -> str | None:
        """Get cached corpus name for a vertical

        Args:
            vertical_name: Name of the vertical

        Returns:
            Corpus name if cached, None otherwise

        """
        return self._corpus_cache.get(vertical_name)
