#!/usr/bin/env python3
"""Nightly Intel Pipeline - Main Entry Point
Local execution script for intelligence gathering and briefing generation
"""

import argparse
import sys
from pathlib import Path

from utils.logging_setup import setup_logging

from pipeline import run_pipeline


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Nightly Intel Pipeline - ATP 5-19 Compliant Intelligence Gathering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (configured topics, 7 days back)
  python main.py

  # Run with specific topics
  python main.py --topics mlops kubernetes ai-orchestration

  # Run with custom date range
  python main.py --days-back 14

  # Download PDFs from arXiv (increases run time)
  python main.py --download-pdfs

  # Combine options
  python main.py --topics llm mlops --days-back 30 --download-pdfs

Environment Variables Required:
  GITHUB_TOKEN        - GitHub personal access token
  ANTHROPIC_API_KEY   - Anthropic API key for Claude
        """,
    )

    parser.add_argument(
        "--topics",
        nargs="+",
        help="GitHub topics to search for (overrides config)",
    )

    parser.add_argument(
        "--days-back",
        type=int,
        help="Number of days to look back for papers/repos (default: 7)",
    )

    parser.add_argument(
        "--download-pdfs",
        action="store_true",
        help="Download PDF files from arXiv (slower, uses more storage)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Verify environment variables
    import os

    if not os.getenv("GITHUB_TOKEN"):
        print("ERROR: GITHUB_TOKEN environment variable not set.", file=sys.stderr)
        print("Create a GitHub personal access token and set it:", file=sys.stderr)
        print("  export GITHUB_TOKEN='your_token_here'", file=sys.stderr)
        sys.exit(1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        print("Get your API key from https://console.anthropic.com/", file=sys.stderr)
        print("  export ANTHROPIC_API_KEY='your_key_here'", file=sys.stderr)
        sys.exit(1)

    # Run pipeline
    print("=" * 80)
    print("NIGHTLY INTEL PIPELINE - EXECUTION STARTED")
    print("=" * 80)
    print()

    try:
        briefing_file = run_pipeline(
            github_topics=args.topics,
            arxiv_days_back=args.days_back,
            download_pdfs=args.download_pdfs,
        )

        print()
        print("=" * 80)
        print("PIPELINE EXECUTION COMPLETE")
        print("=" * 80)
        print()
        print(f"Briefing generated: {briefing_file}")
        print()
        print("Next steps:")
        print(f"  1. Review the briefing: cat {briefing_file}")
        print(
            f"  2. Check the database: sqlite3 {Path(__file__).parent / 'storage' / 'intel_pipeline.db'}",
        )
        print(f"  3. Examine flattened repos: ls {Path(__file__).parent / 'data' / 'repos'}")
        print(f"  4. Review paper metadata: ls {Path(__file__).parent / 'data' / 'papers'}")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("PIPELINE EXECUTION FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e!s}")
        print()
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
