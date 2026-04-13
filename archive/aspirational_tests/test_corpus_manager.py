"""
Tests for CorpusManager
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from pnkln_file_search.corpus.manager import CorpusManager
from pnkln_file_search.config.verticals import get_vertical_config


@pytest.fixture
def mock_aiplatform():
    """Mock aiplatform initialization"""
    with patch("pnkln_file_search.corpus.manager.aiplatform") as mock:
        yield mock


@pytest.fixture
def mock_rag():
    """Mock RAG operations"""
    with patch("pnkln_file_search.corpus.manager.rag") as mock:
        yield mock


@pytest.mark.asyncio
async def test_corpus_manager_initialization(mock_aiplatform):
    """Test corpus manager initialization"""
    manager = CorpusManager()
    await manager.initialize()

    mock_aiplatform.init.assert_called_once()
    assert manager._initialized is True


@pytest.mark.asyncio
async def test_create_corpus(mock_aiplatform, mock_rag):
    """Test corpus creation"""
    manager = CorpusManager()

    # Mock corpus creation
    mock_corpus = Mock()
    mock_corpus.name = "test-corpus-123"
    mock_rag.create_corpus.return_value = mock_corpus

    vertical_config = get_vertical_config("defense")
    corpus_name = await manager.create_corpus(vertical_config)

    assert corpus_name == "test-corpus-123"
    mock_rag.create_corpus.assert_called_once()


@pytest.mark.asyncio
async def test_import_files(mock_aiplatform, mock_rag):
    """Test file import"""
    manager = CorpusManager()
    await manager.initialize()

    corpus_name = "test-corpus"
    file_paths = ["gs://bucket/file1.pdf", "gs://bucket/file2.pdf"]

    await manager.import_files(corpus_name, file_paths)

    mock_rag.import_files.assert_called_once()
    call_args = mock_rag.import_files.call_args
    assert call_args.kwargs["corpus_name"] == corpus_name
    assert call_args.kwargs["paths"] == file_paths


@pytest.mark.asyncio
async def test_setup_vertical(mock_aiplatform, mock_rag):
    """Test complete vertical setup"""
    manager = CorpusManager()

    mock_corpus = Mock()
    mock_corpus.name = "test-corpus-defense"
    mock_rag.create_corpus.return_value = mock_corpus

    document_paths = ["gs://bucket/itar.pdf"]
    corpus_name = await manager.setup_vertical("defense", document_paths)

    assert corpus_name == "test-corpus-defense"
    mock_rag.create_corpus.assert_called_once()
    mock_rag.import_files.assert_called_once()


@pytest.mark.asyncio
async def test_list_corpora(mock_aiplatform, mock_rag):
    """Test listing corpora"""
    manager = CorpusManager()
    await manager.initialize()

    # Mock corpus list
    mock_corpus1 = Mock()
    mock_corpus1.name = "corpus-1"
    mock_corpus1.display_name = "Corpus 1"
    mock_corpus1.description = "Test corpus 1"

    mock_rag.list_corpora.return_value = [mock_corpus1]

    corpora = await manager.list_corpora()

    assert len(corpora) == 1
    assert corpora[0]["name"] == "corpus-1"


@pytest.mark.asyncio
async def test_delete_corpus(mock_aiplatform, mock_rag):
    """Test corpus deletion"""
    manager = CorpusManager()
    await manager.initialize()

    corpus_name = "test-corpus"
    manager._corpus_cache["defense"] = corpus_name

    await manager.delete_corpus(corpus_name)

    mock_rag.delete_corpus.assert_called_once_with(name=corpus_name)
    assert corpus_name not in manager._corpus_cache.values()
