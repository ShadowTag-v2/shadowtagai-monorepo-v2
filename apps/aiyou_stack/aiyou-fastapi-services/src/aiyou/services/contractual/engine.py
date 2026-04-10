"""
Contractual Service Engine
"The Digital Napkin" / "The AI Lawyer"

Implements the core logic for:
1. Ingesting negotiation transcripts.
2. Analyzing for legal risk (Ironwood).
3. Memorializing to Universal Tape (Scribe).
"""

import logging
from datetime import datetime
from typing import Any

# Antigravity OS Components
from src.antigravity.ironwood_mcp import log_event

# ideally we would import IronwoodGemini here for inference,
# for now we simulate the 'Lawyer Meter' logic.

logger = logging.getLogger(__name__)


class ContractualEngine:
    """
    The brain of the Contractual product.
    Analyses text streams for binding agreement terms.
    """

    def __init__(self):
        self.version = "Contractual-1.0-Alpha"

    async def analyze_transcript(self, transcript: str, location: str = "US-CA") -> dict[str, Any]:
        """
        The 'Lawyer Meter': Analyzes a conversation for legal bindingness and risks.
        """
        # 1. Log the 'Input' to Universal Tape (Immutable Record)
        log_event(
            source="Contractual-Engine",
            event_type="transcript_ingest",
            content=f"Location: {location} || Length: {len(transcript)} chars",
        )

        # 2. Extract Terms (Simulated Ironwood Extraction)
        # In production -> await ironwood.generate(transcript, prompt="Extract terms...")
        terms = self._extract_terms_heuristic(transcript)

        # 3. Assess Risk
        risk_score = self._calculate_risk(terms, location)

        # 4. Generate 'The Digital Napkin' (Summary)
        summary = self._generate_napkin(terms)

        # 5. Log the 'Output'
        log_event(
            source="Contractual-Engine",
            event_type="analysis_complete",
            content=f"Risk: {risk_score} || Terms: {len(terms)}",
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "location": location,
            "risk_score": risk_score,  # 0.0 (Safe) to 1.0 (Litigation Bait)
            "terms": terms,
            "digital_napkin": summary,
        }

    def _extract_terms_heuristic(self, text: str) -> list[dict[str, str]]:
        """
        Simple heuristic extraction for Alpha.
        Attributes sentences to 'Vendor' or 'Client'.
        """
        # Placeholder logic
        terms = []
        lines = text.split("\n")
        for line in lines:
            if "price" in line.lower() or "$" in line:
                terms.append({"type": "financial", "content": line})
            elif "deadline" in line.lower() or "date" in line.lower():
                terms.append({"type": "timeline", "content": line})
            elif "agree" in line.lower():
                terms.append({"type": "assent", "content": line})
        return terms

    def _calculate_risk(self, terms: list[dict[str, str]], location: str) -> float:
        """
        Calculates risk based on ambiguity and missing terms.
        """
        risk = 0.0
        # Risk 1: Verbal Agreement without Price
        has_price = any(t["type"] == "financial" for t in terms)
        if not has_price:
            risk += 0.4

        # Risk 2: Timeline Ambiguity
        has_date = any(t["type"] == "timeline" for t in terms)
        if not has_date:
            risk += 0.3

        # Risk 3: Location Specifics (CA/SOMA requires specific disclosures)
        if location == "US-CA" and risk > 0.5:
            risk += 0.1  # CA is litigious

        return min(risk, 1.0)

    def _generate_napkin(self, terms: list[dict[str, str]]) -> str:
        """
        Generates the simple "Butcher Block" summary.
        """
        if not terms:
            return "No binding terms detected."

        napkin = "THE UNDERSIGNED AGREE:\n"
        for t in terms:
            napkin += f"- [{t['type'].upper()}]: {t['content'].strip()}\n"
        return napkin
