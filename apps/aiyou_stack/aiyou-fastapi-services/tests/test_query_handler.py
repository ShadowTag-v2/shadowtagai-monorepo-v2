"""Tests for QueryHandler"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from pnkln_file_search.orchestrator.query_handler import PolicyContext, QueryHandler


@pytest.fixture
def mock_corpus_manager():
    """Mock corpus manager"""
    manager = Mock()
    manager.initialize = AsyncMock()
    manager.get_corpus_name = Mock(return_value="test-corpus")
    return manager


@pytest.fixture
def mock_generative_model():
    """Mock Gemini GenerativeModel"""
    with patch("pnkln_file_search.orchestrator.query_handler.GenerativeModel") as mock:
        yield mock


@pytest.mark.asyncio
async def test_query_handler_initialization(mock_corpus_manager, mock_generative_model):
    """Test query handler initialization"""
    handler = QueryHandler(mock_corpus_manager)
    await handler.initialize()

    mock_corpus_manager.initialize.assert_called_once()
    assert handler._model is not None


@pytest.mark.asyncio
async def test_get_policy_context(mock_corpus_manager, mock_generative_model):
    """Test policy context retrieval"""
    handler = QueryHandler(mock_corpus_manager)

    # Mock response
    mock_response = Mock()
    mock_response.text = "Policy context text"
    mock_response.candidates = [Mock()]
    mock_response.candidates[0].grounding_metadata = Mock()
    mock_response.candidates[0].grounding_metadata.grounding_chunks = []

    mock_model_instance = Mock()
    mock_model_instance.generate_content = Mock(return_value=mock_response)
    mock_generative_model.return_value = mock_model_instance
    handler._model = mock_model_instance

    context = await handler.get_policy_context("test-corpus", "test query")

    assert isinstance(context, PolicyContext)
    assert context.context_text == "Policy context text"
    assert context.retrieval_time_ms > 0


@pytest.mark.asyncio
async def test_judge_layer1(mock_corpus_manager):
    """Test Judge Layer 1 assessment"""
    handler = QueryHandler(mock_corpus_manager)

    result = await handler.judge_gemini_layer1("test query")

    assert "atp_5_19_flags" in result
    assert "risk_level" in result
    assert result["layer1_latency_ms"] >= 0


@pytest.mark.asyncio
async def test_judge_hybrid_enforce(mock_corpus_manager):
    """Test Judge hybrid enforcement"""
    handler = QueryHandler(mock_corpus_manager)

    enhanced_context = {
        "query": "test query",
        "policy_refs": [],
        "risk_signals": [],
    }

    result = await handler.judge_hybrid_enforce(enhanced_context)

    assert "allowed" in result
    assert "confidence" in result
    assert "policy_violations" in result


@pytest.mark.asyncio
async def test_process_query_with_context(mock_corpus_manager, mock_generative_model):
    """Test full query processing"""
    handler = QueryHandler(mock_corpus_manager)

    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = "Policy context"
    mock_response.candidates = [Mock()]
    mock_response.candidates[0].grounding_metadata = Mock()
    mock_response.candidates[0].grounding_metadata.grounding_chunks = []

    mock_model_instance = Mock()
    mock_model_instance.generate_content = Mock(return_value=mock_response)
    mock_generative_model.return_value = mock_model_instance
    handler._model = mock_model_instance

    result = await handler.process_query_with_context(
        user_query="test query",
        vertical="defense",
        corpus_name="test-corpus",
    )

    assert "query" in result
    assert "enforcement" in result
    assert "policy_context" in result
    assert "timing" in result
    assert result["vertical"] == "defense"
