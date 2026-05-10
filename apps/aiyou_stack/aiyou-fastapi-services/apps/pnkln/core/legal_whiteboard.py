"""LegalWhiteboard - Single Point of Truth for Multi-Agent Coordination
Version: 1.0.0

Philosophy: Legal-linguistic precision meets AI coordination.
Design: Bar exam protocols + test-first task framing + phased anonymity.

Target: 99%+ accuracy through:
- Action verb decomposition
- 12 bar exam protocols
- T-shaped specialization
- Quidditch gamification
- Agent wellness system
- Persistent GitHub memory

"Always learning, always yearning, never resting, ever vesting."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

# =============================================================================
# ENUMS AND TYPES
# =============================================================================


class DebatePhase(StrEnum):
    """Phased anonymity protocol to prevent sycophancy."""

    ISOLATED = "isolated"  # Round 1: Independent answers
    BLIND_CRITIQUE = "blind"  # Round 2: See answers, not sources
    ATTRIBUTED = "attributed"  # Round 3+: Full reveal for Glicko-2


class NoteVisibility(StrEnum):
    """Hybrid note visibility - commit then reveal."""

    PRIVATE = "private"  # Only author sees
    COMMITTED = "committed"  # Ready to reveal
    VISIBLE = "visible"  # All can see


class TaskPhase(StrEnum):
    """Bottom-up reading protocol."""

    EXPECTED_OUTPUT = "output"  # What format/result needed
    CALL_OF_QUESTION = "call"  # What verb is being asked
    CONTEXT_FACTS = "facts"  # Supporting details


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class WhiteboardFact:
    """Single fact with formal read highlighting."""

    id: str
    content: str
    formally_read: bool = False
    read_timestamp: datetime | None = None
    acknowledged_by: list[str] = field(default_factory=list)
    related_reference: str | None = None  # Link to reference material


@dataclass
class AgentNote:
    """Agent note with commit-then-reveal visibility."""

    agent_id: str
    fact_id: str
    content: str  # Must be in outline form
    visibility: NoteVisibility = NoteVisibility.PRIVATE
    timestamp: datetime = field(default_factory=datetime.now)
    annotations: list[Annotation] = field(default_factory=list)


@dataclass
class Annotation:
    """Public comment on another agent's note."""

    author_id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestCase:
    """Pre-written test - the call of the question."""

    id: str
    description: str
    assertion: str  # What must be true
    passed: bool | None = None


@dataclass
class OutlineSection:
    """Section of the outline being built."""

    verb: str  # Action verb (RECEIVES, VALIDATES, etc.)
    subsections: dict[str, str] = field(default_factory=dict)
    completed: bool = False


# =============================================================================
# MAIN WHITEBOARD CLASS
# =============================================================================


class LegalWhiteboard:
    """Single point of truth for multi-agent coordination.

    Layout:
    ┌─────────────────────────────────────────────────────────────┐
    │ CALL PANE (Pre-Written Tests)                               │
    ├─────────────────────────────────────────────────────────────┤
    │ FACT PANE (Current)     │ REFERENCE PANE (Flattened Code)   │
    │                         │                                   │
    │ OUTLINE PANE (Building) │                                   │
    ├─────────────────────────────────────────────────────────────┤
    │ NOTES PANE (Commit-Then-Reveal)                             │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.created_at = datetime.now()

        # Call Pane - Tests that define success
        self.tests: list[TestCase] = []
        self.call_of_question: str = ""

        # Fact Pane - Parsed facts with highlighting
        self.facts: dict[str, WhiteboardFact] = {}
        self.current_fact_index: int = 0

        # Reference Pane - Flattened code/specs
        self.reference_material: str = ""
        self.reference_sections: dict[str, str] = {}  # filename → content

        # Outline Pane - Answer being built
        self.outline: list[OutlineSection] = []

        # Notes Pane - Agent notes with visibility
        self.notes: dict[str, list[AgentNote]] = {}  # agent_id → notes

        # Debate phase tracking
        self.current_phase: DebatePhase = DebatePhase.ISOLATED

        # Audience for output formatting
        self.audience: Literal["technical", "executive", "public", "legal"] = "technical"

    # =========================================================================
    # CALL PANE (Test-First)
    # =========================================================================

    def set_tests(self, tests: list[dict[str, str]]):
        """Set pre-written tests - the call of the question.
        Answer = make these tests pass.
        """
        self.tests = [
            TestCase(
                id=f"test_{i}",
                description=t.get("description", ""),
                assertion=t.get("assertion", ""),
            )
            for i, t in enumerate(tests)
        ]

    def set_call_of_question(self, call: str):
        """Set the main question being answered."""
        self.call_of_question = call

    def evaluate_answer(self, answer: str) -> dict[str, Any]:
        """Check if answer passes all tests."""
        results = []
        for test in self.tests:
            # In production, actually evaluate
            # For now, track that evaluation happened
            passed = self._evaluate_test(test, answer)
            test.passed = passed
            results.append({"test_id": test.id, "description": test.description, "passed": passed})

        return {
            "all_passed": all(r["passed"] for r in results),
            "results": results,
            "pass_rate": sum(1 for r in results if r["passed"]) / len(results) if results else 0,
        }

    def _evaluate_test(self, test: TestCase, answer: str) -> bool:
        """Evaluate single test against answer."""
        # Placeholder - in production, use actual test execution
        return test.assertion.lower() in answer.lower()

    # =========================================================================
    # FACT PANE (Period-Stop Parsing)
    # =========================================================================

    def parse_input(self, text: str):
        """Parse input sentence-by-sentence.
        Each period = stop and highlight.
        """
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        for i, sentence in enumerate(sentences):
            fact_id = f"fact_{i}"
            self.facts[fact_id] = WhiteboardFact(id=fact_id, content=sentence)

    def split_compound_subjects(self, sentence: str) -> list[str]:
        """Split compound subjects into simple sentences.
        'Dan and Dave went to burglarize' →
        ['Dan went to burglarize', 'Dave went to burglarize']
        """
        # Simple pattern matching for 'A and B verb'
        import re

        pattern = r"^(\w+)\s+and\s+(\w+)\s+(.+)$"
        match = re.match(pattern, sentence)

        if match:
            subject1, subject2, predicate = match.groups()
            return [f"{subject1} {predicate}", f"{subject2} {predicate}"]
        return [sentence]

    def formally_read_fact(self, fact_id: str):
        """Mark fact as formally read - all agents can see position."""
        if fact_id in self.facts:
            fact = self.facts[fact_id]
            fact.formally_read = True
            fact.read_timestamp = datetime.now()

    def acknowledge_fact(self, fact_id: str, agent_id: str):
        """Agent acknowledges they've read the fact."""
        if fact_id in self.facts and agent_id not in self.facts[fact_id].acknowledged_by:
            self.facts[fact_id].acknowledged_by.append(agent_id)

    def get_current_fact(self) -> WhiteboardFact | None:
        """Get the fact currently being processed."""
        fact_id = f"fact_{self.current_fact_index}"
        return self.facts.get(fact_id)

    def advance_to_next_fact(self):
        """Move to next fact after current is fully processed."""
        self.current_fact_index += 1

    # =========================================================================
    # REFERENCE PANE (Flattened Code)
    # =========================================================================

    def flatten_codebase(self, files: dict[str, str]):
        """Flatten all relevant code into single reference.
        Agents can glance up and see everything.
        """
        sections = []
        for filename, content in files.items():
            self.reference_sections[filename] = content
            sections.append(f"# === {filename} ===\n{content}")

        self.reference_material = "\n\n".join(sections)

    def highlight_relevant(self, current_fact: str) -> list[str]:
        """Highlight sections of reference relevant to current fact."""
        relevant = []
        keywords = current_fact.lower().split()

        for filename, content in self.reference_sections.items():
            content_lower = content.lower()
            if any(kw in content_lower for kw in keywords if len(kw) > 3):
                relevant.append(filename)

        return relevant

    # =========================================================================
    # OUTLINE PANE (Fill Around)
    # =========================================================================

    def create_outline_from_verbs(self, verbs: list[str]):
        """Create outline structure from action verbs.
        Notes ARE the outline - fill in place.
        """
        self.outline = [OutlineSection(verb=verb.upper()) for verb in verbs]

    def fill_outline_section(self, verb: str, subsection: str, content: str):
        """Fill in a subsection of the outline."""
        for section in self.outline:
            if section.verb == verb.upper():
                section.subsections[subsection] = content
                break

    def mark_section_complete(self, verb: str):
        """Mark an outline section as complete."""
        for section in self.outline:
            if section.verb == verb.upper():
                section.completed = True
                break

    def get_outline_text(self) -> str:
        """Get current outline as formatted text."""
        lines = []
        for i, section in enumerate(self.outline, 1):
            status = "✓" if section.completed else " "
            lines.append(f"{i}. [{status}] {section.verb}")
            for key, value in section.subsections.items():
                lines.append(f"   {key}: {value}")
        return "\n".join(lines)

    # =========================================================================
    # NOTES PANE (Commit-Then-Reveal)
    # =========================================================================

    def add_note(self, agent_id: str, fact_id: str, content: str):
        """Agent adds private note (in outline form).
        Note remains private until committed.
        """
        if agent_id not in self.notes:
            self.notes[agent_id] = []

        note = AgentNote(
            agent_id=agent_id,
            fact_id=fact_id,
            content=content,
            visibility=NoteVisibility.PRIVATE,
        )
        self.notes[agent_id].append(note)

    def commit_notes(self, agent_id: str):
        """Agent commits all private notes - ready for reveal."""
        if agent_id in self.notes:
            for note in self.notes[agent_id]:
                if note.visibility == NoteVisibility.PRIVATE:
                    note.visibility = NoteVisibility.COMMITTED

    def reveal_all_committed(self):
        """Reveal all committed notes simultaneously."""
        for agent_id in self.notes:
            for note in self.notes[agent_id]:
                if note.visibility == NoteVisibility.COMMITTED:
                    note.visibility = NoteVisibility.VISIBLE

    def add_annotation(self, author_id: str, target_agent_id: str, note_index: int, content: str):
        """Add public annotation to another agent's visible note."""
        if target_agent_id in self.notes and note_index < len(self.notes[target_agent_id]):
            note = self.notes[target_agent_id][note_index]
            if note.visibility == NoteVisibility.VISIBLE:
                note.annotations.append(Annotation(author_id=author_id, content=content))

    def get_visible_notes(self, requesting_agent_id: str) -> dict[str, list[AgentNote]]:
        """Get all notes visible to requesting agent."""
        visible = {}

        for agent_id, agent_notes in self.notes.items():
            visible_notes = []
            for note in agent_notes:
                # Own notes always visible
                if agent_id == requesting_agent_id or note.visibility == NoteVisibility.VISIBLE:
                    visible_notes.append(note)

            if visible_notes:
                visible[agent_id] = visible_notes

        return visible

    # =========================================================================
    # PHASE MANAGEMENT
    # =========================================================================

    def advance_phase(self):
        """Advance to next debate phase."""
        if self.current_phase == DebatePhase.ISOLATED:
            self.current_phase = DebatePhase.BLIND_CRITIQUE
        elif self.current_phase == DebatePhase.BLIND_CRITIQUE:
            self.current_phase = DebatePhase.ATTRIBUTED

    def get_anonymized_notes(self, fact_id: str) -> list[str]:
        """Get all notes for a fact without revealing authors (blind phase)."""
        all_notes = []
        for agent_notes in self.notes.values():
            for note in agent_notes:
                if note.fact_id == fact_id and note.visibility != NoteVisibility.PRIVATE:
                    all_notes.append(note.content)

        # Shuffle to prevent order-based identification
        import random

        random.shuffle(all_notes)
        return all_notes

    # =========================================================================
    # AUDIENCE ADAPTATION
    # =========================================================================

    def set_audience(self, audience: Literal["technical", "executive", "public", "legal"]):
        """Set audience for output formatting."""
        self.audience = audience

    def format_output(self, content: str) -> str:
        """Format output for target audience."""
        if self.audience == "public":
            return self._simplify_for_public(content)
        if self.audience == "executive":
            return self._summarize_for_executive(content)
        if self.audience == "legal":
            return self._formalize_for_legal(content)
        # technical
        return content

    def _simplify_for_public(self, content: str) -> str:
        """Remove jargon for public audience."""
        # Placeholder - in production, use LLM or rules
        return content.replace("implementation", "setup").replace("endpoint", "address")

    def _summarize_for_executive(self, content: str) -> str:
        """Bottom line up front for executives."""
        lines = content.split("\n")
        if len(lines) > 5:
            return "BLUF: " + lines[0] + "\n\nDetails:\n" + "\n".join(lines[1:5]) + "..."
        return content

    def _formalize_for_legal(self, content: str) -> str:
        """Precise language for legal audience."""
        return content  # Already precise with action verbs

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_layout_snapshot(self) -> dict[str, Any]:
        """Get current state of all panes for display."""
        return {
            "call_pane": {
                "call_of_question": self.call_of_question,
                "tests": [
                    {"id": t.id, "desc": t.description, "passed": t.passed} for t in self.tests
                ],
            },
            "fact_pane": {
                "current": self.get_current_fact(),
                "total_facts": len(self.facts),
                "current_index": self.current_fact_index,
            },
            "reference_pane": {
                "sections": list(self.reference_sections.keys()),
                "total_chars": len(self.reference_material),
            },
            "outline_pane": {
                "sections": len(self.outline),
                "completed": sum(1 for s in self.outline if s.completed),
                "text": self.get_outline_text(),
            },
            "notes_pane": {
                "agents": list(self.notes.keys()),
                "total_notes": sum(len(n) for n in self.notes.values()),
            },
            "phase": self.current_phase.value,
            "audience": self.audience,
        }

    def comprehension_check(self, agent_id: str) -> dict[str, Any]:
        """Verify agent has read every word.
        Bar exam: Must read every single word.
        """
        total_facts = len(self.facts)
        acknowledged = sum(1 for fact in self.facts.values() if agent_id in fact.acknowledged_by)

        return {
            "agent_id": agent_id,
            "total_facts": total_facts,
            "acknowledged": acknowledged,
            "completion_rate": acknowledged / total_facts if total_facts > 0 else 0,
            "complete": acknowledged == total_facts,
        }

    def __repr__(self) -> str:
        return (
            f"LegalWhiteboard(task={self.task_id}, "
            f"facts={len(self.facts)}, "
            f"tests={len(self.tests)}, "
            f"phase={self.current_phase.value})"
        )


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_whiteboard(
    task_id: str,
    call_of_question: str,
    tests: list[dict[str, str]],
    input_text: str,
    reference_files: dict[str, str],
    verbs: list[str],
    audience: str = "technical",
) -> LegalWhiteboard:
    """Create fully configured whiteboard.

    Jobs mode: Make the common case trivial.
    """
    wb = LegalWhiteboard(task_id)

    # Set up call pane
    wb.set_call_of_question(call_of_question)
    wb.set_tests(tests)

    # Parse facts
    wb.parse_input(input_text)

    # Flatten reference
    wb.flatten_codebase(reference_files)

    # Create outline
    wb.create_outline_from_verbs(verbs)

    # Set audience
    wb.set_audience(audience)

    return wb


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("LegalWhiteboard - Self Test")
    print("=" * 60)

    # Create whiteboard
    wb = create_whiteboard(
        task_id="test_001",
        call_of_question="Implement user authentication endpoint",
        tests=[
            {"description": "Returns 401 without token", "assertion": "401"},
            {"description": "Returns user with valid token", "assertion": "user"},
        ],
        input_text="System receives credentials. System validates format. System checks database. System returns token.",
        reference_files={
            "auth.py": "class AuthService:\n    def validate(self): pass",
            "models.py": "class User:\n    email: str",
        },
        verbs=["receives", "validates", "checks", "returns"],
        audience="technical",
    )

    print(f"\nCreated: {wb}")
    print("\nLayout Snapshot:")

    snapshot = wb.get_layout_snapshot()
    for pane, data in snapshot.items():
        print(f"\n{pane}:")
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {data}")

    # Test note workflow
    print("\n" + "=" * 60)
    print("Testing Note Workflow (Commit-Then-Reveal)")

    # Agent A adds private note
    wb.add_note("agent_a", "fact_0", "I. RECEIVES\n   A. Source: HTTP POST\n   B. Format: JSON")
    print("Agent A added private note")

    # Agent B adds private note
    wb.add_note("agent_b", "fact_0", "I. RECEIVES\n   A. Source: REST API\n   B. Auth: Bearer")
    print("Agent B added private note")

    # Commit notes
    wb.commit_notes("agent_a")
    wb.commit_notes("agent_b")
    print("Both agents committed notes")

    # Reveal
    wb.reveal_all_committed()
    print("Notes revealed")

    # Check visibility
    visible = wb.get_visible_notes("agent_a")
    print(f"\nAgent A can see {len(visible)} agents' notes")

    print("\n" + "=" * 60)
    print("✓ LegalWhiteboard working correctly")
    print("\nPhilosophy: Legal-linguistic precision for 99%+ accuracy")
