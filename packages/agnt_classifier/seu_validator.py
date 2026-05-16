# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""S.E.U. Prompt Conformance Validator (Risk #62).

Validates that all client-facing prompts follow the
Safety → Empathy → Utility ordering pattern.

S.E.U. ordering requires:
  1. Safety disclaimers/caveats appear FIRST
  2. Empathetic acknowledgments appear SECOND
  3. Utility (actionable content) appears LAST

This validator scans prompt templates and system messages
to ensure structural compliance.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


# ── S.E.U. Section Markers ────────────────────────────────────────────────

SAFETY_SIGNALS = frozenset(
  {
    "important",
    "warning",
    "caution",
    "note",
    "disclaimer",
    "please be aware",
    "consult",
    "not a substitute",
    "professional advice",
    "limitations",
    "cannot guarantee",
    "may not be accurate",
    "exercise caution",
    "do not",
    "must not",
    "security",
    "privacy",
    "confidential",
    "privilege",
    "attorney-client",
  }
)

EMPATHY_SIGNALS = frozenset(
  {
    "understand",
    "appreciate",
    "thank you",
    "i see",
    "that makes sense",
    "valid concern",
    "good question",
    "of course",
    "absolutely",
    "certainly",
    "happy to help",
    "glad to",
    "let me help",
    "i hear you",
    "acknowledg",
  }
)


class SEUSection(Enum):
  """Prompt section classification."""

  SAFETY = "SAFETY"
  EMPATHY = "EMPATHY"
  UTILITY = "UTILITY"
  UNKNOWN = "UNKNOWN"


@dataclass
class SEUViolation:
  """A detected S.E.U. ordering violation."""

  line_number: int
  section_found: SEUSection
  section_expected: SEUSection
  text_snippet: str
  source_file: str = ""


@dataclass
class SEUResult:
  """Result of S.E.U. conformance check."""

  is_compliant: bool
  violations: list[SEUViolation] = field(default_factory=list)
  sections_found: list[SEUSection] = field(default_factory=list)
  score: float = 1.0  # 0.0–1.0 conformance score


class SEUValidator:
  """Validates prompt text against S.E.U. ordering rules.

  Usage:
      validator = SEUValidator()
      result = validator.check(prompt_text)
      if not result.is_compliant:
          for v in result.violations:
              print(f"Line {v.line_number}: expected {v.section_expected}, found {v.section_found}")
  """

  def __init__(
    self,
    *,
    safety_signals: frozenset[str] | None = None,
    empathy_signals: frozenset[str] | None = None,
  ) -> None:
    self._safety = safety_signals or SAFETY_SIGNALS
    self._empathy = empathy_signals or EMPATHY_SIGNALS

  def classify_line(self, line: str) -> SEUSection:
    """Classify a single line into an S.E.U. section."""
    lower = line.lower().strip()
    if not lower:
      return SEUSection.UNKNOWN

    safety_hits = sum(1 for s in self._safety if s in lower)
    empathy_hits = sum(1 for s in self._empathy if s in lower)

    if safety_hits > empathy_hits and safety_hits > 0:
      return SEUSection.SAFETY
    if empathy_hits > safety_hits and empathy_hits > 0:
      return SEUSection.EMPATHY
    if lower:
      return SEUSection.UTILITY

    return SEUSection.UNKNOWN

  def check(self, text: str, *, source_file: str = "") -> SEUResult:
    """Check text for S.E.U. ordering compliance.

    Returns SEUResult with violations if ordering is wrong.
    """
    lines = text.strip().split("\n")
    sections: list[tuple[int, SEUSection, str]] = []

    for i, line in enumerate(lines, 1):
      section = self.classify_line(line)
      if section != SEUSection.UNKNOWN:
        sections.append((i, section, line[:80]))

    if not sections:
      return SEUResult(is_compliant=True, score=1.0)

    # Extract the ordered sequence of distinct sections
    seen_sections: list[SEUSection] = []
    for _, section, _ in sections:
      if not seen_sections or seen_sections[-1] != section:
        seen_sections.append(section)

    # Check ordering: S must come before E, E must come before U
    violations: list[SEUViolation] = []
    last_section_rank = -1
    section_order = {
      SEUSection.SAFETY: 0,
      SEUSection.EMPATHY: 1,
      SEUSection.UTILITY: 2,
    }

    for line_num, section, snippet in sections:
      rank = section_order.get(section, 99)
      if rank < last_section_rank:
        # Found a section that appears after a later-ranked section
        expected = [s for s, r in section_order.items() if r == last_section_rank][0]
        violations.append(
          SEUViolation(
            line_number=line_num,
            section_found=section,
            section_expected=expected,
            text_snippet=snippet,
            source_file=source_file,
          )
        )
      else:
        last_section_rank = max(last_section_rank, rank)

    total_sections = len(sections)
    violation_count = len(violations)
    score = max(0.0, 1.0 - (violation_count / max(total_sections, 1)))

    return SEUResult(
      is_compliant=len(violations) == 0,
      violations=violations,
      sections_found=seen_sections,
      score=round(score, 3),
    )

  def check_file(self, filepath: str | Path) -> SEUResult:
    """Check a file's contents for S.E.U. compliance."""
    path = Path(filepath)
    if not path.is_file():
      logger.warning("S.E.U. check: file not found: %s", path)
      return SEUResult(is_compliant=True, score=1.0)

    text = path.read_text(encoding="utf-8")
    return self.check(text, source_file=str(path))

  def scan_directory(
    self,
    directory: str | Path,
    *,
    glob_pattern: str = "**/*.md",
  ) -> dict[str, SEUResult]:
    """Scan a directory for prompt files and check each."""
    results: dict[str, SEUResult] = {}
    dir_path = Path(directory)
    if not dir_path.is_dir():
      return results

    for filepath in sorted(dir_path.glob(glob_pattern)):
      result = self.check_file(filepath)
      results[str(filepath)] = result

    return results


__all__ = [
  "EMPATHY_SIGNALS",
  "SAFETY_SIGNALS",
  "SEUResult",
  "SEUSection",
  "SEUValidator",
  "SEUViolation",
]
