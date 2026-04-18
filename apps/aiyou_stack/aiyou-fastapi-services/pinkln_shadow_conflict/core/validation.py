"""Validation Layer and Boy Scout Rule implementation.

This module provides:
1. Validation of outputs against "insanely great" standards
2. Boy Scout Rule metadata tracking
3. Quality assessment and critique
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BoyScoutMetadata:
    """Boy Scout Rule metadata: "Leave it cleaner than you found it"

    Tracks all improvements made during an interaction.
    """

    files_touched: list[str] = field(default_factory=list)
    cleanup_actions: list[str] = field(default_factory=list)
    cleaner_than_found: bool = True
    baseline_state: str = ""
    new_state: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filesTouched": self.files_touched,
            "cleanupActions": self.cleanup_actions,
            "cleanerThanFound": self.cleaner_than_found,
            "baselineState": self.baseline_state,
            "newState": self.new_state,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class BoyScoutRule:
    """Enforces the Boy Scout Rule across all interactions.

    Every deliverable must track:
    - What was touched
    - What was cleaned up
    - Baseline vs. new state
    """

    @staticmethod
    def create_metadata() -> BoyScoutMetadata:
        """Create new Boy Scout metadata."""
        return BoyScoutMetadata()

    @staticmethod
    def validate_cleanup(metadata: BoyScoutMetadata) -> bool:
        """Validate that cleanup actually happened.

        Args:
            metadata: Boy Scout metadata to validate

        Returns:
            True if valid cleanup occurred

        """
        # Must have touched files
        if not metadata.files_touched:
            return True  # No files touched, no cleanup needed

        # Must have cleanup actions if files were touched
        if metadata.files_touched and not metadata.cleanup_actions:
            return False

        # Must have evidence of improvement
        if metadata.baseline_state and not metadata.new_state:
            return False

        return metadata.cleaner_than_found

    @staticmethod
    def format_deliverable_metadata(metadata: BoyScoutMetadata) -> str:
        """Format metadata for inclusion in deliverables.

        Args:
            metadata: Metadata to format

        Returns:
            Formatted markdown string

        """
        return f"""
---
## Boy Scout Rule Metadata

**Files Touched:**
{chr(10).join(f"  - {f}" for f in metadata.files_touched) if metadata.files_touched else "  - None"}

**Cleanup Actions:**
{chr(10).join(f"  - {a}" for a in metadata.cleanup_actions) if metadata.cleanup_actions else "  - None"}

**Cleaner Than Found:** {metadata.cleaner_than_found}

**Baseline State:** {metadata.baseline_state or "N/A"}

**New State:** {metadata.new_state or "N/A"}
---
"""


class ValidationLayer:
    """Validation layer that ensures outputs meet "insanely great" standards.

    This implements the validation system that runs after every complex generation.
    """

    # Excellence criteria
    EXCELLENCE_CRITERIA = {
        "clarity": 0.8,  # Is it clear and understandable?
        "simplicity": 0.8,  # Is it as simple as possible?
        "elegance": 0.7,  # Does it feel elegant and natural?
        "completeness": 0.9,  # Does it fully solve the problem?
        "robustness": 0.8,  # Does it handle edge cases?
    }

    VALIDATION_PROMPT = """
Pause. Critique the response you just generated.

1. Assumptions: What assumptions did you make?
2. Weaknesses: What could be wrong with this answer?
3. Simplification: Is this the simplest possible solution? What can be removed?

Refine the answer based on this critique. Leave this interaction better than you found it.
"""

    def __init__(self):
        """Initialize validation layer."""
        self.validation_history: list[dict[str, Any]] = []

    def verify(self, response: dict[str, Any]) -> bool:
        """Verify that response meets basic quality standards.

        Args:
            response: Response to verify

        Returns:
            True if meets standards

        """
        # Check for required fields
        if "output" not in response:
            return False

        # Check for metadata
        if "metadata" not in response:
            response["metadata"] = {}

        return True

    def is_insanely_great(self, response: dict[str, Any]) -> bool:
        """Check if response meets "insanely great" standards.

        Args:
            response: Response to check

        Returns:
            True if insanely great

        """
        if "quality_score" not in response.get("metadata", {}):
            return False

        quality_score = response["metadata"]["quality_score"]

        # Check against excellence criteria
        for criterion, threshold in self.EXCELLENCE_CRITERIA.items():
            if quality_score.get(criterion, 0) < threshold:
                return False

        return True

    def critique_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Generate critique of response.

        Args:
            response: Response to critique

        Returns:
            Critique dictionary

        """
        critique = {
            "assumptions": self._identify_assumptions(response),
            "weaknesses": self._identify_weaknesses(response),
            "simplification_opportunities": self._identify_simplifications(response),
            "missing_elements": self._identify_missing_elements(response),
        }

        self.validation_history.append({"response_id": id(response), "critique": critique})

        return critique

    def _identify_assumptions(self, response: dict[str, Any]) -> list[str]:
        """Identify assumptions made in response."""
        # Placeholder - would use LLM analysis in production
        return []

    def _identify_weaknesses(self, response: dict[str, Any]) -> list[str]:
        """Identify weaknesses in response."""
        weaknesses = []

        # Check for missing documentation
        if "documentation" not in response.get("metadata", {}):
            weaknesses.append("Missing documentation")

        # Check for missing tests
        if "tests" not in response.get("metadata", {}):
            weaknesses.append("Missing test coverage information")

        return weaknesses

    def _identify_simplifications(self, response: dict[str, Any]) -> list[str]:
        """Identify opportunities to simplify."""
        # Placeholder - would use complexity analysis in production
        return []

    def _identify_missing_elements(self, response: dict[str, Any]) -> list[str]:
        """Identify missing elements."""
        missing = []

        required_fields = ["output", "metadata"]
        for field in required_fields:
            if field not in response:
                missing.append(f"Missing required field: {field}")

        return missing

    def apply_boy_scout_rule(self, response: dict[str, Any], context: Any) -> dict[str, Any]:
        """Apply Boy Scout Rule to response.

        Args:
            response: Response to enhance
            context: Execution context

        Returns:
            Enhanced response with Boy Scout metadata

        """
        # Create Boy Scout metadata
        boy_scout = BoyScoutMetadata()

        # Extract touched files from context
        if hasattr(context, "touched_files"):
            boy_scout.files_touched = context.touched_files

        # Extract cleanup actions from context
        if hasattr(context, "cleanup_actions"):
            boy_scout.cleanup_actions = context.cleanup_actions

        # Add to response
        response["boy_scout"] = boy_scout.to_dict()
        response["metadata"]["boy_scout_compliant"] = BoyScoutRule.validate_cleanup(boy_scout)

        return response

    def get_validation_history(self) -> list[dict[str, Any]]:
        """Get validation history."""
        return self.validation_history

    def clear_history(self):
        """Clear validation history."""
        self.validation_history = []


class QualityMetrics:
    """Quality metrics for measuring output excellence."""

    @staticmethod
    def calculate_quality_score(response: dict[str, Any]) -> dict[str, float]:
        """Calculate quality score across multiple dimensions.

        Args:
            response: Response to score

        Returns:
            Quality scores dictionary

        """
        return {
            "clarity": 0.0,  # Placeholder - would use actual analysis
            "simplicity": 0.0,
            "elegance": 0.0,
            "completeness": 0.0,
            "robustness": 0.0,
            "overall": 0.0,
        }

    @staticmethod
    def assess_complexity(code: str) -> float:
        """Assess code complexity.

        Args:
            code: Code to assess

        Returns:
            Complexity score (0-1, lower is better)

        """
        # Simple heuristic - would use cyclomatic complexity in production
        lines = code.split("\n")
        return min(len(lines) / 100, 1.0)
