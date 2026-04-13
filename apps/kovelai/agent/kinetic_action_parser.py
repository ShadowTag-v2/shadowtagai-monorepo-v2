"""
Kinetic Action Parser (KAP) — Forensic Action Verb Auditor

The Kinetic Action Parser is the mandatory first-pass hook (Prompt 0) in the
KovelAI Oracle Studio pipeline. It performs a "syntactic autopsy" on legal text,
extracting and classifying every material action verb to expose:

  1. Active agency: WHO is doing WHAT — the power map of the document
  2. Passive evasion: Where actors hide behind passive constructions
  3. Hedging language: Weasel verbs that dilute legal certainty
  4. Temporal anchoring: When actions occurred, will occur, or are conditional
  5. Obligation spectrum: MUST vs SHALL vs SHOULD vs MAY gradations

This is NOT semantic summarization. This is syntactic dissection.

Architecture:
    Legal Text → KAP → Verb Ledger → Oracle Studio Steps 2-7

Per the Doctrinal Framework:
    "Move from semantic summarization to syntactic autopsy."
    "What did the CONTRACT actually SAY it would DO?"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VerbClassification(str, Enum):
    """Classification taxonomy for legal action verbs."""

    # Power verbs — direct, unambiguous action
    PERFORMATIVE = "performative"  # "hereby grants", "shall deliver"
    OPERATIVE = "operative"  # "agrees", "warrants", "represents"
    COERCIVE = "coercive"  # "must", "shall", "requires"
    DISPOSITIVE = "dispositive"  # "terminates", "revokes", "voids"

    # Evasion verbs — agency-obscuring constructions
    PASSIVE = "passive"  # "was determined", "has been assessed"
    HEDGING = "hedging"  # "may", "could", "might", "appears to"
    CONDITIONAL = "conditional"  # "if...then", "provided that", "subject to"
    NOMINALIZED = "nominalized"  # "made a determination" vs "determined"

    # Temporal verbs — time-anchoring
    PAST_DEFINITE = "past_definite"  # "executed", "filed", "served"
    PRESENT_OPERATIVE = "present_operative"  # "agrees", "consents", "authorizes"
    FUTURE_OBLIGATORY = "future_obligatory"  # "shall deliver", "will pay"
    FUTURE_CONTINGENT = "future_contingent"  # "may elect to", "could seek"


class ObligationGrade(str, Enum):
    """Obligation spectrum per legal drafting standards."""

    MANDATORY = "MANDATORY"  # shall, must, is required to
    DIRECTORY = "DIRECTORY"  # should, is expected to
    PERMISSIVE = "PERMISSIVE"  # may, is permitted to, can
    PROHIBITIVE = "PROHIBITIVE"  # shall not, must not, is prohibited from
    ASPIRATIONAL = "ASPIRATIONAL"  # endeavors to, will use best efforts


@dataclass
class ExtractedVerb:
    """A single extracted verb with full forensic metadata."""

    verb: str
    original_text: str  # surrounding sentence/clause
    position: int  # character offset in source
    actor: Optional[str] = None  # WHO is performing
    target: Optional[str] = None  # WHAT is being acted upon
    classification: VerbClassification = VerbClassification.OPERATIVE
    obligation_grade: ObligationGrade = ObligationGrade.DIRECTORY
    is_negated: bool = False
    is_passive: bool = False
    tense: str = "present"
    confidence: float = 0.9
    forensic_note: str = ""


@dataclass
class VerbLedger:
    """
    The Verb Ledger — complete forensic output of the Kinetic Action Parser.
    This is the input artifact for Oracle Studio Step 2.
    """

    source_text_hash: str = ""
    total_verbs_extracted: int = 0
    verbs: list[ExtractedVerb] = field(default_factory=list)

    # Aggregate forensic metrics
    active_ratio: float = 0.0  # % of verbs in active voice
    passive_ratio: float = 0.0  # % of verbs in passive voice
    hedging_ratio: float = 0.0  # % of hedging/weasel verbs
    obligation_distribution: dict[str, int] = field(default_factory=dict)
    power_map: dict[str, list[str]] = field(default_factory=dict)  # actor → [verbs]

    # Red flags
    red_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize for AG-UI streaming."""
        return {
            "source_text_hash": self.source_text_hash,
            "total_verbs_extracted": self.total_verbs_extracted,
            "active_voice_ratio": f"{self.active_ratio:.1%}",
            "passive_voice_ratio": f"{self.passive_ratio:.1%}",
            "hedging_ratio": f"{self.hedging_ratio:.1%}",
            "obligation_distribution": self.obligation_distribution,
            "power_map": self.power_map,
            "red_flags": self.red_flags,
            "verbs": [
                {
                    "verb": v.verb,
                    "actor": v.actor,
                    "target": v.target,
                    "classification": v.classification.value,
                    "obligation": v.obligation_grade.value,
                    "is_passive": v.is_passive,
                    "is_negated": v.is_negated,
                    "tense": v.tense,
                    "forensic_note": v.forensic_note,
                    "context": v.original_text[:120],
                }
                for v in self.verbs
            ],
        }


# ──────────────────────────────────────────────
# Verb Detection Patterns
# ──────────────────────────────────────────────

# Mandatory-class modal verbs (highest obligation)
MANDATORY_MODALS = re.compile(
    r"\b(shall|must|is\s+required\s+to|are\s+required\s+to|"
    r"is\s+obligated\s+to|are\s+obligated\s+to)\b",
    re.IGNORECASE,
)

# Prohibitive modals
PROHIBITIVE_MODALS = re.compile(
    r"\b(shall\s+not|must\s+not|may\s+not|is\s+prohibited\s+from|"
    r"are\s+prohibited\s+from|cannot|is\s+forbidden\s+to)\b",
    re.IGNORECASE,
)

# Permissive modals
PERMISSIVE_MODALS = re.compile(
    r"\b(may|can|is\s+permitted\s+to|are\s+permitted\s+to|"
    r"is\s+authorized\s+to|has\s+the\s+right\s+to|is\s+entitled\s+to)\b",
    re.IGNORECASE,
)

# Hedging / weasel patterns
HEDGING_PATTERNS = re.compile(
    r"\b(might|could|may\s+possibly|appears\s+to|seems\s+to|"
    r"is\s+believed\s+to|arguably|potentially|"
    r"would\s+suggest|tends\s+to|is\s+thought\s+to|"
    r"endeavors?\s+to|shall\s+use\s+(?:best|reasonable)\s+efforts)\b",
    re.IGNORECASE,
)

# Passive voice detection
PASSIVE_PATTERN = re.compile(
    r"\b(was|were|been|being|is|are|am|get|gets|got|gotten)\s+"
    r"(\w+ed|dealt|paid|made|given|taken|done|said|found|known|shown)\b",
    re.IGNORECASE,
)

# Nominalization detector (hidden verbs as nouns)
NOMINALIZATION_PATTERN = re.compile(
    r"\b(made\s+a\s+determination|reached\s+a\s+conclusion|"
    r"gave\s+consideration\s+to|took\s+action|"
    r"came\s+to\s+an\s+agreement|entered\s+into\s+a\s+(?:contract|agreement)|"
    r"provided\s+(?:an?\s+)?(?:notification|authorization|acknowledgment)|"
    r"submitted\s+(?:an?\s+)?(?:request|application|petition))\b",
    re.IGNORECASE,
)

# Performative verbs (contractual speech acts)
PERFORMATIVE_VERBS = re.compile(
    r"\b(hereby\s+\w+s?|do\s+hereby|does\s+hereby|"
    r"warrants?\s+(?:and\s+)?represents?|"
    r"acknowledges?\s+and\s+agrees?|"
    r"covenants?\s+and\s+agrees?|"
    r"grants?\s+and\s+conveys?)\b",
    re.IGNORECASE,
)

# Dispositive verbs (termination, revocation)
DISPOSITIVE_VERBS = re.compile(
    r"\b(terminates?|revokes?|nullif(?:y|ies)|voids?|"
    r"cancels?|rescinds?|extinguish(?:es)?|"
    r"dissolves?|annuls?|abrogates?|"
    r"forfeits?|waives?|relinquish(?:es)?)\b",
    re.IGNORECASE,
)

# Core operative verbs in legal documents
OPERATIVE_VERBS = re.compile(
    r"\b(agrees?|consents?|authorizes?|approves?|"
    r"accepts?|confirms?|certif(?:y|ies)|"
    r"acknowledges?|represents?|warrants?|"
    r"indemnif(?:y|ies)|guarantees?|"
    r"assigns?|delegates?|transfers?|"
    r"pays?|delivers?|performs?|provides?|"
    r"compli(?:es|y)|satisf(?:y|ies)|fulfills?|"
    r"discloses?|notif(?:y|ies)|submits?|"
    r"executes?|signs?|files?|serves?)\b",
    re.IGNORECASE,
)


# ──────────────────────────────────────────────
# Kinetic Action Parser Engine
# ──────────────────────────────────────────────


class KineticActionParser:
    """
    The Kinetic Action Parser — forensic verb extraction engine.

    Usage:
        parser = KineticActionParser()
        ledger = parser.parse(legal_text)
        print(ledger.to_dict())
    """

    def parse(self, text: str) -> VerbLedger:
        """
        Execute full forensic analysis on input text.
        Returns a VerbLedger with all extracted verbs and aggregate metrics.
        """
        import hashlib

        ledger = VerbLedger(
            source_text_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
        )

        # Split into sentences for context extraction
        sentences = self._split_sentences(text)

        for i, sentence in enumerate(sentences):
            offset = text.find(sentence)

            # Layer 1: Performative verbs (highest priority)
            for match in PERFORMATIVE_VERBS.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.PERFORMATIVE,
                        obligation_grade=ObligationGrade.MANDATORY,
                        confidence=0.95,
                        forensic_note="Contractual speech act — creates legal obligation on utterance",
                    )
                )

            # Layer 2: Prohibitive modals (check before permissive to avoid overlap)
            for match in PROHIBITIVE_MODALS.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.COERCIVE,
                        obligation_grade=ObligationGrade.PROHIBITIVE,
                        is_negated=True,
                        confidence=0.95,
                        forensic_note="Prohibition — creates negative obligation",
                    )
                )

            # Layer 3: Mandatory modals
            for match in MANDATORY_MODALS.finditer(sentence):
                # Avoid double-counting "shall not" already caught above
                full_context = sentence[max(0, match.start()):match.end() + 10]
                if "not" in full_context.lower():
                    continue
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.COERCIVE,
                        obligation_grade=ObligationGrade.MANDATORY,
                        confidence=0.92,
                        forensic_note="Affirmative mandate — creates positive obligation",
                    )
                )

            # Layer 4: Hedging language
            for match in HEDGING_PATTERNS.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.HEDGING,
                        obligation_grade=ObligationGrade.ASPIRATIONAL,
                        confidence=0.85,
                        forensic_note="⚠️ HEDGING: dilutes certainty — flag for attorney review",
                    )
                )

            # Layer 5: Passive voice
            for match in PASSIVE_PATTERN.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.PASSIVE,
                        is_passive=True,
                        confidence=0.80,
                        forensic_note="⚠️ PASSIVE: actor obscured — WHO did this?",
                    )
                )

            # Layer 6: Nominalizations (hidden verbs)
            for match in NOMINALIZATION_PATTERN.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.NOMINALIZED,
                        confidence=0.78,
                        forensic_note="⚠️ NOMINALIZED: action buried in noun phrase — decompose",
                    )
                )

            # Layer 7: Dispositive verbs
            for match in DISPOSITIVE_VERBS.finditer(sentence):
                ledger.verbs.append(
                    ExtractedVerb(
                        verb=match.group().strip(),
                        original_text=sentence.strip(),
                        position=offset + match.start(),
                        classification=VerbClassification.DISPOSITIVE,
                        obligation_grade=ObligationGrade.MANDATORY,
                        confidence=0.90,
                        forensic_note="DISPOSITIVE: this verb changes legal state — critical",
                    )
                )

            # Layer 8: Operative verbs (catch-all for standard legal verbs)
            for match in OPERATIVE_VERBS.finditer(sentence):
                # Avoid duplicates from higher-priority layers
                verb_text = match.group().strip()
                existing_positions = {v.position for v in ledger.verbs}
                if (offset + match.start()) not in existing_positions:
                    ledger.verbs.append(
                        ExtractedVerb(
                            verb=verb_text,
                            original_text=sentence.strip(),
                            position=offset + match.start(),
                            classification=VerbClassification.OPERATIVE,
                            confidence=0.85,
                        )
                    )

            # Layer 9: Permissive modals
            for match in PERMISSIVE_MODALS.finditer(sentence):
                existing_positions = {v.position for v in ledger.verbs}
                if (offset + match.start()) not in existing_positions:
                    ledger.verbs.append(
                        ExtractedVerb(
                            verb=match.group().strip(),
                            original_text=sentence.strip(),
                            position=offset + match.start(),
                            classification=VerbClassification.CONDITIONAL,
                            obligation_grade=ObligationGrade.PERMISSIVE,
                            confidence=0.85,
                            forensic_note="Permissive — grants discretion, not obligation",
                        )
                    )

        # Sort by position for reading order
        ledger.verbs.sort(key=lambda v: v.position)
        ledger.total_verbs_extracted = len(ledger.verbs)

        # Compute aggregate metrics
        self._compute_metrics(ledger)

        return ledger

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences, respecting legal citation conventions."""
        # Don't split on common abbreviations in legal text
        text = re.sub(r"(\b(?:U\.S|v|No|Rev|Stat|Sec|Art|Amdt|Supp|App)\.) ", r"\1⟨DOT⟩ ", text)
        sentences = re.split(r"(?<=[.!?;])\s+", text)
        return [s.replace("⟨DOT⟩", ".") for s in sentences if s.strip()]

    def _compute_metrics(self, ledger: VerbLedger) -> None:
        """Compute aggregate forensic metrics."""
        if not ledger.verbs:
            return

        total = len(ledger.verbs)
        passive_count = sum(1 for v in ledger.verbs if v.is_passive)
        hedging_count = sum(1 for v in ledger.verbs if v.classification == VerbClassification.HEDGING)
        active_count = total - passive_count

        ledger.active_ratio = active_count / total
        ledger.passive_ratio = passive_count / total
        ledger.hedging_ratio = hedging_count / total

        # Obligation distribution
        for v in ledger.verbs:
            grade = v.obligation_grade.value
            ledger.obligation_distribution[grade] = ledger.obligation_distribution.get(grade, 0) + 1

        # Power map: actor → verbs
        for v in ledger.verbs:
            actor = v.actor or "UNSPECIFIED"
            if actor not in ledger.power_map:
                ledger.power_map[actor] = []
            ledger.power_map[actor].append(v.verb)

        # Red flags
        if ledger.passive_ratio > 0.4:
            ledger.red_flags.append(
                f"⚠️ HIGH PASSIVE RATIO ({ledger.passive_ratio:.0%}): "
                "Document systematically hides actors behind passive constructions"
            )
        if ledger.hedging_ratio > 0.25:
            ledger.red_flags.append(
                f"⚠️ EXCESSIVE HEDGING ({ledger.hedging_ratio:.0%}): "
                "Document dilutes certainty — likely contains escape hatches"
            )
        if not any(v.obligation_grade == ObligationGrade.MANDATORY for v in ledger.verbs):
            ledger.red_flags.append(
                "⚠️ NO MANDATORY OBLIGATIONS: Document creates no binding duties"
            )

        dispositive_count = sum(
            1 for v in ledger.verbs if v.classification == VerbClassification.DISPOSITIVE
        )
        if dispositive_count > 0:
            ledger.red_flags.append(
                f"🔴 DISPOSITIVE ACTIONS ({dispositive_count}): "
                "Document contains state-changing verbs — review immediately"
            )
