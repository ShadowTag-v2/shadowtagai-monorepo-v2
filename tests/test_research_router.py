# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for deep_research.research_router module."""

from __future__ import annotations

from deep_research.research_router import (
  QuerySource,
  ResearchQuery,
  classify_query,
  create_batch_queries,
  route_query,
)


class TestQuerySource:
  def test_all_sources_present(self) -> None:
    expected = {
      "google-developer-knowledge",
      "sequential-thinking",
      "web-search",
      "local-codebase",
      "chrome-devtools-mcp",
      "stitch-mcp",
      "firebase-mcp-server",
    }
    assert {s.value for s in QuerySource} == expected

  def test_string_enum(self) -> None:
    assert QuerySource.WEB_SEARCH == "web-search"


class TestResearchQuery:
  def test_defaults(self) -> None:
    rq = ResearchQuery(query="test", source=QuerySource.WEB_SEARCH)
    assert rq.priority == 1
    assert rq.classified_by == "manual"

  def test_to_dict_truncates(self) -> None:
    rq = ResearchQuery(query="x" * 300, source=QuerySource.WEB_SEARCH)
    assert len(rq.to_dict()["query"]) == 200


class TestClassifyQuery:
  def test_firebase_auth(self) -> None:
    assert classify_query("configure firebase auth") == QuerySource.FIREBASE_MCP

  def test_firestore_rules(self) -> None:
    assert classify_query("firestore rules for collection") == QuerySource.FIREBASE_MCP

  def test_google_cloud(self) -> None:
    assert (
      classify_query("Google Cloud Run best practices")
      == QuerySource.GOOGLE_DEVELOPER_KNOWLEDGE
    )

  def test_vertex_ai(self) -> None:
    assert (
      classify_query("Vertex AI pipeline") == QuerySource.GOOGLE_DEVELOPER_KNOWLEDGE
    )

  def test_local_find_file(self) -> None:
    assert classify_query("Find function in file auth.py") == QuerySource.LOCAL_CODEBASE

  def test_local_existing(self) -> None:
    assert (
      classify_query("Show me existing implementation") == QuerySource.LOCAL_CODEBASE
    )

  def test_thinking_tradeoff(self) -> None:
    assert (
      classify_query("Compare tradeoffs, break down pros and cons")
      == QuerySource.SEQUENTIAL_THINKING
    )

  def test_thinking_hypothesis(self) -> None:
    assert (
      classify_query("Verify the hypothesis about caching")
      == QuerySource.SEQUENTIAL_THINKING
    )

  def test_web_search_fallback(self) -> None:
    assert classify_query("weather in Tokyo") == QuerySource.WEB_SEARCH

  def test_empty_fallback(self) -> None:
    assert classify_query("") == QuerySource.WEB_SEARCH

  def test_firebase_beats_google_dev(self) -> None:
    # "firebase auth" matches Firebase; "firebase hosting" is unambiguous.
    assert classify_query("firebase hosting deployment") == QuerySource.FIREBASE_MCP


class TestRouteQuery:
  def test_classified_by(self) -> None:
    assert route_query("firebase hosting").classified_by == "auto_router"

  def test_kwargs_pass_through(self) -> None:
    rq = route_query("firebase hosting", priority=5, max_results=3)
    assert rq.priority == 5
    assert rq.max_results == 3


class TestCreateBatchQueries:
  def test_returns_sorted(self) -> None:
    batch = create_batch_queries(["firebase auth", "weather"], default_priority=2)
    assert len(batch) == 2
    assert all(rq.priority == 2 for rq in batch)

  def test_empty_list(self) -> None:
    assert create_batch_queries([]) == []
