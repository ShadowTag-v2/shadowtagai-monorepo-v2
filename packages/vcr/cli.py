"""CLI entrypoint enhancements for VCR replay flag."""

import argparse


def add_vcr_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add VCR-specific arguments to the argument parser.

    Args:
        parser (argparse.ArgumentParser): The parser to modify.
    """
    parser.add_argument("--replay", action="store_true", help="Enable VCR replay mode for local testing to avoid live model calls.")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Antigravity Agent CLI")
    add_vcr_arguments(parser)
    # Add other agent arguments here...
    return parser.parse_args()
