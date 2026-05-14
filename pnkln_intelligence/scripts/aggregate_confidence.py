#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Gemini Analysis Confidence Score Aggregator

Parses Gemini Ingestion Layer analysis output and computes overall confidence score.

Usage:
    python aggregate_confidence.py analysis_report.md

Output:
    - Dimension-level scores
    - Overall weighted confidence
    - Go/no-go recommendation
"""

import re
import sys
from pathlib import Path


class ConfidenceAggregator:
    """Analyzes Gemini output for confidence metrics and recommendations"""

    # Dimension weights (must sum to 1.0)
    DIMENSION_WEIGHTS = {
        "architecture": 0.20,
        "cost_efficiency": 0.15,
        "ethical_compliance": 0.20,
        "data_quality": 0.20,
        "operational_reliability": 0.15,
        "integration_health": 0.10,
    }

    CONFIDENCE_THRESHOLD_APPROVED = 60
    CONFIDENCE_THRESHOLD_WARNING = 50

    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.report_text = self._load_report()
        self.dimension_scores: dict[str, int] = {}
        self.overall_confidence: float | None = None
        self.recommendations: list[str] = []

    def _load_report(self) -> str:
        """Load analysis report from file"""
        if not self.report_path.exists():
            raise FileNotFoundError(f"Report not found: {self.report_path}")

        with open(self.report_path, encoding="utf-8") as f:
            return f.read()

    def extract_confidence_scores(self) -> dict[str, int]:
        """Extract confidence percentages from analysis sections"""
        # Pattern matches: (Confidence: 72%), (confidence: 72%), etc.
        pattern = r"\((?:C|c)onfidence:\s*(\d+)%\)"
        matches = re.findall(pattern, self.report_text)

        if not matches:
            print("⚠️  No confidence scores found in report", file=sys.stderr)
            return {}

        scores = [int(score) for score in matches]

        # Map to dimensions (order matters - should match analysis output)
        dimension_names = list(self.DIMENSION_WEIGHTS.keys())

        for i, score in enumerate(scores[:6]):  # Max 6 dimensions
            if i < len(dimension_names):
                self.dimension_scores[dimension_names[i]] = score

        return self.dimension_scores

    def compute_overall_confidence(self) -> float:
        """Compute weighted average confidence across dimensions"""
        if not self.dimension_scores:
            return 0.0

        weighted_sum = sum(score * self.DIMENSION_WEIGHTS.get(dim, 0) for dim, score in self.dimension_scores.items())

        self.overall_confidence = round(weighted_sum, 1)
        return self.overall_confidence

    def extract_recommendations(self) -> list[str]:
        """Extract key recommendations from analysis"""
        # Look for numbered lists in recommendations section
        rec_section = re.search(r"## (?:10\.|Recommended Actions|Recommendations)(.*?)(?=##|$)", self.report_text, re.DOTALL | re.IGNORECASE)

        if not rec_section:
            return []

        # Extract bullet points or numbered items
        rec_text = rec_section.group(1)
        rec_pattern = r"(?:^|\n)\s*(?:\d+\.|-|\*)\s*\*\*\[(.*?)\]\*\*(.+?)(?=\n(?:\d+\.|-|\*)|$)"
        matches = re.findall(rec_pattern, rec_text, re.MULTILINE)

        self.recommendations = [f"[{priority}] {desc.strip()}" for priority, desc in matches]

        return self.recommendations

    def generate_summary(self) -> str:
        """Generate human-readable summary"""
        if self.overall_confidence is None:
            self.compute_overall_confidence()

        status_emoji = "✅" if self.overall_confidence >= self.CONFIDENCE_THRESHOLD_APPROVED else "❌"
        status_text = "APPROVED" if self.overall_confidence >= self.CONFIDENCE_THRESHOLD_APPROVED else "NEEDS WORK"

        summary = f"""
{"=" * 70}
GEMINI INGESTION LAYER ANALYSIS - CONFIDENCE SUMMARY
{"=" * 70}

Report: {self.report_path.name}
Analyzed: {self.report_path.stat().st_mtime}

DIMENSION SCORES:
"""

        for dim, score in self.dimension_scores.items():
            emoji = "✅" if score >= 60 else ("⚠️" if score >= 50 else "❌")
            weight_pct = self.DIMENSION_WEIGHTS.get(dim, 0) * 100
            summary += f"  {emoji} {dim.replace('_', ' ').title():<30} {score:>3}% (weight: {weight_pct:.0f}%)\n"

        summary += f"""
OVERALL CONFIDENCE: {self.overall_confidence}%
STATUS: {status_emoji} {status_text}

THRESHOLDS:
  - Approved for deployment: ≥{self.CONFIDENCE_THRESHOLD_APPROVED}%
  - Warning level: {self.CONFIDENCE_THRESHOLD_WARNING}-{self.CONFIDENCE_THRESHOLD_APPROVED - 1}%
  - Needs significant work: <{self.CONFIDENCE_THRESHOLD_WARNING}%

"""

        if self.overall_confidence < self.CONFIDENCE_THRESHOLD_APPROVED:
            summary += "⚠️  DEPLOYMENT BLOCKED - Address concerns before proceeding\n\n"

            # Identify low-scoring dimensions
            low_scores = [(dim, score) for dim, score in self.dimension_scores.items() if score < self.CONFIDENCE_THRESHOLD_APPROVED]

            if low_scores:
                summary += "LOW-CONFIDENCE DIMENSIONS:\n"
                for dim, score in sorted(low_scores, key=lambda x: x[1]):
                    summary += f"  - {dim.replace('_', ' ').title()}: {score}%\n"
                summary += "\n"

        if self.recommendations:
            summary += "TOP RECOMMENDATIONS:\n"
            for i, rec in enumerate(self.recommendations[:5], 1):
                summary += f"  {i}. {rec}\n"
            summary += "\n"

        summary += f"{'=' * 70}\n"

        return summary

    def export_metrics(self) -> dict:
        """Export metrics as structured data for programmatic use"""
        return {
            "report_file": str(self.report_path),
            "overall_confidence": self.overall_confidence,
            "approved": self.overall_confidence >= self.CONFIDENCE_THRESHOLD_APPROVED,
            "dimension_scores": self.dimension_scores,
            "recommendations_count": len(self.recommendations),
            "recommendations": self.recommendations,
            "thresholds": {"approved": self.CONFIDENCE_THRESHOLD_APPROVED, "warning": self.CONFIDENCE_THRESHOLD_WARNING},
        }


def main():
    """CLI entry point"""
    if len(sys.argv) != 2:
        print("Usage: python aggregate_confidence.py <analysis_report.md>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python aggregate_confidence.py docs/analysis/gemini_ingestion_2025-11-15.md", file=sys.stderr)
        sys.exit(1)

    report_path = sys.argv[1]

    try:
        aggregator = ConfidenceAggregator(report_path)

        # Extract data
        aggregator.extract_confidence_scores()
        aggregator.compute_overall_confidence()
        aggregator.extract_recommendations()

        # Print summary
        print(aggregator.generate_summary())

        # Export JSON (optional)
        import json

        json_output = json.dumps(aggregator.export_metrics(), indent=2)

        json_path = Path(report_path).with_suffix(".confidence.json")
        json_path.write_text(json_output, encoding="utf-8")
        print(f"✅ Metrics exported to: {json_path}\n")

        # Exit code based on approval status
        sys.exit(0 if aggregator.overall_confidence >= aggregator.CONFIDENCE_THRESHOLD_APPROVED else 1)

    except Exception as e:
        print(f"❌ Error processing report: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
