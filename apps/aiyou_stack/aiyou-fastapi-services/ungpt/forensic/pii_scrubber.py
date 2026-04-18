"""PII Scrubber for Forensic Index

Removes personally identifiable information before indexing.
Uses pattern matching and optional Presidio integration.
"""

import re
from dataclasses import dataclass


@dataclass
class PIIMatch:
    """A detected PII match"""

    type: str
    value: str
    start: int
    end: int
    replacement: str


# PII patterns (regex-based, no ML dependency)
PII_PATTERNS = {
    # US Social Security Number
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    # Credit card numbers (basic)
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    # Email addresses
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    # Phone numbers (US format)
    "phone": r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    # IP addresses
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    # AWS keys (basic pattern)
    "aws_key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    # API keys (generic pattern)
    "api_key": r"\b(?:sk-|pk_|rk_)[A-Za-z0-9]{20,}\b",
    # Dates of birth (various formats)
    "dob": r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b",
}

# Replacement tokens
REPLACEMENTS = {
    "ssn": "[SSN_REDACTED]",
    "credit_card": "[CC_REDACTED]",
    "email": "[EMAIL_REDACTED]",
    "phone": "[PHONE_REDACTED]",
    "ip_address": "[IP_REDACTED]",
    "aws_key": "[AWS_KEY_REDACTED]",
    "api_key": "[API_KEY_REDACTED]",
    "dob": "[DOB_REDACTED]",
}


def scrub_pii(
    text: str,
    patterns: dict[str, str] | None = None,
    _return_matches: bool = False,
) -> tuple[str, list[PIIMatch]]:
    """Scrub PII from text using regex patterns.

    Args:
        text: Input text to scrub
        patterns: Optional custom patterns (defaults to PII_PATTERNS)
        return_matches: Whether to return match details

    Returns:
        Tuple of (scrubbed_text, list_of_matches)

    """
    if patterns is None:
        patterns = PII_PATTERNS

    matches = []
    scrubbed = text

    for pii_type, pattern in patterns.items():
        replacement = REPLACEMENTS.get(pii_type, f"[{pii_type.upper()}_REDACTED]")

        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(
                PIIMatch(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    replacement=replacement,
                ),
            )

        # Replace in scrubbed text
        scrubbed = re.sub(pattern, replacement, scrubbed, flags=re.IGNORECASE)

    return scrubbed, matches


def scrub_document(doc: dict) -> tuple[dict, dict]:
    """Scrub PII from a document dict.

    Args:
        doc: Document with text fields

    Returns:
        Tuple of (scrubbed_doc, pii_report)

    """
    text_fields = ["full_prompt", "reasoning_chain", "final_output", "code_blocks"]

    scrubbed_doc = doc.copy()
    pii_report = {"total_matches": 0, "by_type": {}, "by_field": {}}

    for field in text_fields:
        if doc.get(field):
            scrubbed_text, matches = scrub_pii(doc[field])
            scrubbed_doc[field] = scrubbed_text

            if matches:
                pii_report["total_matches"] += len(matches)
                pii_report["by_field"][field] = len(matches)

                for m in matches:
                    pii_report["by_type"][m.type] = pii_report["by_type"].get(m.type, 0) + 1

    scrubbed_doc["pii_scrubbed"] = pii_report["total_matches"] > 0

    return scrubbed_doc, pii_report


class PIIScrubber:
    """Stateful PII scrubber with statistics tracking."""

    def __init__(self, custom_patterns: dict[str, str] | None = None):
        self.patterns = {**PII_PATTERNS, **(custom_patterns or {})}
        self.stats = {
            "documents_processed": 0,
            "documents_with_pii": 0,
            "total_pii_found": 0,
            "by_type": {},
        }

    def scrub(self, text: str) -> str:
        """Scrub text and update stats"""
        scrubbed, matches = scrub_pii(text, self.patterns)

        self.stats["documents_processed"] += 1
        if matches:
            self.stats["documents_with_pii"] += 1
            self.stats["total_pii_found"] += len(matches)

            for m in matches:
                self.stats["by_type"][m.type] = self.stats["by_type"].get(m.type, 0) + 1

        return scrubbed

    def get_stats(self) -> dict:
        """Get scrubbing statistics"""
        return {
            **self.stats,
            "pii_rate": (
                self.stats["documents_with_pii"] / self.stats["documents_processed"]
                if self.stats["documents_processed"] > 0
                else 0
            ),
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "documents_processed": 0,
            "documents_with_pii": 0,
            "total_pii_found": 0,
            "by_type": {},
        }
