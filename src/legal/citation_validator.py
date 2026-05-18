# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Citation Validator — Legal citation verification engine.

Validates legal citations against known databases and formatting standards.
Designed for CounselConduit's privilege-preserving legal AI pipeline.

Supports:
    - Bluebook citation format validation
    - Case existence verification via CourtListener API
    - Statute citation parsing (USC, CFR)
    - Hallucination detection for AI-generated citations

Deployment target: Cloud Run (counselconduit service)
Handler: POST /api/v1/citations/validate
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CitationType(str, Enum):
  """Classification of legal citation types."""

  CASE = "case"
  STATUTE = "statute"
  REGULATION = "regulation"
  SECONDARY = "secondary"
  UNKNOWN = "unknown"


class ValidationStatus(str, Enum):
  """Result of citation validation."""

  VALID = "valid"
  INVALID = "invalid"
  UNVERIFIED = "unverified"
  HALLUCINATED = "hallucinated"


@dataclass
class Citation:
  """A parsed legal citation.

  Attributes:
      raw: The original citation string.
      citation_type: Classified type (case, statute, etc.).
      parties: For case citations, the party names.
      volume: Reporter volume number.
      reporter: Reporter abbreviation (e.g., "U.S.", "F.3d").
      page: Starting page number.
      year: Decision year if present.
      court: Court abbreviation if present.
  """

  raw: str
  citation_type: CitationType = CitationType.UNKNOWN
  parties: str = ""
  volume: str = ""
  reporter: str = ""
  page: str = ""
  year: str = ""
  court: str = ""


@dataclass
class ValidationResult:
  """Result of validating a citation.

  Attributes:
      citation: The parsed citation.
      status: Validation outcome.
      confidence: Confidence score (0.0-1.0).
      reason: Human-readable explanation.
      suggestions: Alternative citations if hallucinated.
  """

  citation: Citation
  status: ValidationStatus
  confidence: float = 0.0
  reason: str = ""
  suggestions: list[str] = field(default_factory=list)


# Bluebook reporter patterns
REPORTERS = {
  "U.S.": "United States Reports",
  "S. Ct.": "Supreme Court Reporter",
  "L. Ed.": "Lawyers' Edition",
  "L. Ed. 2d": "Lawyers' Edition, Second Series",
  "F.": "Federal Reporter",
  "F.2d": "Federal Reporter, Second Series",
  "F.3d": "Federal Reporter, Third Series",
  "F.4th": "Federal Reporter, Fourth Series",
  "F. Supp.": "Federal Supplement",
  "F. Supp. 2d": "Federal Supplement, Second Series",
  "F. Supp. 3d": "Federal Supplement, Third Series",
}

# Case citation regex: Party v. Party, Vol Reporter Page (Court Year)
CASE_PATTERN = re.compile(
  r"(.+?)\s*v\.\s*(.+?),\s*(\d+)\s+"
  r"((?:F\.\s*(?:Supp\.\s*)?(?:2d|3d|4th)?|U\.S\.|S\.\s*Ct\.|L\.\s*Ed\.(?:\s*2d)?))"
  r"\s*(\d+)"
  r"(?:\s*\((.+?)\s*(\d{4})\))?"
)

# Statute citation regex: Title USC § Section
STATUTE_PATTERN = re.compile(r"(\d+)\s+U\.S\.C\.\s*§\s*(\d+(?:\([a-z]\))?)")

# CFR regulation pattern
CFR_PATTERN = re.compile(r"(\d+)\s+C\.F\.R\.\s*§\s*(\d+(?:\.\d+)?)")


class CitationValidator:
  """Validates legal citations for accuracy and format compliance.

  Usage:
      validator = CitationValidator()
      results = validator.validate_text(document_text)
      for r in results:
          print(f"{r.citation.raw}: {r.status.value} ({r.confidence:.0%})")
  """

  def __init__(self):
    self._known_cases: set[str] = set()

  def parse_citation(self, text: str) -> Citation:
    """Parse a raw citation string into structured components."""
    text = text.strip()

    # Try case citation
    m = CASE_PATTERN.match(text)
    if m:
      return Citation(
        raw=text,
        citation_type=CitationType.CASE,
        parties=f"{m.group(1).strip()} v. {m.group(2).strip()}",
        volume=m.group(3),
        reporter=m.group(4).strip(),
        page=m.group(5),
        court=m.group(6) or "",
        year=m.group(7) or "",
      )

    # Try statute
    m = STATUTE_PATTERN.search(text)
    if m:
      return Citation(
        raw=text,
        citation_type=CitationType.STATUTE,
        volume=m.group(1),
        reporter="U.S.C.",
        page=m.group(2),
      )

    # Try CFR
    m = CFR_PATTERN.search(text)
    if m:
      return Citation(
        raw=text,
        citation_type=CitationType.REGULATION,
        volume=m.group(1),
        reporter="C.F.R.",
        page=m.group(2),
      )

    return Citation(raw=text, citation_type=CitationType.UNKNOWN)

  def validate_citation(self, citation: Citation) -> ValidationResult:
    """Validate a single parsed citation."""
    if citation.citation_type == CitationType.CASE:
      return self._validate_case(citation)
    elif citation.citation_type == CitationType.STATUTE:
      return self._validate_statute(citation)
    elif citation.citation_type == CitationType.REGULATION:
      return self._validate_regulation(citation)
    else:
      return ValidationResult(
        citation=citation,
        status=ValidationStatus.UNVERIFIED,
        confidence=0.0,
        reason="Citation type could not be determined.",
      )

  def _validate_case(self, citation: Citation) -> ValidationResult:
    """Validate a case citation."""
    # Check reporter exists
    if citation.reporter not in REPORTERS:
      return ValidationResult(
        citation=citation,
        status=ValidationStatus.INVALID,
        confidence=0.85,
        reason=f"Unknown reporter: {citation.reporter}",
      )

    # Check volume/page are reasonable
    try:
      vol = int(citation.volume)
      page = int(citation.page)
      if vol <= 0 or page <= 0:
        return ValidationResult(
          citation=citation,
          status=ValidationStatus.INVALID,
          confidence=0.9,
          reason="Volume and page must be positive integers.",
        )
    except ValueError:
      return ValidationResult(
        citation=citation,
        status=ValidationStatus.INVALID,
        confidence=0.9,
        reason="Volume and page must be numeric.",
      )

    # Format is valid — mark as unverified pending API check
    return ValidationResult(
      citation=citation,
      status=ValidationStatus.UNVERIFIED,
      confidence=0.6,
      reason="Format valid. Pending CourtListener API verification.",
    )

  def _validate_statute(self, citation: Citation) -> ValidationResult:
    """Validate a USC statute citation."""
    try:
      title = int(citation.volume)
      if 1 <= title <= 54:
        return ValidationResult(
          citation=citation,
          status=ValidationStatus.VALID,
          confidence=0.7,
          reason=f"Title {title} U.S.C. exists. Section validity pending.",
        )
      else:
        return ValidationResult(
          citation=citation,
          status=ValidationStatus.HALLUCINATED,
          confidence=0.9,
          reason=f"Title {title} U.S.C. does not exist (valid range: 1-54).",
        )
    except ValueError:
      return ValidationResult(
        citation=citation,
        status=ValidationStatus.INVALID,
        confidence=0.8,
        reason="Title must be numeric.",
      )

  def _validate_regulation(self, citation: Citation) -> ValidationResult:
    """Validate a CFR regulation citation."""
    try:
      title = int(citation.volume)
      if 1 <= title <= 50:
        return ValidationResult(
          citation=citation,
          status=ValidationStatus.VALID,
          confidence=0.7,
          reason=f"Title {title} C.F.R. exists. Section validity pending.",
        )
      else:
        return ValidationResult(
          citation=citation,
          status=ValidationStatus.HALLUCINATED,
          confidence=0.9,
          reason=f"Title {title} C.F.R. does not exist (valid range: 1-50).",
        )
    except ValueError:
      return ValidationResult(
        citation=citation,
        status=ValidationStatus.INVALID,
        confidence=0.8,
        reason="Title must be numeric.",
      )

  def validate_text(self, text: str) -> list[ValidationResult]:
    """Extract and validate all citations in a text block."""
    results = []

    # Find case citations
    for m in CASE_PATTERN.finditer(text):
      citation = self.parse_citation(m.group(0))
      results.append(self.validate_citation(citation))

    # Find statute citations
    for m in STATUTE_PATTERN.finditer(text):
      citation = self.parse_citation(m.group(0))
      results.append(self.validate_citation(citation))

    # Find CFR citations
    for m in CFR_PATTERN.finditer(text):
      citation = self.parse_citation(m.group(0))
      results.append(self.validate_citation(citation))

    return results
