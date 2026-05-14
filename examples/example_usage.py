#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Example usage of KERNEL prompt engineering framework.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_engineering import KernelValidator, PromptAnalyzer
from prompt_engineering.metrics import PromptExecution, MetricsTracker
from datetime import datetime


def example_validate_prompt():
    """Example: Validate a prompt against KERNEL framework."""
    print("=" * 60)
    print("EXAMPLE 1: Validating Prompts")
    print("=" * 60)

    # Bad prompt (violates KERNEL)
    bad_prompt = """
    Help me write a script to process some data files and make them more efficient.
    Use the latest best practices and modern techniques.
    """

    # Good prompt (follows KERNEL)
    good_prompt = """
    TASK: Python script to merge CSVs

    INPUT: Multiple CSV files in ./data/ directory with identical column structure

    CONSTRAINTS:
    - Use pandas only (no other libraries)
    - Under 50 lines of code
    - No functions over 20 lines
    - Preserve original column order

    OUTPUT: Single merged.csv file in ./output/ directory

    VERIFICATION: Successfully runs on test_data/ directory with 10 sample CSVs
    """

    validator = KernelValidator(strict=False)

    print("\n--- Bad Prompt ---")
    bad_result = validator.validate(bad_prompt)
    print(bad_result.summary)
    print(f"Score: {bad_result.overall_score:.1%}\n")

    print("--- Good Prompt ---")
    good_result = validator.validate(good_prompt)
    print(good_result.summary)
    print(f"Score: {good_result.overall_score:.1%}\n")


def example_analyze_prompt():
    """Example: Analyze prompt quality and get optimization suggestions."""
    print("=" * 60)
    print("EXAMPLE 2: Analyzing Prompt Quality")
    print("=" * 60)

    prompt = """
    CONTEXT: Building a REST API for user authentication

    TASK: Implement JWT-based authentication endpoints

    CONSTRAINTS:
    - Python 3.11+ with FastAPI
    - No external auth libraries (implement JWT manually)
    - Maximum token lifetime: 24 hours
    - Include refresh token mechanism

    OUTPUT:
    - /auth/login endpoint (POST)
    - /auth/refresh endpoint (POST)
    - /auth/logout endpoint (POST)
    - Middleware for protected routes

    VERIFICATION:
    - All endpoints return proper status codes
    - Tokens validate correctly
    - Refresh mechanism works
    """

    analyzer = PromptAnalyzer(model="gemini-2.0-pro")
    report = analyzer.analyze(prompt, expected_output_tokens=2000)

    print(f"\nWord Count: {report.word_count}")
    print(f"Estimated Tokens: {report.token_estimate}")
    print(f"Clarity Score: {report.clarity_score:.1%}")
    print(f"Complexity Score: {report.complexity_score:.1%}")
    print(f"Estimated Cost: ${report.estimated_cost_usd:.4f}")
    print(f"Estimated Time: {report.estimated_response_time_sec:.1f}s")

    if report.suggestions:
        print("\nSuggestions:")
        for suggestion in report.suggestions:
            print(f"  • {suggestion}")


def example_compare_prompts():
    """Example: Compare before/after KERNEL optimization."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Comparing Prompts (Before/After KERNEL)")
    print("=" * 60)

    before = """
    I need you to help me build a complete e-commerce website with a shopping cart,
    user accounts, payment processing, product catalog, reviews, and an admin panel.
    Make sure it looks modern and professional and uses the latest technologies.
    Also add some good security practices and make it fast.
    """

    after = """
    TASK: Design database schema for e-commerce product catalog

    CONTEXT: Building e-commerce platform, starting with product management

    CONSTRAINTS:
    - PostgreSQL 15
    - Support 100K+ products
    - Include: products, categories, variants, inventory
    - Normalized to 3NF

    OUTPUT: SQL schema file with:
    - CREATE TABLE statements
    - Indexes on lookup fields
    - Foreign key constraints

    VERIFICATION: Schema validates with no errors, supports sample queries
    """

    analyzer = PromptAnalyzer()
    comparison = analyzer.compare_prompts(before, after, labels=["Before KERNEL", "After KERNEL"])

    print("\nBefore KERNEL:")
    print(f"  Tokens: {comparison['analyses'][0].token_estimate}")
    print(f"  Clarity: {comparison['analyses'][0].clarity_score:.1%}")
    print(f"  Cost: ${comparison['analyses'][0].estimated_cost_usd:.4f}")

    print("\nAfter KERNEL:")
    print(f"  Tokens: {comparison['analyses'][1].token_estimate}")
    print(f"  Clarity: {comparison['analyses'][1].clarity_score:.1%}")
    print(f"  Cost: ${comparison['analyses'][1].estimated_cost_usd:.4f}")

    comp = comparison["comparison"]
    print("\nImprovements:")
    print(f"  Token Reduction: {comp['token_difference']} tokens")
    print(f"  Clarity Improvement: {comp['clarity_improvement']:+.1%}")
    print(f"  Winner: {comparison['winner']}")


def example_track_metrics():
    """Example: Track prompt performance over time."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Tracking Metrics Over Time")
    print("=" * 60)

    tracker = MetricsTracker()

    # Simulate some executions before KERNEL
    before_prompts = ["before_1", "before_2", "before_3"]
    for i, prompt_id in enumerate(before_prompts):
        execution = PromptExecution(
            prompt_id=prompt_id,
            prompt_text="<before KERNEL prompt>",
            timestamp=datetime.now(),
            model="gemini-2.0-pro",
            success=True,
            first_try_success=(i == 0),  # Only 1 out of 3 succeeded first try
            revisions_needed=2 if i > 0 else 0,
            tokens_used=800,
            cost_usd=0.024,
            response_time_sec=12.5,
        )
        tracker.track_execution(execution)

    # Simulate some executions after KERNEL
    after_prompts = ["after_1", "after_2", "after_3"]
    for prompt_id in after_prompts:
        execution = PromptExecution(
            prompt_id=prompt_id,
            prompt_text="<after KERNEL prompt>",
            timestamp=datetime.now(),
            model="gemini-2.0-pro",
            success=True,
            first_try_success=True,  # All succeeded first try
            revisions_needed=0,
            tokens_used=350,
            cost_usd=0.010,
            response_time_sec=4.2,
        )
        tracker.track_execution(execution)

    # Generate comparison report
    report = tracker.generate_comparison_report(before_prompts, after_prompts)
    print(report)


def example_gemini_ingestion_validation():
    """Example: Validate the Gemini Ingestion Layer prompt."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Validating Gemini Ingestion Layer Prompt")
    print("=" * 60)

    # Read the actual prompt from docs (simplified version for example)
    gemini_prompt = """
    CONTEXT:
    You are analyzing the Gemini Ingestion Layer, a pre-production intelligence
    collection pipeline within the PNKLN Core Stack.

    INPUT ARTIFACTS:
    - Pipeline architecture documentation (GKE CronJob specs)
    - Multi-source configuration files (YouTube, Twitter, News)
    - Ethical crawling policies (robots.txt, rate limiting)

    TASK:
    Perform comprehensive analysis across six dimensions:
    1. Ethical Compliance Model
    2. Multi-Source Coverage Analysis
    3. Tier Classification Metrics
    4. Runtime Efficiency
    5. Cost Optimization
    6. AM Briefing Delivery Effectiveness

    CONSTRAINTS:
    - Analysis based on pre-production specs only
    - Minimum confidence threshold: ≥60%
    - Focus on the 6 dimensions (do not expand scope)
    - Do NOT analyze downstream services

    OUTPUT FORMAT:
    Structured analysis report with:
    - Executive Summary
    - Findings for each dimension with confidence scores
    - Actionable recommendations prioritized by impact
    - Cost projections and sensitivity analysis

    VERIFICATION CRITERIA:
    - All 6 dimensions analyzed
    - Every finding includes confidence percentage
    - Recommendations are actionable (not vague)
    - Overall confidence ≥60%
    """

    validator = KernelValidator(strict=False)
    result = validator.validate(gemini_prompt)

    print(result.summary)
    print(f"\nOverall Score: {result.overall_score:.1%}")

    # Show which principles passed
    for name, score in result.principle_scores.items():
        status = "✓" if score.passed else "✗"
        print(f"{status} {score.principle}: {score.score:.1%}")


if __name__ == "__main__":
    example_validate_prompt()
    example_analyze_prompt()
    example_compare_prompts()
    example_track_metrics()
    example_gemini_ingestion_validation()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
