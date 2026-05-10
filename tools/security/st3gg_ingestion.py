# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ST3GG Unwrapper: Steganographic Prompt Injection Detection

Detects and strips hidden prompt injections embedded in:
- Unicode zero-width characters (U+200B, U+200C, U+200D, U+FEFF)
- Invisible markdown directives
- Base64-encoded payloads in comments
- Homoglyph substitution attacks (Cyrillic/Latin lookalikes)

Part of the 17-Layer DOW CRSMC Shield architecture.
"""

from __future__ import annotations

import base64
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Zero-width Unicode characters used for steganographic encoding
ZERO_WIDTH_CHARS = {
  "\u200b",  # Zero-width space
  "\u200c",  # Zero-width non-joiner
  "\u200d",  # Zero-width joiner
  "\ufeff",  # Zero-width no-break space (BOM)
  "\u2060",  # Word joiner
  "\u2061",  # Function application
  "\u2062",  # Invisible times
  "\u2063",  # Invisible separator
  "\u2064",  # Invisible plus
}

# Cyrillic homoglyphs that mimic Latin characters
HOMOGLYPH_MAP = {
  "А": "A",
  "В": "B",
  "С": "C",
  "Е": "E",
  "Н": "H",
  "К": "K",
  "М": "M",
  "О": "O",
  "Р": "P",
  "Т": "T",
  "Х": "X",
  "а": "a",
  "с": "c",
  "е": "e",
  "о": "o",
  "р": "p",
  "х": "x",
  "у": "y",
}

# Patterns that indicate hidden prompt injection
INJECTION_PATTERNS = [
  re.compile(r"<!--\s*system\s*:", re.IGNORECASE),
  re.compile(r"<\|im_start\|>", re.IGNORECASE),
  re.compile(r"<\|endoftext\|>", re.IGNORECASE),
  re.compile(r"\[INST\]", re.IGNORECASE),
  re.compile(r"```\s*system", re.IGNORECASE),
  re.compile(r"<system>", re.IGNORECASE),
]


@dataclass
class ScanResult:
  """Result of a steganographic scan."""

  clean_text: str
  threats_found: int
  threat_details: list[str]
  zero_width_count: int
  homoglyphs_found: int
  injections_found: int


def strip_zero_width(text: str) -> tuple[str, int]:
  """Remove all zero-width Unicode characters.

  Returns:
      Tuple of (cleaned text, count of removed characters).
  """
  count = sum(1 for c in text if c in ZERO_WIDTH_CHARS)
  cleaned = "".join(c for c in text if c not in ZERO_WIDTH_CHARS)
  return cleaned, count


def detect_homoglyphs(text: str) -> tuple[str, int]:
  """Replace Cyrillic homoglyphs with Latin equivalents.

  Returns:
      Tuple of (normalized text, count of substitutions).
  """
  count = 0
  chars = []
  for c in text:
    if c in HOMOGLYPH_MAP:
      chars.append(HOMOGLYPH_MAP[c])
      count += 1
    else:
      chars.append(c)
  return "".join(chars), count


def detect_hidden_base64(text: str) -> list[str]:
  """Find base64-encoded payloads hidden in comments or whitespace."""
  threats = []
  # HTML/markdown comments with base64
  for match in re.finditer(r"<!--\s*([A-Za-z0-9+/=]{20,})\s*-->", text):
    try:
      decoded = base64.b64decode(match.group(1)).decode("utf-8", errors="ignore")
      if any(kw in decoded.lower() for kw in ("system", "ignore", "instruction")):
        threats.append(f"Base64 injection: {decoded[:100]}")
    except Exception:
      pass
  return threats


def detect_injection_patterns(text: str) -> list[str]:
  """Detect known prompt injection patterns."""
  threats = []
  for pattern in INJECTION_PATTERNS:
    for match in pattern.finditer(text):
      threats.append(f"Injection pattern: {match.group()[:80]}")
  return threats


def scan_and_clean(text: str) -> ScanResult:
  """Perform full steganographic scan and cleaning.

  Args:
      text: Input text to scan.

  Returns:
      ScanResult with cleaned text and threat details.
  """
  threats: list[str] = []

  # Phase 1: Strip zero-width characters
  cleaned, zw_count = strip_zero_width(text)
  if zw_count > 0:
    threats.append(f"Removed {zw_count} zero-width characters")

  # Phase 2: Detect homoglyphs
  cleaned, hg_count = detect_homoglyphs(cleaned)
  if hg_count > 0:
    threats.append(f"Normalized {hg_count} Cyrillic homoglyphs")

  # Phase 3: Check for hidden base64
  b64_threats = detect_hidden_base64(cleaned)
  threats.extend(b64_threats)

  # Phase 4: Check for injection patterns
  inj_threats = detect_injection_patterns(cleaned)
  threats.extend(inj_threats)
  # Remove injection patterns from cleaned text
  for pattern in INJECTION_PATTERNS:
    cleaned = pattern.sub("[REDACTED]", cleaned)

  if threats:
    logger.warning(
      "ST3GG threats detected",
      extra={"count": len(threats), "details": threats[:5]},
    )

  return ScanResult(
    clean_text=cleaned,
    threats_found=len(threats),
    threat_details=threats,
    zero_width_count=zw_count,
    homoglyphs_found=hg_count,
    injections_found=len(inj_threats),
  )
