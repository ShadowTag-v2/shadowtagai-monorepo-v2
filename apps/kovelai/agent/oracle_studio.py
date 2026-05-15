"""Oracle Studio — 7-Step Murder Board Pipeline

The Oracle Studio is the lawyer-side intelligence engine of KovelAI.
While the client side provides "Privileged Perplexity" (search + AI chat),
the lawyer side provides a forensic document analysis workbench that
transforms raw legal text into actionable legal intelligence.

The 7 Steps:
    0. Kinetic Action Parser  (Verb Auditor — Prompt 0, pre-hook)
    1. Argument Extraction    (Claim decomposition + thesis mapping)
    2. Verb Auditing          (KAP integration — obligation spectrum analysis)
    3. Assumption Auditing    (Hidden premise excavation)
    4. Relevance Filtering    (Logical nexus scoring)
    5. Steelman / Challenger  (Adversarial dialectic — strongest form + attack)
    6. Action Extraction      (Next-move synthesis — "So What?")
    7. Permanent Note Builder (Zettelkasten vault — atomic legal notes)

Each step is designed to be:
    - Streamable via AG-UI SSE events
    - Independently cacheable
    - Asynchronously executable via Inngest (for long documents)
    - Auditable (each step produces a signed artifact)

Monetization:
    - Each Murder Board invocation = 1 "Oracle Session"
    - Tier consumption: Starter (10/mo), Pro (50/mo), Sovereign (unlimited)
    - Pass-through compute: $49/session billed to client as e-discovery cost
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from agent.kinetic_action_parser import KineticActionParser, VerbLedger


class MurderBoardStep(StrEnum):
  """The 7 canonical steps of the Oracle Studio Murder Board."""

  ARGUMENT_EXTRACTION = "argument_extraction"
  VERB_AUDITING = "verb_auditing"
  ASSUMPTION_AUDITING = "assumption_auditing"
  RELEVANCE_FILTERING = "relevance_filtering"
  STEELMAN_CHALLENGER = "steelman_challenger"
  ACTION_EXTRACTION = "action_extraction"
  PERMANENT_NOTE_BUILDER = "permanent_note_builder"


@dataclass
class Argument:
  """A decomposed legal argument with forensic metadata."""

  id: str
  claim: str  # The core assertion
  support: list[str] = field(default_factory=list)  # Supporting evidence/reasoning
  classification: str = ""  # factual, legal, procedural, policy
  strength: float = 0.0  # 0.0 (baseless) to 1.0 (ironclad)
  vulnerabilities: list[str] = field(default_factory=list)


@dataclass
class Assumption:
  """A hidden premise extracted from legal text."""

  id: str
  assumption: str
  source_argument_id: str
  is_stated: bool = False  # explicitly stated vs implied
  is_valid: bool = True
  challenge: str = ""  # how to attack this assumption
  risk_level: str = "medium"  # low, medium, high, critical


@dataclass
class RelevanceScore:
  """Logical nexus scoring for an argument."""

  argument_id: str
  relevance_to_issue: float = 0.0  # 0.0 to 1.0
  relevance_to_relief: float = 0.0  # does it help win?
  evidentiary_weight: float = 0.0  # strength of supporting evidence
  composite_score: float = 0.0
  recommendation: str = ""  # "keep", "deprioritize", "challenge", "abandon"


@dataclass
class SteelmanResult:
  """Adversarial dialectic output — strongest form + attack vectors."""

  argument_id: str
  steelman: str  # strongest possible version of the argument
  challenger_attacks: list[str] = field(default_factory=list)
  counter_arguments: list[str] = field(default_factory=list)
  net_assessment: str = ""  # survives, weakened, defeated


@dataclass
class ActionItem:
  """Extracted next-move from the analysis."""

  id: str
  action: str
  priority: str = "medium"  # critical, high, medium, low
  deadline: str = ""
  assigned_to: str = "attorney"
  rationale: str = ""
  dependencies: list[str] = field(default_factory=list)


@dataclass
class PermanentNote:
  """Zettelkasten-style atomic legal note for the vault."""

  id: str
  title: str
  content: str
  source_document_hash: str = ""
  tags: list[str] = field(default_factory=list)
  links: list[str] = field(default_factory=list)  # IDs of related notes
  created_at: str = ""
  note_type: str = "legal_analysis"  # legal_analysis, case_law, strategy, procedural


@dataclass
class MurderBoardResult:
  """Complete output of a 7-step Murder Board session."""

  session_id: str
  document_hash: str
  timestamp: str
  steps_completed: list[str] = field(default_factory=list)

  # Step outputs
  verb_ledger: dict | None = None
  arguments: list[dict] = field(default_factory=list)
  assumptions: list[dict] = field(default_factory=list)
  relevance_scores: list[dict] = field(default_factory=list)
  steelman_results: list[dict] = field(default_factory=list)
  action_items: list[dict] = field(default_factory=list)
  permanent_notes: list[dict] = field(default_factory=list)

  # Aggregate intelligence
  executive_summary: str = ""
  risk_assessment: str = ""
  win_probability: float = 0.0

  def to_dict(self) -> dict:
    return {
      "session_id": self.session_id,
      "document_hash": self.document_hash,
      "timestamp": self.timestamp,
      "steps_completed": self.steps_completed,
      "verb_ledger": self.verb_ledger,
      "arguments": self.arguments,
      "assumptions": self.assumptions,
      "relevance_scores": self.relevance_scores,
      "steelman_results": self.steelman_results,
      "action_items": self.action_items,
      "permanent_notes": self.permanent_notes,
      "executive_summary": self.executive_summary,
      "risk_assessment": self.risk_assessment,
      "win_probability": self.win_probability,
    }


# ──────────────────────────────────────────────
# Oracle Studio Pipeline Orchestrator
# ──────────────────────────────────────────────


class OracleStudio:
  """The Oracle Studio Murder Board — 7-step legal intelligence pipeline.

  Usage:
      studio = OracleStudio()
      # Full pipeline
      result = studio.execute_murder_board(document_text)
      # Individual steps (for streaming)
      for step_event in studio.stream_murder_board(document_text):
          yield step_event  # AG-UI SSE events
  """

  def __init__(self):
    self.kap = KineticActionParser()

  def execute_murder_board(self, text: str, attorney_id: str = "") -> MurderBoardResult:
    """Execute the full 7-step Murder Board pipeline synchronously."""
    session_id = str(uuid.uuid4())
    doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

    result = MurderBoardResult(
      session_id=session_id,
      document_hash=doc_hash,
      timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # Step 0 (Pre-hook): Kinetic Action Parser
    verb_ledger = self.kap.parse(text)
    result.verb_ledger = verb_ledger.to_dict()

    # Step 1: Argument Extraction
    arguments = self._extract_arguments(text, verb_ledger)
    result.arguments = [self._argument_to_dict(a) for a in arguments]
    result.steps_completed.append(MurderBoardStep.ARGUMENT_EXTRACTION.value)

    # Step 2: Verb Auditing (KAP results integrated with arguments)
    self._audit_verbs_against_arguments(arguments, verb_ledger)
    result.steps_completed.append(MurderBoardStep.VERB_AUDITING.value)

    # Step 3: Assumption Auditing
    assumptions = self._audit_assumptions(arguments, text)
    result.assumptions = [self._assumption_to_dict(a) for a in assumptions]
    result.steps_completed.append(MurderBoardStep.ASSUMPTION_AUDITING.value)

    # Step 4: Relevance Filtering
    scores = self._filter_relevance(arguments, assumptions)
    result.relevance_scores = [self._relevance_to_dict(s) for s in scores]
    result.steps_completed.append(MurderBoardStep.RELEVANCE_FILTERING.value)

    # Step 5: Steelman / Challenger
    steelmans = self._steelman_challenge(arguments, scores)
    result.steelman_results = [self._steelman_to_dict(s) for s in steelmans]
    result.steps_completed.append(MurderBoardStep.STEELMAN_CHALLENGER.value)

    # Step 6: Action Extraction
    actions = self._extract_actions(arguments, steelmans, assumptions)
    result.action_items = [self._action_to_dict(a) for a in actions]
    result.steps_completed.append(MurderBoardStep.ACTION_EXTRACTION.value)

    # Step 7: Permanent Note Builder
    notes = self._build_permanent_notes(
      arguments, assumptions, steelmans, actions, doc_hash
    )
    result.permanent_notes = [self._note_to_dict(n) for n in notes]
    result.steps_completed.append(MurderBoardStep.PERMANENT_NOTE_BUILDER.value)

    # Executive summary
    result.executive_summary = self._generate_executive_summary(
      arguments,
      assumptions,
      scores,
      steelmans,
      actions,
      verb_ledger,
    )
    result.risk_assessment = self._assess_risk(assumptions, verb_ledger)
    result.win_probability = self._estimate_win_probability(scores, steelmans)

    return result

  # ──────────────────────────────────────
  # Step 1: Argument Extraction
  # ──────────────────────────────────────

  def _extract_arguments(self, text: str, verb_ledger: VerbLedger) -> list[Argument]:
    """Decompose legal text into discrete, atomic arguments.
    Uses verb positions as anchor points for claim boundaries.
    """
    arguments = []
    sentences = self._split_legal_text(text)

    # Cluster sentences around operative/performative verbs
    claim_buffer = []
    current_claim_id = 0

    for sentence in sentences:
      has_operative = any(
        v.original_text.strip() == sentence.strip()
        for v in verb_ledger.verbs
        if v.classification.value
        in ("performative", "operative", "coercive", "dispositive")
      )

      claim_buffer.append(sentence)

      if has_operative and len(claim_buffer) >= 1:
        current_claim_id += 1
        arg = Argument(
          id=f"ARG-{current_claim_id:03d}",
          claim=claim_buffer[-1].strip(),
          support=[s.strip() for s in claim_buffer[:-1] if s.strip()],
          classification=self._classify_argument(claim_buffer[-1]),
          strength=self._assess_argument_strength(claim_buffer, verb_ledger),
        )
        arguments.append(arg)
        claim_buffer = []

    # Catch remaining text as a final argument if substantive
    if claim_buffer and any(s.strip() for s in claim_buffer):
      current_claim_id += 1
      arguments.append(
        Argument(
          id=f"ARG-{current_claim_id:03d}",
          claim=" ".join(s.strip() for s in claim_buffer if s.strip()),
          classification="supplementary",
          strength=0.3,
        ),
      )

    return arguments

  def _classify_argument(self, text: str) -> str:
    """Classify an argument as factual, legal, procedural, or policy."""
    text_lower = text.lower()
    if any(
      w in text_lower
      for w in ["statute", "code", "section", "u.s.c.", "rule", "precedent"]
    ):
      return "legal"
    if any(
      w in text_lower for w in ["court", "motion", "filing", "hearing", "procedur"]
    ):
      return "procedural"
    if any(
      w in text_lower
      for w in ["policy", "interest", "purpose", "intent", "legislative"]
    ):
      return "policy"
    return "factual"

  def _assess_argument_strength(
    self, sentences: list[str], verb_ledger: VerbLedger
  ) -> float:
    """Score argument strength based on verb forensics."""
    combined = " ".join(sentences)
    relevant_verbs = [v for v in verb_ledger.verbs if v.original_text in combined]
    if not relevant_verbs:
      return 0.5

    # Mandatory + performative = strong
    strong = sum(1 for v in relevant_verbs if v.obligation_grade.value == "MANDATORY")
    # Hedging = weak
    weak = sum(1 for v in relevant_verbs if v.classification.value == "hedging")
    # Passive = slightly weak
    passive = sum(1 for v in relevant_verbs if v.is_passive)

    total = len(relevant_verbs)
    score = (strong * 1.5 - weak * 1.0 - passive * 0.3) / max(total, 1)
    return max(0.0, min(1.0, 0.5 + score * 0.3))

  # ──────────────────────────────────────
  # Step 2: Verb Auditing
  # ──────────────────────────────────────

  def _audit_verbs_against_arguments(
    self,
    arguments: list[Argument],
    verb_ledger: VerbLedger,
  ) -> None:
    """Cross-reference verb forensics against extracted arguments."""
    for arg in arguments:
      arg_text = arg.claim.lower()
      # Flag arguments with excessive hedging
      hedging_verbs = [
        v
        for v in verb_ledger.verbs
        if v.classification.value == "hedging" and v.verb.lower() in arg_text
      ]
      if hedging_verbs:
        arg.vulnerabilities.append(
          f"Contains {len(hedging_verbs)} hedging verb(s): {', '.join(v.verb for v in hedging_verbs)} — weakens assertion",
        )

      # Flag passive constructions that obscure actor
      passive_verbs = [
        v for v in verb_ledger.verbs if v.is_passive and v.verb.lower() in arg_text
      ]
      if passive_verbs:
        arg.vulnerabilities.append(
          f"Contains {len(passive_verbs)} passive construction(s) — actor obscured, opposing counsel can challenge attribution",
        )

  # ──────────────────────────────────────
  # Step 3: Assumption Auditing
  # ──────────────────────────────────────

  def _audit_assumptions(
    self, arguments: list[Argument], text: str
  ) -> list[Assumption]:
    """Excavate hidden premises from each argument."""
    assumptions = []
    counter = 0

    for arg in arguments:
      # Check for unstated jurisdictional assumptions
      if arg.classification == "legal" and "jurisdiction" not in arg.claim.lower():
        counter += 1
        assumptions.append(
          Assumption(
            id=f"ASM-{counter:03d}",
            assumption="Assumes current jurisdiction's law applies without conflict-of-law analysis",
            source_argument_id=arg.id,
            is_stated=False,
            risk_level="high",
            challenge="Challenge applicable law if multi-jurisdictional contacts exist",
          ),
        )

      # Check for temporal assumptions
      if any(w in arg.claim.lower() for w in ["current", "existing", "present"]):
        counter += 1
        assumptions.append(
          Assumption(
            id=f"ASM-{counter:03d}",
            assumption="Assumes current state of affairs will persist — no change-of-law provision",
            source_argument_id=arg.id,
            is_stated=False,
            risk_level="medium",
            challenge="Request sunset clause or amendment provision",
          ),
        )

      # Check for factual assertions without evidentiary support
      if arg.classification == "factual" and not arg.support:
        counter += 1
        assumptions.append(
          Assumption(
            id=f"ASM-{counter:03d}",
            assumption="Factual claim asserted without cited evidence — assumes truth without proof",
            source_argument_id=arg.id,
            is_stated=False,
            risk_level="critical",
            challenge="Demand documentary evidence or sworn declaration",
          ),
        )

      # Check for implied authority assumptions
      if any(w in arg.claim.lower() for w in ["authorized", "empowered", "entitled"]):
        counter += 1
        assumptions.append(
          Assumption(
            id=f"ASM-{counter:03d}",
            assumption="Assumes signatory has authority to bind the entity",
            source_argument_id=arg.id,
            is_stated=False,
            risk_level="high",
            challenge="Request certificate of authority or board resolution",
          ),
        )

    return assumptions

  # ──────────────────────────────────────
  # Step 4: Relevance Filtering
  # ──────────────────────────────────────

  def _filter_relevance(
    self,
    arguments: list[Argument],
    assumptions: list[Assumption],
  ) -> list[RelevanceScore]:
    """Score each argument's logical nexus to the central issue."""
    scores = []
    for arg in arguments:
      # Arguments with vulnerabilities are less relevant
      vulnerability_penalty = min(len(arg.vulnerabilities) * 0.1, 0.4)

      # Arguments with critical assumptions are riskier
      related_assumptions = [a for a in assumptions if a.source_argument_id == arg.id]
      critical_assumptions = [
        a for a in related_assumptions if a.risk_level == "critical"
      ]
      assumption_penalty = len(critical_assumptions) * 0.15

      relevance = arg.strength - vulnerability_penalty - assumption_penalty
      relevance = max(0.0, min(1.0, relevance))

      # Determine recommendation
      if relevance >= 0.7:
        rec = "keep — strong argument, advance in brief"
      elif relevance >= 0.5:
        rec = "keep with caveats — address vulnerabilities before using"
      elif relevance >= 0.3:
        rec = "deprioritize — weak argument, use only if needed for completeness"
      else:
        rec = "challenge or abandon — too many vulnerabilities to be useful"

      scores.append(
        RelevanceScore(
          argument_id=arg.id,
          relevance_to_issue=relevance,
          relevance_to_relief=arg.strength,
          evidentiary_weight=max(0, arg.strength - vulnerability_penalty),
          composite_score=relevance,
          recommendation=rec,
        ),
      )

    return scores

  # ──────────────────────────────────────
  # Step 5: Steelman / Challenger
  # ──────────────────────────────────────

  def _steelman_challenge(
    self,
    arguments: list[Argument],
    scores: list[RelevanceScore],
  ) -> list[SteelmanResult]:
    """Adversarial dialectic: for each argument, construct the
    strongest possible version AND the most devastating attack.
    """
    results = []
    score_map = {s.argument_id: s for s in scores}

    for arg in arguments:
      score = score_map.get(arg.id)
      composite = score.composite_score if score else 0.5

      # Steelman: strongest possible version
      steelman = (
        f"At its strongest, this {arg.classification} argument asserts: {arg.claim} "
      )
      if arg.support:
        steelman += f"Supported by: {'; '.join(arg.support[:3])}. "
      steelman += f"Strength assessment: {composite:.0%}. If properly supported with documentary evidence, this argument could withstand challenge."

      # Challenger: attack vectors
      attacks = []
      if arg.vulnerabilities:
        attacks.extend(arg.vulnerabilities)
      if composite < 0.5:
        attacks.append(
          "Low composite score suggests fundamental weakness — opposing counsel likely to move to strike or challenge standing",
        )
      if arg.classification == "factual" and not arg.support:
        attacks.append(
          "Factual assertion without evidentiary foundation — challenge with Rule 56(e) (summary judgment standard)",
        )

      # Counter-arguments
      counters = []
      if arg.classification == "legal":
        counters.append("Challenge with contrary authority or distinguish on facts")
      if arg.classification == "factual":
        counters.append("Demand production of underlying documents (FRCP 34)")
      counters.append("Depose declarant to test credibility and consistency")

      # Net assessment
      if composite >= 0.7 and len(attacks) <= 1:
        assessment = "SURVIVES — argument likely withstands adversarial scrutiny"
      elif composite >= 0.4:
        assessment = (
          "WEAKENED — argument has exploitable vulnerabilities but may survive"
        )
      else:
        assessment = "DEFEATED — argument unlikely to survive sustained challenge"

      results.append(
        SteelmanResult(
          argument_id=arg.id,
          steelman=steelman,
          challenger_attacks=attacks,
          counter_arguments=counters,
          net_assessment=assessment,
        ),
      )

    return results

  # ──────────────────────────────────────
  # Step 6: Action Extraction
  # ──────────────────────────────────────

  def _extract_actions(
    self,
    arguments: list[Argument],
    steelmans: list[SteelmanResult],
    assumptions: list[Assumption],
  ) -> list[ActionItem]:
    """The 'So What?' step — synthesize all analysis into
    concrete next-move actions for the attorney.
    """
    actions = []
    counter = 0
    {s.argument_id: s for s in steelmans}

    # Actions from defeated arguments
    for s in steelmans:
      if "DEFEATED" in s.net_assessment:
        counter += 1
        actions.append(
          ActionItem(
            id=f"ACT-{counter:03d}",
            action=f"Abandon or substantially rewrite argument {s.argument_id}",
            priority="high",
            rationale=f"Net assessment: {s.net_assessment}",
            assigned_to="attorney",
          ),
        )
      elif "WEAKENED" in s.net_assessment:
        counter += 1
        actions.append(
          ActionItem(
            id=f"ACT-{counter:03d}",
            action=f"Shore up {s.argument_id}: address {len(s.challenger_attacks)} attack vector(s)",
            priority="medium",
            rationale="Argument salvageable with additional evidence or briefing",
            assigned_to="attorney",
          ),
        )

    # Actions from critical assumptions
    for a in assumptions:
      if a.risk_level == "critical":
        counter += 1
        actions.append(
          ActionItem(
            id=f"ACT-{counter:03d}",
            action=f"Resolve {a.id}: {a.challenge}",
            priority="critical",
            rationale=f"Hidden premise: {a.assumption}",
            assigned_to="attorney",
          ),
        )

    # Global action: document preservation
    counter += 1
    actions.append(
      ActionItem(
        id=f"ACT-{counter:03d}",
        action="Issue litigation hold notice to preserve all related documents",
        priority="high",
        rationale="Standard practice — prevents spoliation claims",
        assigned_to="attorney",
      ),
    )

    # Global action: privilege review
    counter += 1
    actions.append(
      ActionItem(
        id=f"ACT-{counter:03d}",
        action="Review this Murder Board output for work-product privilege before sharing",
        priority="critical",
        rationale="This analysis constitutes attorney work product — protect from discovery",
        assigned_to="attorney",
      ),
    )

    return actions

  # ──────────────────────────────────────
  # Step 7: Permanent Note Builder
  # ──────────────────────────────────────

  def _build_permanent_notes(
    self,
    arguments: list[Argument],
    assumptions: list[Assumption],
    steelmans: list[SteelmanResult],
    actions: list[ActionItem],
    doc_hash: str,
  ) -> list[PermanentNote]:
    """Build Zettelkasten-style atomic notes for the lawyer's vault.
    Each note is self-contained, linked, and tagged for retrieval.
    """
    notes = []
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Note per argument
    for arg in arguments:
      steelman = next((s for s in steelmans if s.argument_id == arg.id), None)
      related_assumptions = [a for a in assumptions if a.source_argument_id == arg.id]

      content = f"**Claim**: {arg.claim}\n\n"
      content += f"**Classification**: {arg.classification}\n"
      content += f"**Strength**: {arg.strength:.0%}\n\n"

      if arg.vulnerabilities:
        content += "**Vulnerabilities**:\n"
        for v in arg.vulnerabilities:
          content += f"  - {v}\n"
        content += "\n"

      if steelman:
        content += f"**Net Assessment**: {steelman.net_assessment}\n\n"

      if related_assumptions:
        content += "**Hidden Assumptions**:\n"
        for a in related_assumptions:
          content += f"  - [{a.risk_level.upper()}] {a.assumption}\n"

      notes.append(
        PermanentNote(
          id=f"ZK-{arg.id}",
          title=f"Argument Analysis: {arg.claim[:80]}",
          content=content,
          source_document_hash=doc_hash,
          tags=[arg.classification, "murder-board", "argument-analysis"],
          links=[f"ZK-{a.id}" for a in related_assumptions],
          created_at=timestamp,
          note_type="legal_analysis",
        ),
      )

    # Summary note
    critical_actions = [a for a in actions if a.priority == "critical"]
    summary_content = (
      f"**Murder Board Summary** — {len(arguments)} arguments analyzed\n\n"
    )
    summary_content += f"**Critical Actions**: {len(critical_actions)}\n\n"
    for a in critical_actions:
      summary_content += f"  - [{a.id}] {a.action}\n"

    notes.append(
      PermanentNote(
        id="ZK-SUMMARY",
        title="Murder Board Executive Summary",
        content=summary_content,
        source_document_hash=doc_hash,
        tags=["summary", "murder-board", "executive"],
        links=[f"ZK-{arg.id}" for arg in arguments],
        created_at=timestamp,
        note_type="strategy",
      ),
    )

    return notes

  # ──────────────────────────────────────
  # Executive Summary & Risk Assessment
  # ──────────────────────────────────────

  def _generate_executive_summary(
    self,
    arguments: list[Argument],
    assumptions: list[Assumption],
    scores: list[RelevanceScore],
    steelmans: list[SteelmanResult],
    actions: list[ActionItem],
    verb_ledger: VerbLedger,
  ) -> str:
    """Generate the executive summary paragraph."""
    total_args = len(arguments)
    strong_args = sum(1 for s in scores if s.composite_score >= 0.7)
    sum(1 for s in scores if s.composite_score < 0.3)
    defeated = sum(1 for s in steelmans if "DEFEATED" in s.net_assessment)
    critical_assumptions = sum(1 for a in assumptions if a.risk_level == "critical")
    critical_actions = sum(1 for a in actions if a.priority == "critical")

    summary = (
      f"Murder Board analyzed {total_args} arguments. "
      f"{strong_args} survive adversarial scrutiny at ≥70% confidence. "
      f"{defeated} are assessed as DEFEATED and should be abandoned or rewritten. "
      f"{critical_assumptions} critical hidden assumptions require immediate resolution. "
      f"{critical_actions} critical action items generated. "
    )

    if verb_ledger.red_flags:
      summary += f"Verb Auditor raised {len(verb_ledger.red_flags)} red flag(s): "
      summary += "; ".join(verb_ledger.red_flags[:3])

    return summary

  def _assess_risk(self, assumptions: list[Assumption], verb_ledger: VerbLedger) -> str:
    """Assess overall document risk level."""
    critical = sum(1 for a in assumptions if a.risk_level == "critical")
    high = sum(1 for a in assumptions if a.risk_level == "high")
    red_flags = len(verb_ledger.red_flags)

    if critical >= 3 or (critical >= 1 and red_flags >= 2):
      return "🔴 CRITICAL — Document has fundamental structural deficiencies"
    if critical >= 1 or high >= 3:
      return "🟠 HIGH — Document has significant exposures requiring attorney attention"
    if high >= 1 or red_flags >= 1:
      return "🟡 ELEVATED — Document has identifiable weaknesses"
    return "🟢 LOW — Document appears structurally sound"

  def _estimate_win_probability(
    self,
    scores: list[RelevanceScore],
    steelmans: list[SteelmanResult],
  ) -> float:
    """Rough win probability estimate based on argument survival rates."""
    if not scores:
      return 0.5

    avg_relevance = sum(s.composite_score for s in scores) / len(scores)
    survival_rate = sum(1 for s in steelmans if "SURVIVES" in s.net_assessment) / max(
      len(steelmans),
      1,
    )

    return min(0.95, max(0.05, (avg_relevance * 0.6 + survival_rate * 0.4)))

  # ──────────────────────────────────────
  # Utility Methods
  # ──────────────────────────────────────

  def _split_legal_text(self, text: str) -> list[str]:
    """Split legal text into meaningful segments."""
    import re

    text = re.sub(
      r"(\b(?:U\.S|v|No|Rev|Stat|Sec|Art|Amdt|Supp|App)\.) ", r"\1⟨DOT⟩ ", text
    )
    sentences = re.split(r"(?<=[.!?;])\s+", text)
    return [s.replace("⟨DOT⟩", ".") for s in sentences if s.strip()]

  # Serialization helpers
  @staticmethod
  def _argument_to_dict(a: Argument) -> dict:
    return {
      "id": a.id,
      "claim": a.claim,
      "support": a.support,
      "classification": a.classification,
      "strength": f"{a.strength:.0%}",
      "vulnerabilities": a.vulnerabilities,
    }

  @staticmethod
  def _assumption_to_dict(a: Assumption) -> dict:
    return {
      "id": a.id,
      "assumption": a.assumption,
      "source_argument": a.source_argument_id,
      "is_stated": a.is_stated,
      "risk_level": a.risk_level,
      "challenge": a.challenge,
    }

  @staticmethod
  def _relevance_to_dict(r: RelevanceScore) -> dict:
    return {
      "argument_id": r.argument_id,
      "composite_score": f"{r.composite_score:.0%}",
      "recommendation": r.recommendation,
    }

  @staticmethod
  def _steelman_to_dict(s: SteelmanResult) -> dict:
    return {
      "argument_id": s.argument_id,
      "steelman": s.steelman,
      "attacks": s.challenger_attacks,
      "counter_arguments": s.counter_arguments,
      "net_assessment": s.net_assessment,
    }

  @staticmethod
  def _action_to_dict(a: ActionItem) -> dict:
    return {
      "id": a.id,
      "action": a.action,
      "priority": a.priority,
      "assigned_to": a.assigned_to,
      "rationale": a.rationale,
    }

  @staticmethod
  def _note_to_dict(n: PermanentNote) -> dict:
    return {
      "id": n.id,
      "title": n.title,
      "content": n.content,
      "tags": n.tags,
      "links": n.links,
      "created_at": n.created_at,
      "note_type": n.note_type,
    }
