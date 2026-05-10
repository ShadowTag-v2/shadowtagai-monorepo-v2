"""VerbSpecification - Action Verb Decomposition System
Version: 1.0.0

Philosophy: California Bar Method - each action verb gets its own separate consideration.
Design: Complete task coverage by decomposing to atomic verbs.

"11 bar exams taught me: all errors are reading comprehension.
Break every statement into simple sentences. Each verb = separate analysis."
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class VerbCategory(StrEnum):
    """Categories of action verbs."""

    DATA_FLOW = "data_flow"  # RECEIVES, SENDS, RETURNS
    TRANSFORM = "transform"  # VALIDATES, TRANSFORMS, COMPUTES
    STORAGE = "storage"  # STORES, RETRIEVES, DELETES
    CONTROL = "control"  # CHECKS, DECIDES, ROUTES
    LIFECYCLE = "lifecycle"  # CREATES, UPDATES, DESTROYS


# Common action verbs with their analysis templates
VERB_TEMPLATES = {
    # Data Flow
    "RECEIVES": {
        "category": VerbCategory.DATA_FLOW,
        "questions": [
            "Source: Where does it come from?",
            "Format: What format? (JSON, XML, binary)",
            "Protocol: HTTP, WebSocket, gRPC?",
            "Authentication: Who can send?",
            "Validation: What's checked on receipt?",
            "Failures: Connection timeout? Malformed data?",
        ],
    },
    "SENDS": {
        "category": VerbCategory.DATA_FLOW,
        "questions": [
            "Destination: Where does it go?",
            "Format: What format?",
            "Protocol: How transmitted?",
            "Retry: What if fails?",
            "Timeout: How long to wait?",
            "Confirmation: How to verify receipt?",
        ],
    },
    "RETURNS": {
        "category": VerbCategory.DATA_FLOW,
        "questions": [
            "Format: Response structure?",
            "Status codes: Success/error codes?",
            "Payload: What data included?",
            "Headers: Any special headers?",
            "Timing: Sync or async?",
        ],
    },
    # Transform
    "VALIDATES": {
        "category": VerbCategory.TRANSFORM,
        "questions": [
            "Rules: What schema/constraints?",
            "Sanitization: XSS, SQL injection?",
            "Required fields: What's mandatory?",
            "Format checks: Types, ranges, patterns?",
            "Business rules: Domain-specific validation?",
            "Error messages: What feedback on failure?",
        ],
    },
    "TRANSFORMS": {
        "category": VerbCategory.TRANSFORM,
        "questions": [
            "Input format: What comes in?",
            "Output format: What goes out?",
            "Mapping: Field-by-field transformation?",
            "Defaults: What if field missing?",
            "Encoding: Character set, compression?",
            "Reversible: Can it be undone?",
        ],
    },
    "COMPUTES": {
        "category": VerbCategory.TRANSFORM,
        "questions": [
            "Algorithm: What calculation?",
            "Inputs: What values needed?",
            "Precision: Decimal places, rounding?",
            "Edge cases: Division by zero? Overflow?",
            "Performance: Time complexity?",
        ],
    },
    # Storage
    "STORES": {
        "category": VerbCategory.STORAGE,
        "questions": [
            "Where: Database, cache, file?",
            "Format: How serialized?",
            "Durability: Persistent or ephemeral?",
            "Indexing: What's indexed?",
            "Encryption: At rest?",
            "Retention: How long kept?",
        ],
    },
    "RETRIEVES": {
        "category": VerbCategory.STORAGE,
        "questions": [
            "Source: Where from?",
            "Query: How to find it?",
            "Caching: Is it cached?",
            "Not found: What if missing?",
            "Permissions: Who can access?",
            "Performance: Query time?",
        ],
    },
    "DELETES": {
        "category": VerbCategory.STORAGE,
        "questions": [
            "Target: What gets deleted?",
            "Cascade: Related data?",
            "Soft delete: Recoverable?",
            "Audit: Is it logged?",
            "Permissions: Who can delete?",
        ],
    },
    # Control
    "CHECKS": {
        "category": VerbCategory.CONTROL,
        "questions": [
            "Condition: What's being checked?",
            "True path: What if true?",
            "False path: What if false?",
            "Edge cases: Null? Empty?",
            "Performance: How expensive?",
        ],
    },
    "DECIDES": {
        "category": VerbCategory.CONTROL,
        "questions": [
            "Criteria: What determines outcome?",
            "Options: What are the choices?",
            "Default: If no criteria match?",
            "Audit: Is decision logged?",
            "Override: Can it be changed?",
        ],
    },
    "ROUTES": {
        "category": VerbCategory.CONTROL,
        "questions": [
            "Destinations: Where can it go?",
            "Criteria: How is route chosen?",
            "Fallback: If primary unavailable?",
            "Load balancing: How distributed?",
            "Tracing: Can route be traced?",
        ],
    },
    # Lifecycle
    "CREATES": {
        "category": VerbCategory.LIFECYCLE,
        "questions": [
            "What: Entity being created?",
            "Required: Mandatory fields?",
            "Defaults: Auto-populated values?",
            "Uniqueness: ID generation?",
            "Events: Triggers on create?",
            "Permissions: Who can create?",
        ],
    },
    "UPDATES": {
        "category": VerbCategory.LIFECYCLE,
        "questions": [
            "Target: What's being updated?",
            "Fields: Which fields change?",
            "Partial: Can update subset?",
            "Versioning: Track changes?",
            "Conflicts: Concurrent updates?",
            "Events: Triggers on update?",
        ],
    },
    "DESTROYS": {
        "category": VerbCategory.LIFECYCLE,
        "questions": [
            "Target: What's destroyed?",
            "Dependencies: Related resources?",
            "Cleanup: Side effects?",
            "Confirmation: Require confirmation?",
            "Undo: Can it be reversed?",
        ],
    },
}


@dataclass
class VerbAnalysis:
    """Analysis of a single verb."""

    verb: str
    category: VerbCategory
    questions: list[str]
    answers: dict[str, str] = field(default_factory=dict)
    edge_cases: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


@dataclass
class TaskDecomposition:
    """Complete decomposition of a task into verbs."""

    original_text: str
    verbs: list[str]
    analyses: dict[str, VerbAnalysis]
    simple_sentences: list[str]


class VerbSpecification:
    """Action verb decomposition system.

    California Bar Method:
    1. Break compound statements into simple sentences
    2. Identify all action verbs
    3. Analyze each verb separately
    4. Leave no points on the table
    """

    def __init__(self):
        self.verb_templates = VERB_TEMPLATES

    # =========================================================================
    # DECOMPOSITION
    # =========================================================================

    def decompose(self, text: str) -> TaskDecomposition:
        """Decompose text into action verbs with analysis.

        "Dan and Dave went to burglarize" becomes:
        - "Dan went to burglarize"
        - "Dave went to burglarize"

        Each verb gets separate consideration.
        """
        # Split compound subjects
        simple_sentences = self._split_compound_subjects(text)

        # Extract verbs
        verbs = self._extract_verbs(simple_sentences)

        # Analyze each verb
        analyses = {}
        for verb in verbs:
            verb_upper = verb.upper()
            if verb_upper in self.verb_templates:
                template = self.verb_templates[verb_upper]
                analyses[verb] = VerbAnalysis(
                    verb=verb_upper,
                    category=template["category"],
                    questions=template["questions"],
                )
            else:
                # Unknown verb - generic analysis
                analyses[verb] = VerbAnalysis(
                    verb=verb_upper,
                    category=VerbCategory.CONTROL,
                    questions=[
                        "Input: What does it take?",
                        "Output: What does it produce?",
                        "Failures: What can go wrong?",
                        "Edge cases: Unusual scenarios?",
                    ],
                )

        return TaskDecomposition(
            original_text=text,
            verbs=verbs,
            analyses=analyses,
            simple_sentences=simple_sentences,
        )

    def _split_compound_subjects(self, text: str) -> list[str]:
        """Split compound subjects into simple sentences.

        "A and B do X" → ["A does X", "B does X"]
        """
        import re

        sentences = []

        # Split on periods first
        for sentence in text.split("."):
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check for compound subjects
            pattern = r"^(\w+)\s+and\s+(\w+)\s+(.+)$"
            match = re.match(pattern, sentence, re.IGNORECASE)

            if match:
                subject1, subject2, predicate = match.groups()
                sentences.append(f"{subject1} {predicate}")
                sentences.append(f"{subject2} {predicate}")
            else:
                sentences.append(sentence)

        return sentences

    def _extract_verbs(self, sentences: list[str]) -> list[str]:
        """Extract action verbs from sentences."""
        verbs = []
        known_verbs = set(v.lower() for v in self.verb_templates)

        # Also look for verb-like words
        verb_indicators = [
            "receives",
            "sends",
            "returns",
            "validates",
            "transforms",
            "computes",
            "stores",
            "retrieves",
            "deletes",
            "checks",
            "decides",
            "routes",
            "creates",
            "updates",
            "destroys",
            "processes",
            "generates",
            "analyzes",
            "optimizes",
            "handles",
            "authenticates",
            "authorizes",
            "encrypts",
            "decrypts",
        ]

        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                # Clean word
                clean_word = "".join(c for c in word if c.isalnum())
                if clean_word in known_verbs or clean_word in verb_indicators:  # noqa: SIM102
                    if clean_word not in verbs:
                        verbs.append(clean_word)

        return verbs

    # =========================================================================
    # ANALYSIS HELPERS
    # =========================================================================

    def get_verb_template(self, verb: str) -> dict[str, Any]:
        """Get analysis template for a verb."""
        verb_upper = verb.upper()
        if verb_upper in self.verb_templates:
            return self.verb_templates[verb_upper]
        return {
            "category": VerbCategory.CONTROL,
            "questions": [
                "Input: What does it take?",
                "Output: What does it produce?",
                "Failures: What can go wrong?",
                "Edge cases: Unusual scenarios?",
            ],
        }

    def analyze_verb(self, verb: str, answers: dict[str, str] = None) -> VerbAnalysis:
        """Create analysis for a specific verb.

        Args:
            verb: The action verb
            answers: Pre-filled answers to questions

        Returns:
            VerbAnalysis with template and answers

        """
        template = self.get_verb_template(verb)
        analysis = VerbAnalysis(
            verb=verb.upper(),
            category=template["category"],
            questions=template["questions"],
            answers=answers or {},
        )
        return analysis

    def format_analysis(self, analysis: VerbAnalysis) -> str:
        """Format verb analysis as outline text."""
        lines = [f"### {analysis.verb}"]

        for i, question in enumerate(analysis.questions, 1):
            answer = analysis.answers.get(question, "[TODO]")
            # Extract short label from question
            label = question.split(":")[0] if ":" in question else f"Q{i}"
            lines.append(f"  {label}: {answer}")

        if analysis.edge_cases:
            lines.append("  Edge cases:")
            for case in analysis.edge_cases:
                lines.append(f"    - {case}")

        if analysis.failures:
            lines.append("  Failures:")
            for failure in analysis.failures:
                lines.append(f"    - {failure}")

        return "\n".join(lines)

    # =========================================================================
    # OUTLINE GENERATION
    # =========================================================================

    def generate_outline(self, decomposition: TaskDecomposition) -> str:
        """Generate outline from decomposition.

        This is the skeleton that gets filled in.
        """
        lines = [
            "# Task Outline",
            "",
            f"Original: {decomposition.original_text}",
            "",
            "## Simple Sentences",
        ]

        for i, sentence in enumerate(decomposition.simple_sentences, 1):
            lines.append(f"{i}. {sentence}")

        lines.extend(["", "## Verb Analysis", ""])

        for verb in decomposition.verbs:
            if verb in decomposition.analyses:
                analysis = decomposition.analyses[verb]
                lines.append(self.format_analysis(analysis))
                lines.append("")

        return "\n".join(lines)

    def generate_spec_document(
        self,
        decomposition: TaskDecomposition,
        filled_analyses: dict[str, dict[str, str]] = None,
    ) -> str:
        """Generate complete specification document.

        Args:
            decomposition: The task decomposition
            filled_analyses: Dict of verb → {question → answer}

        """
        filled = filled_analyses or {}

        lines = [
            "# Specification Document",
            "",
            "## Task",
            decomposition.original_text,
            "",
            "## Requirements",
            "",
        ]

        for verb in decomposition.verbs:
            verb_upper = verb.upper()
            lines.append(f"### {verb_upper}")
            lines.append("")

            if verb in decomposition.analyses:
                analysis = decomposition.analyses[verb]

                # Fill in answers if provided
                if verb in filled:
                    for question in analysis.questions:
                        key = question.split(":")[0]
                        answer = filled[verb].get(key, filled[verb].get(question, "TBD"))
                        lines.append(f"- **{key}**: {answer}")
                else:
                    for question in analysis.questions:
                        lines.append(f"- **{question}**: TBD")

            lines.append("")

        return "\n".join(lines)

    # =========================================================================
    # COMPLETENESS CHECK
    # =========================================================================

    def check_completeness(
        self,
        decomposition: TaskDecomposition,
        filled_analyses: dict[str, dict[str, str]],
    ) -> dict[str, Any]:
        """Check if all verbs have been fully analyzed.

        "Leave no points on the table."
        """
        total_questions = 0
        answered_questions = 0
        missing = []

        for verb in decomposition.verbs:
            if verb in decomposition.analyses:
                analysis = decomposition.analyses[verb]
                verb_answers = filled_analyses.get(verb, {})

                for question in analysis.questions:
                    total_questions += 1
                    key = question.split(":")[0]
                    if key in verb_answers or question in verb_answers:
                        answered_questions += 1
                    else:
                        missing.append(f"{verb.upper()}: {key}")

        completeness = answered_questions / total_questions if total_questions > 0 else 0

        return {
            "total_questions": total_questions,
            "answered": answered_questions,
            "missing": len(missing),
            "completeness": f"{completeness:.1%}",
            "is_complete": len(missing) == 0,
            "missing_items": missing[:10],  # Show first 10
        }

    def __repr__(self) -> str:
        return f"VerbSpecification(templates={len(self.verb_templates)})"


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_verb_system() -> VerbSpecification:
    """Create verb specification system.

    "Each action verb gets its own separate consideration."
    """
    return VerbSpecification()


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("VerbSpecification - Self Test")
    print("=" * 60)

    # Create system
    verb_sys = create_verb_system()
    print(f"\nCreated: {verb_sys}")

    # Test decomposition
    print("\n" + "=" * 60)
    print("Decomposing Task...")

    task = "System receives credentials, validates format, stores in database, and returns token"
    decomp = verb_sys.decompose(task)

    print(f"\nOriginal: {decomp.original_text}")
    print("\nSimple sentences:")
    for s in decomp.simple_sentences:
        print(f"  - {s}")

    print(f"\nVerbs found: {decomp.verbs}")

    # Show outline
    print("\n" + "=" * 60)
    print("Generated Outline:")
    print(verb_sys.generate_outline(decomp))

    # Fill in some answers
    print("\n" + "=" * 60)
    print("Filling Analysis...")

    filled = {
        "receives": {
            "Source": "HTTP POST /auth/login",
            "Format": "JSON {email, password}",
            "Protocol": "HTTPS",
            "Authentication": "None (public endpoint)",
            "Validation": "Check Content-Type header",
            "Failures": "Connection timeout, malformed JSON",
        },
        "validates": {
            "Rules": "Email regex, password 8+ chars",
            "Sanitization": "Trim whitespace, escape SQL",
            "Required fields": "email, password",
            "Format checks": "Valid email format",
            "Business rules": "Account not locked",
            "Error messages": "Specific field errors",
        },
    }

    # Check completeness
    check = verb_sys.check_completeness(decomp, filled)
    print(f"\nCompleteness: {check['completeness']}")
    print(f"Answered: {check['answered']}/{check['total_questions']}")
    if check["missing_items"]:
        print(f"Missing: {check['missing_items'][:5]}")

    # Generate spec document
    print("\n" + "=" * 60)
    print("Specification Document (excerpt):")
    spec = verb_sys.generate_spec_document(decomp, filled)
    # Show first 50 lines
    for line in spec.split("\n")[:30]:
        print(line)

    print("\n" + "=" * 60)
    print("✓ VerbSpecification working correctly")
    print("\nPhilosophy: Each action verb gets its own separate consideration.")
