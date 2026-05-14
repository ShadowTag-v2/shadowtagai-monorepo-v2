# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tests for KERNEL validator
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_engineering import KernelValidator


def test_simple_prompt_passes():
    """Test that a simple, well-structured prompt passes."""
    prompt = """
    TASK: Write a Python function to calculate fibonacci numbers

    CONSTRAINTS:
    - Python 3.11+
    - Use recursion
    - Under 15 lines
    - Include type hints

    OUTPUT: Single function in fib.py

    VERIFY: fib(10) == 55
    """

    validator = KernelValidator(strict=False)
    result = validator.validate(prompt)

    assert result.passed, "Simple well-structured prompt should pass"
    assert result.overall_score > 0.6


def test_verbose_prompt_fails_simplicity():
    """Test that verbose prompt fails Keep it Simple."""
    prompt = " ".join(["This is a very long prompt with many words"] * 50)

    validator = KernelValidator()
    result = validator.validate(prompt)

    k_score = result.principle_scores["K"]
    assert not k_score.passed, "Verbose prompt should fail Keep it Simple"


def test_temporal_references_fail_reproducibility():
    """Test that temporal references fail Reproducible."""
    prompt = """
    TASK: Analyze current trends in machine learning using latest best practices
    """

    validator = KernelValidator()
    result = validator.validate(prompt)

    r_score = result.principle_scores["R"]
    assert not r_score.passed, "Temporal references should fail Reproducible"


def test_no_constraints_fails():
    """Test that prompt without constraints fails."""
    prompt = """
    TASK: Write a function to process data
    """

    validator = KernelValidator()
    result = validator.validate(prompt)

    e2_score = result.principle_scores["E2"]
    assert not e2_score.passed, "No constraints should fail Explicit Constraints"


def test_vague_terms_fail_verification():
    """Test that vague quality terms fail Easy to Verify."""
    prompt = """
    TASK: Make the code better and more professional
    """

    validator = KernelValidator()
    result = validator.validate(prompt)

    e1_score = result.principle_scores["E1"]
    assert not e1_score.passed, "Vague terms should fail Easy to Verify"


def test_structured_prompt_passes_logical():
    """Test that well-structured prompt passes Logical Structure."""
    prompt = """
    CONTEXT: Building authentication system

    TASK: Implement JWT tokens

    CONSTRAINTS:
    - Python 3.11
    - No external libraries
    - 24 hour expiry

    OUTPUT: auth.py file

    VERIFY: Tokens validate correctly
    """

    validator = KernelValidator()
    result = validator.validate(prompt)

    l_score = result.principle_scores["L"]
    assert l_score.passed, "Well-structured prompt should pass Logical Structure"


def test_strict_mode_higher_threshold():
    """Test that strict mode requires higher scores."""
    # Mediocre prompt that passes normal but fails strict
    prompt = """
    TASK: Write code

    CONSTRAINTS:
    - Python

    OUTPUT: code.py
    """

    normal_validator = KernelValidator(strict=False)
    strict_validator = KernelValidator(strict=True)

    normal_result = normal_validator.validate(prompt)
    strict_result = strict_validator.validate(prompt)

    # Strict mode should have stricter requirements
    assert strict_validator.pass_threshold > normal_validator.pass_threshold


def test_gemini_ingestion_prompt_quality():
    """Test the actual Gemini Ingestion Layer prompt."""
    prompt = """
    CONTEXT:
    You are analyzing the Gemini Ingestion Layer, a pre-production intelligence
    collection pipeline within the PNKLN Core Stack.

    INPUT ARTIFACTS:
    - Pipeline architecture documentation (GKE CronJob specs)
    - Multi-source configuration files (YouTube, Twitter, News)

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
    - Focus on 6 dimensions only
    - Do NOT analyze downstream services

    OUTPUT FORMAT:
    Structured analysis report with executive summary, findings per dimension,
    actionable recommendations, cost projections

    VERIFICATION CRITERIA:
    - All 6 dimensions analyzed with confidence scores
    - Recommendations are actionable (not vague)
    - Overall confidence ≥60%
    """

    validator = KernelValidator(strict=False)
    result = validator.validate(prompt)

    # Should pass most principles
    assert result.overall_score > 0.7, "Gemini Ingestion prompt should score well"

    # Should definitely pass structure
    assert result.principle_scores["L"].passed


if __name__ == "__main__":
    # Run tests
    test_simple_prompt_passes()
    test_verbose_prompt_fails_simplicity()
    test_temporal_references_fail_reproducibility()
    test_no_constraints_fails()
    test_vague_terms_fail_verification()
    test_structured_prompt_passes_logical()
    test_strict_mode_higher_threshold()
    test_gemini_ingestion_prompt_quality()

    print("✓ All tests passed!")
