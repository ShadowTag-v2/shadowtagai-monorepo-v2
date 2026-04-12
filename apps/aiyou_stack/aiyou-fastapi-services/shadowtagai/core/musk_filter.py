"""
Musk First Principles Filter - Pre-JR Engine Triage.

Runs BEFORE Purpose/Reasons/Brakes to ensure we're not
optimizing things that shouldn't exist.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RequirementQuestion:
    """A scored question about a requirement."""

    question: str
    answer: str = ""
    score: int = 0  # 1-5 scale


@dataclass
class DeletionCandidate:
    """A component/feature/step proposed for deletion."""

    name: str
    proposed: bool = True
    deleted: bool = False
    restored: bool = False
    reason: str = ""


@dataclass
class MuskFilterResult:
    """Result of running the Musk First Principles Filter."""

    passed: bool
    step1_passed: bool
    step2_passed: bool
    step3_ready: bool
    requirements_score: float
    restore_rate: float
    deletions: list[DeletionCandidate]
    audit_trail: dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MuskFilter:
    """
    Pre-JR Engine triage filter based on Elon Musk's first principles algorithm.

    1. Question requirements (make less dumb)
    2. Delete the thing (10% restore rule)
    3. Only then optimize
    """

    def __init__(self):
        self.requirement_questions = [
            RequirementQuestion("Who gave this requirement?"),
            RequirementQuestion("What's their bias/incentive?"),
            RequirementQuestion("What problem does this ACTUALLY solve?"),
            RequirementQuestion("Is this inherited assumption or validated?"),
            RequirementQuestion("Can we find first-hand evidence it's needed?"),
        ]
        self.deletion_candidates: list[DeletionCandidate] = []
        self.optimizations_blocked: list[str] = []

    def score_requirements(self, answers: dict) -> float:
        """
        Score requirements questioning (Step 1).

        Args:
            answers: Dict mapping question text to (answer, score) tuples

        Returns:
            Average score (must be >= 3.0 to pass)
        """
        total = 0
        count = 0

        for q in self.requirement_questions:
            if q.question in answers:
                answer, score = answers[q.question]
                q.answer = answer
                q.score = min(max(score, 1), 5)  # Clamp to 1-5
                total += q.score
                count += 1

        return total / count if count > 0 else 0.0

    def attempt_deletion(self, candidates: list[dict]) -> float:
        """
        Attempt deletion on components (Step 2).

        Args:
            candidates: List of dicts with keys: name, deleted, restored, reason

        Returns:
            Restore rate (should be >= 10% to pass)
        """
        self.deletion_candidates = []

        for c in candidates:
            candidate = DeletionCandidate(
                name=c.get("name", "Unknown"),
                proposed=True,
                deleted=c.get("deleted", False),
                restored=c.get("restored", False),
                reason=c.get("reason", ""),
            )
            self.deletion_candidates.append(candidate)

        # Calculate restore rate
        deleted_count = sum(1 for c in self.deletion_candidates if c.deleted)
        restored_count = sum(1 for c in self.deletion_candidates if c.restored)

        if deleted_count == 0:
            return 0.0

        return (restored_count / deleted_count) * 100

    def block_optimization(self, item: str, reason: str = "") -> None:
        """
        Block an optimization that hasn't passed Steps 1+2.

        Args:
            item: The thing being optimized
            reason: Why optimization was blocked
        """
        self.optimizations_blocked.append(f"{item}: {reason}")

    def run_filter(
        self,
        requirement_answers: dict,
        deletion_candidates: list[dict],
        min_requirement_score: float = 3.0,
        min_restore_rate: float = 10.0,
        max_restore_rate: float = 50.0,
    ) -> MuskFilterResult:
        """
        Run the complete Musk First Principles Filter.

        Args:
            requirement_answers: Dict mapping questions to (answer, score) tuples
            deletion_candidates: List of deletion candidate dicts
            min_requirement_score: Minimum average score to pass Step 1
            min_restore_rate: Minimum restore % to pass Step 2
            max_restore_rate: Maximum restore % to pass Step 2

        Returns:
            MuskFilterResult with pass/fail and audit data
        """
        # Step 1: Question requirements
        req_score = self.score_requirements(requirement_answers)
        step1_passed = req_score >= min_requirement_score

        # Step 2: Attempt deletion
        restore_rate = self.attempt_deletion(deletion_candidates)

        # Must attempt deletion on at least 3 items
        attempted = len([c for c in self.deletion_candidates if c.deleted])
        step2_passed = (
            attempted >= 3 and restore_rate >= min_restore_rate and restore_rate <= max_restore_rate
        )

        # Step 3: Only ready if 1+2 passed
        step3_ready = step1_passed and step2_passed

        # Overall pass
        passed = step1_passed and step2_passed

        # Build audit trail
        audit_trail = {
            "deleted": [c.name for c in self.deletion_candidates if c.deleted and not c.restored],
            "restored": [c.name for c in self.deletion_candidates if c.restored],
            "optimizations_blocked": self.optimizations_blocked,
            "warnings": [],
        }

        if restore_rate < min_restore_rate:
            audit_trail["warnings"].append(
                f"Restore rate {restore_rate:.1f}% < {min_restore_rate}% - too timid, delete more"
            )
        if restore_rate > max_restore_rate:
            audit_trail["warnings"].append(
                f"Restore rate {restore_rate:.1f}% > {max_restore_rate}% - too aggressive"
            )
        if not step1_passed:
            audit_trail["warnings"].append(
                f"Requirements score {req_score:.1f} < {min_requirement_score} - requirements too dumb"
            )

        return MuskFilterResult(
            passed=passed,
            step1_passed=step1_passed,
            step2_passed=step2_passed,
            step3_ready=step3_ready,
            requirements_score=req_score,
            restore_rate=restore_rate,
            deletions=self.deletion_candidates,
            audit_trail=audit_trail,
        )


# Convenience function
def run_musk_filter(requirement_answers: dict, deletion_candidates: list[dict]) -> MuskFilterResult:
    """
    One-liner to run Musk First Principles Filter.

    Returns MuskFilterResult with pass/fail status.
    """
    musk_filter = MuskFilter()
    return musk_filter.run_filter(requirement_answers, deletion_candidates)


if __name__ == "__main__":
    # Example usage
    filter = MuskFilter()

    # Step 1: Question requirements
    answers = {
        "Who gave this requirement?": ("Product team", 4),
        "What's their bias/incentive?": ("Ship fast, may skip validation", 3),
        "What problem does this ACTUALLY solve?": ("Customer audit needs", 5),
        "Is this inherited assumption or validated?": ("Validated with 3 customers", 5),
        "Can we find first-hand evidence it's needed?": ("Yes, compliance requirement", 5),
    }

    # Step 2: Deletion candidates
    candidates = [
        {
            "name": "AutoGen middleware",
            "deleted": True,
            "restored": False,
            "reason": "Unnecessary complexity",
        },
        {
            "name": "LangGraph orchestration",
            "deleted": True,
            "restored": False,
            "reason": "Native Gemini sufficient",
        },
        {
            "name": "Custom caching layer",
            "deleted": True,
            "restored": True,
            "reason": "Needed for p99 SLA",
        },
        {"name": "Debug logging", "deleted": True, "restored": False, "reason": "Production noise"},
        {
            "name": "Metrics endpoint",
            "deleted": True,
            "restored": True,
            "reason": "Required for monitoring",
        },
    ]

    # Run filter
    result = filter.run_filter(answers, candidates)

    print(f"Filter passed: {result.passed}")
    print(f"Requirements score: {result.requirements_score:.1f}")
    print(f"Restore rate: {result.restore_rate:.1f}%")
    print(f"Audit trail: {result.audit_trail}")
