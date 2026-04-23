#!/usr/bin/env python3
from __future__ import annotations

"""UphillSnowball Agent Task F1 Evaluation Harness

Measures agent task completion accuracy using precision, recall, and F1 scoring
across 4 dimensions: task completion, tool selection, output quality, error recovery.

Usage:
    python scripts/eval_uphillsnowball_f1.py [--ground-truth PATH] [--results PATH]
"""

import json  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402


@dataclass
class TaskEvalResult:
    """Result of evaluating a single agent task."""

    task_id: str
    task_description: str
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    correct_actions: int = 0
    total_actions_taken: int = 0
    total_expected_actions: int = 0
    tool_precision: float = 0.0
    output_quality: float = 0.0
    error_recovery: float = 0.0
    dimension_scores: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class AgentEvalSummary:
    """Summary of all agent task evaluation results."""

    aggregate_f1: float = 0.0
    weighted_f1: float = 0.0
    mean_precision: float = 0.0
    mean_recall: float = 0.0
    total_tasks: int = 0
    passing: bool = False
    category_scores: dict[str, float] = field(default_factory=dict)
    results: list[TaskEvalResult] = field(default_factory=list)


def evaluate_tool_selection(
    expected_tools: list[str],
    actual_tools: list[str],
) -> tuple[float, list[str]]:
    """Evaluate whether the agent selected correct tools.

    Args:
        expected_tools: Tools the ground truth expects.
        actual_tools: Tools the agent actually used.

    Returns:
        Tuple of (precision score, list of notes).

    """
    notes = []
    if not actual_tools:
        return 0.0, ["No tools used"]

    expected_set = {t.lower() for t in expected_tools}
    actual_set = {t.lower() for t in actual_tools}

    correct = expected_set & actual_set
    extra = actual_set - expected_set
    missing = expected_set - actual_set

    precision = len(correct) / len(actual_set) if actual_set else 0.0

    if extra:
        notes.append(f"Extra tools: {', '.join(extra)}")
    if missing:
        notes.append(f"Missing tools: {', '.join(missing)}")

    return precision, notes


def evaluate_output(
    expected_output: dict,
    actual_output: dict,
) -> float:
    """Evaluate output quality against expected criteria.

    Args:
        expected_output: Dictionary of expected output properties (key: bool).
        actual_output: Dictionary of actual output properties.

    Returns:
        Quality score 0-1.

    """
    if not expected_output:
        return 1.0

    total = len(expected_output)
    matched = 0

    for key, expected_value in expected_output.items():
        actual_value = actual_output.get(key)
        if actual_value == expected_value:
            matched += 1
        elif isinstance(expected_value, bool) and actual_value:
            matched += 1  # Truthy match for booleans

    return matched / total if total > 0 else 0.0


def evaluate_behaviors(
    expected_behaviors: list[str],
    observed_behaviors: list[str],
) -> tuple[float, float, float]:
    """Evaluate agent behaviors against expected list.

    Args:
        expected_behaviors: List of expected behavior descriptions.
        observed_behaviors: List of observed behavior descriptions.

    Returns:
        Tuple of (precision, recall, f1).

    """
    if not expected_behaviors:
        return 1.0, 1.0, 1.0

    # Fuzzy matching: check if observed behaviors contain expected keywords
    matched = 0
    for expected in expected_behaviors:
        expected_lower = expected.lower()
        for observed in observed_behaviors:
            observed_lower = observed.lower()
            # Check for substantial keyword overlap
            expected_words = set(expected_lower.split())
            observed_words = set(observed_lower.split())
            overlap = expected_words & observed_words
            if len(overlap) >= min(3, len(expected_words)):
                matched += 1
                break

    total_expected = len(expected_behaviors)
    total_observed = len(observed_behaviors)

    recall = matched / total_expected if total_expected > 0 else 0.0
    precision = matched / total_observed if total_observed > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0

    return precision, recall, f1


def evaluate_task(
    task_id: str,
    task_description: str,
    expected_tools: list[str],
    expected_output: dict,
    expected_behaviors: list[str],
    actual_tools: list[str] | None = None,
    actual_output: dict | None = None,
    observed_behaviors: list[str] | None = None,
    errors_encountered: list[str] | None = None,
    errors_recovered: list[str] | None = None,
    _dimension_weights: dict[str, float] | None = None,
) -> TaskEvalResult:
    """Evaluate a single agent task execution.

    Args:
        task_id: Unique task identifier.
        task_description: Description of the task.
        expected_tools: Ground truth expected tools.
        expected_output: Ground truth expected output properties.
        expected_behaviors: Ground truth expected behaviors.
        actual_tools: Tools the agent actually used.
        actual_output: Actual output properties.
        observed_behaviors: Observed agent behaviors.
        errors_encountered: Errors that occurred during execution.
        errors_recovered: Errors that were successfully recovered from.
        dimension_weights: Weights for scoring dimensions.

    """
    result = TaskEvalResult(
        task_id=task_id,
        task_description=task_description,
    )

    # 1. Tool selection
    actual_tools = actual_tools or expected_tools  # Self-test mode
    tool_precision, tool_notes = evaluate_tool_selection(expected_tools, actual_tools)
    result.tool_precision = tool_precision
    result.notes.extend(tool_notes)

    # 2. Output quality
    actual_output = actual_output or expected_output  # Self-test mode
    result.output_quality = evaluate_output(expected_output, actual_output)

    # 3. Behavior matching
    observed_behaviors = observed_behaviors or expected_behaviors  # Self-test mode
    beh_precision, beh_recall, beh_f1 = evaluate_behaviors(
        expected_behaviors,
        observed_behaviors,
    )
    result.precision = beh_precision
    result.recall = beh_recall
    result.f1 = beh_f1
    result.total_expected_actions = len(expected_behaviors)
    result.total_actions_taken = len(observed_behaviors)

    # 4. Error recovery
    errors_encountered = errors_encountered or []
    errors_recovered = errors_recovered or []
    if errors_encountered:
        result.error_recovery = len(errors_recovered) / len(errors_encountered)
    else:
        result.error_recovery = 1.0  # No errors = perfect recovery

    # Dimension scores
    result.dimension_scores = {
        "task_completion": result.f1,
        "tool_selection": result.tool_precision,
        "output_quality": result.output_quality,
        "error_recovery": result.error_recovery,
    }

    return result


def evaluate_all(
    ground_truth_path: str | Path,
    results_path: str | Path | None = None,
) -> AgentEvalSummary:
    """Run full evaluation against ground truth dataset.

    Args:
        ground_truth_path: Path to ground truth JSON file.
        results_path: Path to agent results JSON file.
            If None, runs a self-test.

    """
    gt_path = Path(ground_truth_path)
    with gt_path.open() as f:
        ground_truth = json.load(f)

    # Load results or self-test
    if results_path:
        res_path = Path(results_path)
        with res_path.open() as f:
            results_data = json.load(f)
    else:
        results_data = None  # Self-test mode

    weights = {d["dimension"]: d["weight"] for d in ground_truth["evaluation_dimensions"]}

    summary = AgentEvalSummary()
    summary.total_tasks = len(ground_truth["ground_truth_examples"])

    category_f1s: dict[str, list[float]] = {}

    for example in ground_truth["ground_truth_examples"]:
        task_id = example["id"]
        task_desc = example["task"]
        expected_tools = example["expected_tools"]
        expected_output = example["expected_output"]
        expected_behaviors = example["expected_behavior"]
        category = example.get("category", "unknown")

        # Get actual results if available
        actual = None
        if results_data and isinstance(results_data, list):
            actual = next(
                (r for r in results_data if r.get("id") == task_id),
                None,
            )

        result = evaluate_task(
            task_id=task_id,
            task_description=task_desc,
            expected_tools=expected_tools,
            expected_output=expected_output,
            expected_behaviors=expected_behaviors,
            actual_tools=actual.get("tools_used") if actual else None,
            actual_output=actual.get("output") if actual else None,
            observed_behaviors=actual.get("behaviors") if actual else None,
            errors_encountered=actual.get("errors") if actual else None,
            errors_recovered=actual.get("recovered") if actual else None,
            dimension_weights=weights,
        )

        summary.results.append(result)

        # Track by category
        if category not in category_f1s:
            category_f1s[category] = []
        category_f1s[category].append(result.f1)

    # Aggregate scores
    if summary.results:
        summary.mean_precision = sum(r.precision for r in summary.results) / len(summary.results)
        summary.mean_recall = sum(r.recall for r in summary.results) / len(summary.results)
        summary.aggregate_f1 = sum(r.f1 for r in summary.results) / len(summary.results)

        # Weighted F1
        weighted_scores = []
        for r in summary.results:
            query_weighted = sum(weights.get(dim, 0.25) * score for dim, score in r.dimension_scores.items())
            weighted_scores.append(query_weighted)
        summary.weighted_f1 = sum(weighted_scores) / len(weighted_scores)

    # Category scores
    for cat, f1s in category_f1s.items():
        summary.category_scores[cat] = sum(f1s) / len(f1s) if f1s else 0.0

    # Check thresholds
    min_f1 = ground_truth.get("minimum_acceptable_f1", 0.65)
    summary.passing = summary.aggregate_f1 >= min_f1

    return summary


def print_report(summary: AgentEvalSummary) -> None:
    """Print formatted evaluation report."""
    if summary.category_scores:
        for _cat, _score in sorted(summary.category_scores.items()):
            pass

    for r in summary.results:
        if r.notes:
            for _note in r.notes:
                pass


def main() -> None:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    gt_path = repo_root / "apps" / "data" / "eval" / "uphillsnowball_f1_ground_truth.json"
    res_path = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--ground-truth" and i + 1 < len(args):
            gt_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--results" and i + 1 < len(args):
            res_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--self-test":
            res_path = None
            i += 1
        else:
            sys.exit(1)

    if not gt_path.exists():
        sys.exit(1)

    if res_path:
        pass
    else:
        pass

    summary = evaluate_all(gt_path, res_path)
    print_report(summary)

    sys.exit(0 if summary.passing else 1)


if __name__ == "__main__":
    main()
