# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Eyecite integration for open-source legal citation parsing.

Eyecite (https://github.com/freelawproject/eyecite) is the gold standard
for extracting legal citations from text. It handles:
  - Full citations (e.g., "556 U.S. 662")
  - Short forms (e.g., "Id. at 12")
  - Supra references
  - Case names with parallel citations

This module bridges eyecite → CitationValidator pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedLegalCitation:
  """A legal citation extracted by eyecite.

  Attributes:
      raw_text: The raw citation text as found in the document.
      volume: Reporter volume number.
      reporter: Reporter abbreviation (e.g., "U.S.", "F.3d").
      page: Starting page number.
      year: Year of the decision (if found).
      court: Court name (if found).
      pin_cite: Pin citation page (if any).
      citation_type: Type: "full", "short", "supra", "id".
      matched_text: Full matched text including surrounding context.
  """

  raw_text: str = ""
  volume: str = ""
  reporter: str = ""
  page: str = ""
  year: str = ""
  court: str = ""
  pin_cite: str = ""
  citation_type: str = "full"
  matched_text: str = ""


def extract_citations(text: str) -> list[ParsedLegalCitation]:
  """Extract all legal citations from text using eyecite.

  Args:
      text: Legal text to parse.

  Returns:
      List of ParsedLegalCitation objects.
  """
  try:
    from eyecite import get_citations
    from eyecite.models import (
      FullCaseCitation,
      IdCitation,
      ShortCaseCitation,
      SupraCitation,
    )
  except ImportError:
    logger.warning("eyecite not installed. Run: uv pip install eyecite")
    return []

  results: list[ParsedLegalCitation] = []

  try:
    citations = get_citations(text)
  except Exception:
    logger.exception("eyecite parsing failed")
    return []

  for cite in citations:
    parsed = ParsedLegalCitation(matched_text=str(cite))

    if isinstance(cite, FullCaseCitation):
      parsed.citation_type = "full"
      parsed.volume = str(cite.groups.get("volume", ""))
      parsed.reporter = str(cite.groups.get("reporter", ""))
      parsed.page = str(cite.groups.get("page", ""))
      parsed.year = str(cite.groups.get("year", ""))
      parsed.court = str(cite.groups.get("court", ""))
      parsed.pin_cite = str(cite.metadata.pin_cite or "")
      parsed.raw_text = cite.matched_text()

    elif isinstance(cite, ShortCaseCitation):
      parsed.citation_type = "short"
      parsed.volume = str(cite.groups.get("volume", ""))
      parsed.reporter = str(cite.groups.get("reporter", ""))
      parsed.page = str(cite.groups.get("page", ""))
      parsed.raw_text = cite.matched_text()

    elif isinstance(cite, IdCitation):
      parsed.citation_type = "id"
      parsed.raw_text = cite.matched_text()
      parsed.pin_cite = str(cite.metadata.pin_cite or "")

    elif isinstance(cite, SupraCitation):
      parsed.citation_type = "supra"
      parsed.raw_text = cite.matched_text()

    else:
      parsed.citation_type = "unknown"
      parsed.raw_text = str(cite)

    results.append(parsed)

  logger.info(
    "eyecite: extracted %d citations (%d full, %d short, %d id, %d supra)",
    len(results),
    sum(1 for r in results if r.citation_type == "full"),
    sum(1 for r in results if r.citation_type == "short"),
    sum(1 for r in results if r.citation_type == "id"),
    sum(1 for r in results if r.citation_type == "supra"),
  )

  return results


def extract_and_resolve(text: str) -> list[ParsedLegalCitation]:
  """Extract citations and resolve short forms to their antecedents.

  Uses eyecite's resolve_citations to link "Id." and short forms
  back to their full citation antecedents.

  Args:
      text: Legal text to parse.

  Returns:
      List of ParsedLegalCitation with resolved references.
  """
  try:
    from eyecite import get_citations, resolve_citations
  except ImportError:
    logger.warning("eyecite not installed")
    return []

  try:
    citations = get_citations(text)
    resolved = resolve_citations(citations)
  except Exception:
    logger.exception("eyecite resolution failed")
    return extract_citations(text)

  results: list[ParsedLegalCitation] = []
  for cite in resolved:
    parsed = ParsedLegalCitation(
      raw_text=cite.matched_text() if hasattr(cite, "matched_text") else str(cite),
      matched_text=str(cite),
    )
    results.append(parsed)

  return results
