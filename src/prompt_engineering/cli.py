#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
KERNEL CLI Tool

Command-line interface for KERNEL prompt validation and analysis.
"""

import argparse
import sys
from pathlib import Path
from .kernel_validator import KernelValidator
from .prompt_analyzer import PromptAnalyzer


def validate_command(args):
    """Validate a prompt against KERNEL framework."""
    # Read prompt from file or stdin
    if args.file:
        prompt = Path(args.file).read_text()
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read()

    validator = KernelValidator(strict=args.strict)
    result = validator.validate(prompt)

    # Print summary
    print(result.summary)
    print(f"\nOverall Score: {result.overall_score:.1%}")
    print(f"Status: {'✓ PASSED' if result.passed else '✗ FAILED'}")
    print(f"Estimated Tokens: {result.token_estimate}")

    # Print detailed feedback
    print("\n" + "=" * 60)
    print("DETAILED FEEDBACK")
    print("=" * 60)

    for principle_name, score in result.principle_scores.items():
        status_icon = "✓" if score.passed else "✗"
        print(f"\n{status_icon} {score.principle} - {score.score:.1%}")

        if score.feedback:
            print("  Feedback:")
            for fb in score.feedback:
                print(f"    • {fb}")

        if score.recommendations:
            print("  Recommendations:")
            for rec in score.recommendations:
                print(f"    → {rec}")

    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


def analyze_command(args):
    """Analyze prompt quality and efficiency."""
    # Read prompt from file or stdin
    if args.file:
        prompt = Path(args.file).read_text()
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read()

    analyzer = PromptAnalyzer(model=args.model)
    report = analyzer.analyze(prompt, expected_output_tokens=args.output_tokens)

    # Print report
    print("=" * 60)
    print("PROMPT ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nModel: {args.model}")
    print("\nMetrics:")
    print(f"  Word Count: {report.word_count}")
    print(f"  Estimated Tokens: {report.token_estimate}")
    print(f"  Sentence Count: {report.sentence_count}")
    print(f"  Avg Sentence Length: {report.avg_sentence_length:.1f} words")
    print(f"  Complexity Score: {report.complexity_score:.1%}")
    print(f"  Clarity Score: {report.clarity_score:.1%}")

    print("\nCost Estimates:")
    print(f"  Estimated Cost: ${report.estimated_cost_usd:.4f}")
    print(f"  Estimated Response Time: {report.estimated_response_time_sec:.1f}s")

    if report.suggestions:
        print("\nSuggestions:")
        for i, suggestion in enumerate(report.suggestions, 1):
            print(f"  {i}. {suggestion}")


def compare_command(args):
    """Compare two prompts."""
    prompt1 = Path(args.file1).read_text()
    prompt2 = Path(args.file2).read_text()

    analyzer = PromptAnalyzer(model=args.model)
    comparison = analyzer.compare_prompts(prompt1, prompt2, labels=[args.file1, args.file2])

    print("=" * 60)
    print("PROMPT COMPARISON")
    print("=" * 60)

    for i, (label, analysis) in enumerate(zip(comparison["labels"], comparison["analyses"])):
        print(f"\n{label}:")
        print(f"  Tokens: {analysis.token_estimate}")
        print(f"  Clarity: {analysis.clarity_score:.1%}")
        print(f"  Complexity: {analysis.complexity_score:.1%}")
        print(f"  Cost: ${analysis.estimated_cost_usd:.4f}")

    print("\nDifferences:")
    comp = comparison["comparison"]
    print(f"  Token Difference: {comp['token_difference']:+d}")
    print(f"  Cost Difference: ${comp['cost_difference_usd']:+.4f}")
    print(f"  Time Difference: {comp['time_difference_sec']:+.1f}s")
    print(f"  Clarity Change: {comp['clarity_improvement']:+.1%}")
    print(f"  Complexity Change: {comp['complexity_change']:+.1%}")

    print(f"\nWinner: {comparison['winner']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KERNEL Prompt Engineering Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a prompt from file
  kernel validate --file my_prompt.txt

  # Validate from stdin
  cat prompt.txt | kernel validate

  # Validate with strict mode
  kernel validate --file prompt.txt --strict

  # Analyze a prompt
  kernel analyze --file prompt.txt --model gemini-2.0-pro

  # Compare two prompts
  kernel compare before.txt after.txt
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate prompt against KERNEL")
    validate_parser.add_argument("--file", "-f", help="Prompt file (or use stdin)")
    validate_parser.add_argument("--prompt", "-p", help="Prompt text directly")
    validate_parser.add_argument("--strict", action="store_true", help="Use strict validation (80% threshold)")
    validate_parser.set_defaults(func=validate_command)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze prompt quality")
    analyze_parser.add_argument("--file", "-f", help="Prompt file (or use stdin)")
    analyze_parser.add_argument("--prompt", "-p", help="Prompt text directly")
    analyze_parser.add_argument("--model", default="gemini-2.0-pro", help="Target model")
    analyze_parser.add_argument("--output-tokens", type=int, default=1000, help="Expected output tokens")
    analyze_parser.set_defaults(func=analyze_command)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two prompts")
    compare_parser.add_argument("file1", help="First prompt file")
    compare_parser.add_argument("file2", help="Second prompt file")
    compare_parser.add_argument("--model", default="gemini-2.0-pro", help="Target model")
    compare_parser.set_defaults(func=compare_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
