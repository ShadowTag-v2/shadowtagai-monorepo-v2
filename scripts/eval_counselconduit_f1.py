#!/usr/bin/env python3
from __future__ import annotations

"""CounselConduit F1 Evaluation Harness

Measures legal citation accuracy using precision, recall, and F1 scoring
across 4 dimensions: accuracy, relevance, completeness, shepardization.

Usage:
    python scripts/eval_counselconduit_f1.py [--ground-truth PATH] [--predictions PATH]
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CitationEvalResult:
    """Result of evaluating a single query."""

    query_id: str
    query_text: str
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    correct_citations: int = 0
    total_predicted: int = 0
    total_expected: int = 0
    false_positives: list[str] = field(default_factory=list)
    false_negatives: list[str] = field(default_factory=list)
    dimension_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class EvalSummary:
    """Summary of all evaluation results."""

    aggregate_f1: float = 0.0
    weighted_f1: float = 0.0
    mean_precision: float = 0.0
    mean_recall: float = 0.0
    total_queries: int = 0
    passing: bool = False
    results: list[CitationEvalResult] = field(default_factory=list)


def normalize_citation(citation: str) -> str:
    """Normalize a citation for comparison.

    Strips whitespace, lowercases, and removes common formatting differences.
    """
    normalized = citation.strip().lower()
    # Remove extra spaces
    normalized = " ".join(normalized.split())
    # Remove trailing periods
    return normalized.rstrip(".")


def citation_matches(predicted: str, expected: str, fuzzy: bool = True) -> bool:
    """Check if a predicted citation matches an expected one.

    Args:
        predicted: The citation produced by the system.
        expected: The ground truth citation.
        fuzzy: If True, use fuzzy matching (substring containment).

    """
    p = normalize_citation(predicted)
    e = normalize_citation(expected)

    # Exact match
    if p == e:
        return True

    if fuzzy:
        # Check if key parts of the expected citation appear in predicted
        # Extract case name and reporter
        parts = e.split(",")
        if len(parts) >= 2:
            case_name = parts[0].strip()
            # Check if case name appears in predicted
            if case_name in p:
                return True

        # Check if predicted contains expected or vice versa
        if e in p or p in e:
            return True

    return False


def evaluate_query(
    query_id: str,
    query_text: str,
    expected_citations: list[str],
    predicted_citations: list[str],
    dimension_weights: dict[str, float] | None = None,
) -> CitationEvalResult:
    """Evaluate a single query's citations.

    Args:
        query_id: Unique identifier for the query.
        query_text: The legal question asked.
        expected_citations: Ground truth citations.
        predicted_citations: System-produced citations.
        dimension_weights: Optional weights for scoring dimensions.

    """
    result = CitationEvalResult(
        query_id=query_id,
        query_text=query_text,
        total_predicted=len(predicted_citations),
        total_expected=len(expected_citations),
    )

    # Match predicted to expected
    matched_expected = set()
    matched_predicted = set()

    for i, pred in enumerate(predicted_citations):
        for j, exp in enumerate(expected_citations):
            if j not in matched_expected and citation_matches(pred, exp):
                matched_expected.add(j)
                matched_predicted.add(i)
                result.correct_citations += 1
                break

    # False positives: predicted but not in ground truth
    for i, pred in enumerate(predicted_citations):
        if i not in matched_predicted:
            result.false_positives.append(pred)

    # False negatives: expected but not predicted
    for j, exp in enumerate(expected_citations):
        if j not in matched_expected:
            result.false_negatives.append(exp)

    # Calculate precision, recall, F1
    if result.total_predicted > 0:
        result.precision = result.correct_citations / result.total_predicted
    if result.total_expected > 0:
        result.recall = result.correct_citations / result.total_expected
    if result.precision + result.recall > 0:
        result.f1 = 2 * (result.precision * result.recall) / (result.precision + result.recall)

    # Dimension scores (simplified — full implementation would check each dimension)

    result.dimension_scores = {
        "citation_accuracy": result.precision,
        "citation_relevance": result.precision * 0.9,  # Proxy: accuracy implies relevance
        "citation_completeness": result.recall,
        "shepardization_status": 1.0 if result.correct_citations > 0 else 0.0,
    }

    return result


def evaluate_all(
    ground_truth_path: str | Path,
    predictions_path: str | Path | None = None,
) -> EvalSummary:
    """Run full evaluation against ground truth dataset.

    Args:
        ground_truth_path: Path to ground truth JSON file.
        predictions_path: Path to predictions JSON file.
            If None, runs a self-test with ground truth as both.

    """
    gt_path = Path(ground_truth_path)
    with gt_path.open() as f:
        ground_truth = json.load(f)

    # Load predictions or self-test
    if predictions_path:
        pred_path = Path(predictions_path)
        with pred_path.open() as f:
            predictions = json.load(f)
    else:
        # Self-test: use ground truth as predictions (should get F1 = 1.0)
        predictions = {ex["id"]: ex["expected_citations"] for ex in ground_truth["ground_truth_examples"]}

    # Get dimension weights
    weights = {d["dimension"]: d["weight"] for d in ground_truth["evaluation_dimensions"]}

    summary = EvalSummary()
    summary.total_queries = len(ground_truth["ground_truth_examples"])

    for example in ground_truth["ground_truth_examples"]:
        query_id = example["id"]
        query_text = example["query"]
        expected = example["expected_citations"]

        # Get predicted citations for this query
        if isinstance(predictions, dict):
            predicted = predictions.get(query_id, [])
        else:
            # Assume list format
            predicted = next(
                (p.get("citations", []) for p in predictions if p.get("id") == query_id),
                [],
            )

        result = evaluate_query(query_id, query_text, expected, predicted, weights)
        summary.results.append(result)

    # Aggregate scores
    if summary.results:
        summary.mean_precision = sum(r.precision for r in summary.results) / len(summary.results)
        summary.mean_recall = sum(r.recall for r in summary.results) / len(summary.results)
        summary.aggregate_f1 = sum(r.f1 for r in summary.results) / len(summary.results)

        # Weighted F1 across dimensions
        weighted_scores = []
        for r in summary.results:
            query_weighted = sum(weights.get(dim, 0.25) * score for dim, score in r.dimension_scores.items())
            weighted_scores.append(query_weighted)
        summary.weighted_f1 = sum(weighted_scores) / len(weighted_scores)

    # Check thresholds
    min_f1 = ground_truth.get("minimum_acceptable_f1", 0.70)
    summary.passing = summary.aggregate_f1 >= min_f1

    return summary


def print_report(summary: EvalSummary) -> None:
    """Print formatted evaluation report."""
    for r in summary.results:
        if r.false_positives:
            pass
        if r.false_negatives:
            for _fn in r.false_negatives[:3]:
                pass



def main() -> None:
    """Main entry point."""
    # Default paths
    repo_root = Path(__file__).parent.parent
    gt_path = repo_root / "apps" / "data" / "eval" / "counselconduit_f1_ground_truth.json"
    pred_path = None

    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--ground-truth" and i + 1 < len(args):
            gt_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--predictions" and i + 1 < len(args):
            pred_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--self-test":
            pred_path = None
            i += 1
        else:
            sys.exit(1)

    if not gt_path.exists():
        sys.exit(1)

    if pred_path:
        pass
    else:
        pass

    summary = evaluate_all(gt_path, pred_path)
    print_report(summary)

    # Exit with appropriate code
    sys.exit(0 if summary.passing else 1)


if __name__ == "__main__":
    main()
