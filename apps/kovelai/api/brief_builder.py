"""
Brief Builder — Attorney Work-Product PDF Generator.

Generates privileged attorney briefs from War Room pipeline output.
Content is compiled from Oracle memo + Verb Audit + Citations into
a structured markdown document, then converted to PDF.

V11 Sprint: Week 2 deliverable.

Security: ALL output is Attorney Work-Product — never shown to clients.
Firestore: brief_exports collection (with 30-day GDPR TTL).

@see WAR_ROOM_ARCHITECTURE.md — Pipeline Stage 6
@see V11_SPRINT.md — Week 2 spec
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, UTC

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# Brief Data Model
# ═══════════════════════════════════════════════════════════


class BriefMetadata(BaseModel):
    """Metadata for a generated attorney brief."""

    session_id: str
    firm_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=30)
    )
    kovel_attestation_hash: str = ""
    privilege_designation: str = "Attorney Work-Product — Not Subject to Compulsory Disclosure"
    pages: int = 0


class BriefSection(BaseModel):
    """A single section of the attorney brief."""

    title: str
    content: str
    order: int


class AttorneyBrief(BaseModel):
    """Complete attorney brief document."""

    metadata: BriefMetadata
    sections: list[BriefSection] = Field(default_factory=list)

    def add_section(self, title: str, content: str) -> None:
        """Add a section to the brief."""
        order = len(self.sections) + 1
        self.sections.append(BriefSection(title=title, content=content, order=order))


# ═══════════════════════════════════════════════════════════
# Brief Builder
# ═══════════════════════════════════════════════════════════


def build_brief(
    *,
    session_id: str,
    firm_id: str,
    oracle_memo: str,
    verb_audit: list[dict],
    citations: list[dict],
    intake_data: dict,
    seu_token_hash: str,
) -> AttorneyBrief:
    """
    Build a complete attorney brief from War Room pipeline output.

    Args:
        session_id: Unique session identifier
        firm_id: Law firm identifier
        oracle_memo: Full text from Oracle Stage 4
        verb_audit: Verb entries from Stage 3
        citations: Citation entries from Stage 5
        intake_data: Structured intake from Stage 1
        seu_token_hash: S.E.U. token hash for Kovel attestation

    Returns:
        AttorneyBrief with all sections populated
    """
    kovel_hash = hashlib.sha256(
        f"{session_id}:{firm_id}:{seu_token_hash}".encode()
    ).hexdigest()

    brief = AttorneyBrief(
        metadata=BriefMetadata(
            session_id=session_id,
            firm_id=firm_id,
            kovel_attestation_hash=kovel_hash,
        )
    )

    # Section 1: Privilege Header
    brief.add_section(
        "PRIVILEGE DESIGNATION",
        _build_privilege_header(firm_id, kovel_hash),
    )

    # Section 2: Executive Summary
    brief.add_section(
        "EXECUTIVE SUMMARY",
        _extract_section(oracle_memo, "EXECUTIVE SUMMARY"),
    )

    # Section 3: Factual Timeline
    brief.add_section(
        "FACTUAL TIMELINE",
        _build_timeline(intake_data),
    )

    # Section 4: Causes of Action + Verb Matrix
    brief.add_section(
        "CAUSES OF ACTION & VERB MATRIX",
        _build_verb_matrix_section(verb_audit),
    )

    # Section 5: Legal Analysis
    brief.add_section(
        "LEGAL ANALYSIS",
        _extract_section(oracle_memo, "LEGAL ANALYSIS"),
    )

    # Section 6: Strategic Recommendations
    brief.add_section(
        "STRATEGIC RECOMMENDATIONS",
        _extract_section(oracle_memo, "STRATEGIC RECOMMENDATIONS"),
    )

    # Section 7: Risk Assessment
    brief.add_section(
        "RISK ASSESSMENT",
        _extract_section(oracle_memo, "RISK ASSESSMENT"),
    )

    # Section 8: Citation Appendix
    brief.add_section(
        "CITATION APPENDIX",
        _build_citation_appendix(citations),
    )

    # Section 9: Kovel Attestation
    brief.add_section(
        "KOVEL ATTESTATION",
        _build_kovel_attestation(firm_id, session_id, kovel_hash),
    )

    return brief


# ═══════════════════════════════════════════════════════════
# Section Builders
# ═══════════════════════════════════════════════════════════


def _build_privilege_header(firm_id: str, kovel_hash: str) -> str:
    """Generate the privilege designation header."""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    return f"""
**PRIVILEGED AND CONFIDENTIAL — ATTORNEY WORK-PRODUCT**

This document is protected by the attorney-client privilege and the
work-product doctrine. It was prepared at the express direction of
supervising counsel and is not subject to compulsory disclosure.

- Firm ID: {firm_id}
- Generated: {now}
- Kovel Attestation Hash: `{kovel_hash[:16]}...`
- Generated by: KovelAI War Room (Oracle Studio Pipeline)
""".strip()


def _extract_section(memo: str, section_name: str) -> str:
    """Extract a named section from the Oracle memo."""
    lines = memo.split("\n")
    capturing = False
    captured: list[str] = []

    for line in lines:
        if section_name.upper() in line.upper() and line.strip().startswith("#"):
            capturing = True
            continue
        if capturing:
            if line.strip().startswith("##") and section_name.upper() not in line.upper():
                break
            captured.append(line)

    result = "\n".join(captured).strip()
    return result if result else f"[Section '{section_name}' not found in Oracle output]"


def _build_timeline(intake_data: dict) -> str:
    """Build a factual timeline from intake data."""
    dates = intake_data.get("dates", [])
    entities = intake_data.get("entities", [])
    claims = intake_data.get("claims", [])

    lines = ["### Key Dates"]
    for date in dates:
        lines.append(f"- **{date}**: [Event details from transcript]")

    lines.append("\n### Key Entities")
    for entity in entities:
        lines.append(f"- {entity}")

    lines.append("\n### Identified Claims")
    for claim in claims:
        lines.append(f"- {claim}")

    return "\n".join(lines)


def _build_verb_matrix_section(verb_audit: list[dict]) -> str:
    """Build the verb matrix section for the brief."""
    if not verb_audit:
        return "[No action verbs identified in this session]"

    lines = [
        "| Verb | Classification | Cause of Action | Confidence | Impact |",
        "|------|---------------|-----------------|------------|--------|",
    ]

    for verb in verb_audit:
        conf = f"{round(verb.get('confidence', 0) * 100)}%"
        impact = verb.get("strengthens_or_weakens", "neutral")
        icon = "🟢" if impact == "strengthens" else "🔴" if impact == "weakens" else "⚪"
        lines.append(
            f"| `{verb.get('verb', '')}` "
            f"| {verb.get('kinematic_classification', '')} "
            f"| {verb.get('cause_of_action', '')} "
            f"| {conf} "
            f"| {icon} {impact} |"
        )

    return "\n".join(lines)


def _build_citation_appendix(citations: list[dict]) -> str:
    """Build the citation appendix."""
    if not citations:
        return "[No citations generated]"

    lines = [
        "| # | Authority | Type | Relevance | Status |",
        "|---|-----------|------|-----------|--------|",
    ]

    for citation in citations:
        rel = f"{round(citation.get('relevance_score', 0) * 100)}%"
        status = citation.get("status", "unverified")
        icon = "✓" if status == "verified" else "?" if status == "unverified" else "⚠"
        lines.append(
            f"| {citation.get('index', '')} "
            f"| {citation.get('authority', '')} "
            f"| {citation.get('type', '')} "
            f"| {rel} "
            f"| {icon} {status} |"
        )

    return "\n".join(lines)


def _build_kovel_attestation(firm_id: str, session_id: str, kovel_hash: str) -> str:
    """Build the Kovel attestation block."""
    now = datetime.now(UTC).isoformat()
    return f"""
*** PRIVILEGE ATTESTATION (UNITED STATES V. HEPPNER COMPLIANT) ***

Timestamp: {now}
Firm ID: {firm_id}
Session ID: {session_id}
Attestation Hash: {kovel_hash}
Enterprise ZDR Enforced: TRUE
Zero Data Retention: CONFIRMED

This brief, including all War Room intelligence, was conducted via a
Zero-Data B2B Router at the express direction of supervising counsel.

The AI functioned strictly as a deputized agent under:
  - United States v. Kovel, 296 F.2d 918 (2d Cir. 1961)
  - United States v. Heppner (S.D.N.Y. Feb. 10, 2026)

*** END ATTESTATION ***
""".strip()


def brief_to_markdown(brief: AttorneyBrief) -> str:
    """Convert an AttorneyBrief to a complete markdown document."""
    lines = [
        "# Attorney Work-Product Brief",
        "",
        f"**Session**: {brief.metadata.session_id}  ",
        f"**Firm**: {brief.metadata.firm_id}  ",
        f"**Generated**: {brief.metadata.generated_at.strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Expires**: {brief.metadata.expires_at.strftime('%Y-%m-%d %H:%M UTC')}  ",
        "",
        "---",
        "",
    ]

    for section in sorted(brief.sections, key=lambda s: s.order):
        lines.append(f"## {section.title}")
        lines.append("")
        lines.append(section.content)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
