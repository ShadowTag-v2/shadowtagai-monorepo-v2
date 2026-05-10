# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for deep_research.synthesis module."""

from __future__ import annotations

from deep_research.synthesis import (
  ActionItem,
  Finding,
  synthesize_findings,
)


class TestFinding:
  def test_defaults(self) -> None:
    f = Finding(content="test", source="web")
    assert f.confidence == 0.8
    assert f.tags == []
    assert f.references == []


class TestActionItem:
  def test_defaults(self) -> None:
    a = ActionItem(description="Do the thing")
    assert a.priority == 1
    assert a.dependencies == []


class TestSynthesizeFindings:
  def test_empty_findings(self) -> None:
    result = synthesize_findings([], objective="test")
    assert result.confidence == 0.0
    assert result.action_items == []
    assert "No findings" in result.summary

  def test_single_finding(self) -> None:
    findings = [Finding(content="We should implement caching", source="docs")]
    result = synthesize_findings(findings, objective="Cache layer")
    assert result.confidence > 0.0
    assert result.total_sources == 1
    assert "Cache layer" in result.summary

  def test_action_extraction_should(self) -> None:
    findings = [
      Finding(
        content="You should implement rate limiting for all API endpoints to prevent abuse.",
        source="docs",
      )
    ]
    result = synthesize_findings(findings, objective="Security")
    assert len(result.action_items) >= 1

  def test_action_extraction_must(self) -> None:
    findings = [
      Finding(
        content="You must validate all inputs using Pydantic before processing.",
        source="security",
      )
    ]
    result = synthesize_findings(findings, objective="Security")
    p1_actions = [a for a in result.action_items if a.priority == 1]
    assert len(p1_actions) >= 1

  def test_multi_source_confidence_boost(self) -> None:
    findings = [
      Finding(content="Pattern A is good", source="docs", confidence=0.8),
      Finding(content="Pattern A confirmed", source="web", confidence=0.8),
      Finding(content="Pattern A verified", source="local", confidence=0.8),
    ]
    result = synthesize_findings(findings, objective="Test")
    assert result.confidence > 0.8  # Diversity bonus applied

  def test_confidence_capped_at_one(self) -> None:
    findings = [
      Finding(content="x", source=f"s{i}", confidence=0.99) for i in range(10)
    ]
    result = synthesize_findings(findings, objective="Cap test")
    assert result.confidence <= 1.0

  def test_recommendations_from_high_confidence(self) -> None:
    findings = [
      Finding(content="Use Cloud Run for deployment", source="docs", confidence=0.95)
    ]
    result = synthesize_findings(findings, objective="Deploy")
    high_conf = [r for r in result.recommendations if "HIGH CONFIDENCE" in r]
    assert len(high_conf) >= 1

  def test_recommendations_capped_at_ten(self) -> None:
    findings = [
      Finding(content=f"Must do thing {i} immediately.", source="sec", confidence=0.95)
      for i in range(20)
    ]
    result = synthesize_findings(findings, objective="Cap")
    assert len(result.recommendations) <= 10

  def test_dedup_by_prefix(self) -> None:
    findings = [
      Finding(
        content="You should implement caching for performance. Details follow.",
        source="a",
      ),
      Finding(
        content="You should implement caching for performance. More info.", source="b"
      ),
    ]
    result = synthesize_findings(findings, objective="Dedup")
    descs = [a.description[:50] for a in result.action_items]
    assert len(set(descs)) == len(descs)

  def test_metadata_passthrough(self) -> None:
    result = synthesize_findings([], objective="meta", metadata={"k": "v"})
    assert result.metadata == {"k": "v"}

  def test_summary_groups_by_source(self) -> None:
    findings = [
      Finding(content="From docs", source="docs"),
      Finding(content="From web", source="web"),
    ]
    result = synthesize_findings(findings, objective="Group")
    assert "docs" in result.summary
    assert "web" in result.summary
