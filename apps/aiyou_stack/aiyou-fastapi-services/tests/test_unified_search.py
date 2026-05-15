"""Tests for Unified Search API"""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from unified_search_api import SearchResult, app, merge_and_rank_results

client = TestClient(app)


class TestUnifiedSearchAPI:
    """Test suite for Unified Search API"""

    def test_health_check(self):
        """Test root endpoint returns healthy status"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "Unified Search API"
        assert data["status"] == "healthy"
        assert "sources_available" in data

    def test_get_sources(self):
        """Test /sources endpoint returns available search sources"""
        response = client.get("/sources")
        assert response.status_code == 200

        data = response.json()
        assert "gptram" in data
        assert data["gptram"]["available"] is True
        assert data["gptram"]["type"] == "local"

    def test_merge_and_rank_results(self):
        """Test Reciprocal Rank Fusion (RRF) merging"""
        gptram_results = [
            SearchResult(source="gptram", score=1.0, key="decision:1", text="First GPTRAM result"),
            SearchResult(source="gptram", score=0.9, key="decision:2", text="Second GPTRAM result"),
        ]

        pnkln_results = [
            SearchResult(
                source="pnkln",
                score=1.0,
                key="code:1",
                text="First PNKLN result",
                repository="vllm",
            ),
        ]

        merged = merge_and_rank_results(gptram_results, pnkln_results, k=10)

        # Should have 3 total results
        assert len(merged) == 3

        # All should have RRF scores
        for result in merged:
            assert 0 < result.score <= 1.0

        # Results should be sorted by score (descending)
        scores = [r.score for r in merged]
        assert scores == sorted(scores, reverse=True)

    def test_merge_and_rank_top_k_limit(self):
        """Test that merge_and_rank respects k limit"""
        gptram_results = [
            SearchResult(source="gptram", score=1.0, key=f"gptram:{i}", text=f"Result {i}")
            for i in range(10)
        ]

        pnkln_results = [
            SearchResult(source="pnkln", score=1.0, key=f"pnkln:{i}", text=f"Result {i}")
            for i in range(10)
        ]

        merged = merge_and_rank_results(gptram_results, pnkln_results, k=5)

        # Should return only top 5
        assert len(merged) == 5

    @patch("unified_search_api.search_gptram")
    async def test_unified_search_gptram_only(self, mock_search_gptram):
        """Test unified search with GPTRAM only"""
        # Mock GPTRAM results
        mock_search_gptram.return_value = [
            SearchResult(
                source="gptram",
                score=0.9,
                key="decision:test",
                text="Test decision",
                ts=1700000000,
            ),
        ]

        response = client.post(
            "/search",
            json={"query": "test query", "k": 5, "sources": ["gptram"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "test query"
        assert data["total_results"] == 1
        assert "gptram" in data["sources_queried"]
        assert len(data["results"]) == 1
        assert data["results"][0]["source"] == "gptram"

    def test_unified_search_invalid_source(self):
        """Test unified search with invalid source"""
        response = client.post("/search", json={"query": "test query", "k": 5, "sources": []})

        # Should fail with no sources
        assert response.status_code == 400

    def test_search_result_dataclass(self):
        """Test SearchResult dataclass creation"""
        result = SearchResult(
            source="gptram",
            score=0.85,
            key="test:key",
            text="Test text",
            meta={"author": "test"},
            ts=1700000000,
        )

        assert result.source == "gptram"
        assert result.score == 0.85
        assert result.key == "test:key"
        assert result.text == "Test text"
        assert result.meta["author"] == "test"
        assert result.ts == 1700000000

    def test_search_result_pnkln_fields(self):
        """Test SearchResult with PNKLN-specific fields"""
        result = SearchResult(
            source="pnkln",
            score=0.95,
            key="code:chunk:123",
            text="def optimize_inference():",
            repository="vllm",
            file_path="vllm/engine/llm_engine.py",
            chunk_id="chunk_123",
        )

        assert result.source == "pnkln"
        assert result.repository == "vllm"
        assert result.file_path == "vllm/engine/llm_engine.py"
        assert result.chunk_id == "chunk_123"


class TestRRFAlgorithm:
    """Test Reciprocal Rank Fusion algorithm details"""

    def test_rrf_score_calculation(self):
        """Test RRF score formula: 1/(K + rank)"""
        K_RRF = 60

        # Rank 1 result
        result1 = SearchResult(source="gptram", score=1.0, key="1", text="Result 1")
        # Rank 2 result
        result2 = SearchResult(source="gptram", score=0.9, key="2", text="Result 2")

        merged = merge_and_rank_results([result1, result2], [], k=10)

        # Check RRF scores
        expected_score_1 = 1.0 / (K_RRF + 1)
        expected_score_2 = 1.0 / (K_RRF + 2)

        assert abs(merged[0].score - expected_score_1) < 0.001
        assert abs(merged[1].score - expected_score_2) < 0.001

    def test_rrf_combines_sources_fairly(self):
        """Test that RRF gives fair weight to both sources"""
        # Both sources return same-ranked results
        gptram_results = [
            SearchResult(source="gptram", score=1.0, key="g1", text="GPTRAM result 1"),
        ]
        pnkln_results = [SearchResult(source="pnkln", score=1.0, key="p1", text="PNKLN result 1")]

        merged = merge_and_rank_results(gptram_results, pnkln_results, k=10)

        # Both should have equal RRF scores (both rank 1)
        K_RRF = 60
        expected_score = 1.0 / (K_RRF + 1)

        assert abs(merged[0].score - expected_score) < 0.001
        assert abs(merged[1].score - expected_score) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
