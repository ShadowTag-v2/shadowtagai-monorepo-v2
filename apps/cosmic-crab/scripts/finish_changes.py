#!/usr/bin/env python
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import argparse
import logging
import subprocess
import sys

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("FinishChanges")


def run_command(command, dry_run=False):
    """Runs a command and logs its output."""
    logger.info(f"Running command: {' '.join(command)}")
    if dry_run:
        logger.info("[DRY RUN] Command not executed.")
        return True
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(
            f"Command not found: {command[0]}. Please ensure it is installed and in your PATH.",
        )
        return False


def main():
    """Main function to run the finish changes cycle.
    Lint -> Format -> Stage -> Commit
    """
    parser = argparse.ArgumentParser(description="Finish changes cycle.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands instead of executing them.",
    )
    args = parser.parse_args()

    logger.info("Starting the finish changes cycle...")
    if args.dry_run:
        logger.info("[DRY RUN] Running in dry-run mode. No changes will be made.")

    # Linting
    if not run_command(["ruff", "check", "--fix", "."], dry_run=args.dry_run):
        logger.error("Linting with ruff failed. Aborting.")
        sys.exit(1)

    if not run_command(["oxlint"], dry_run=args.dry_run):
        logger.error("Linting with oxlint failed. Aborting.")
        sys.exit(1)

    if not run_command(["npx", "markdownlint-cli2", "**/*.md"], dry_run=args.dry_run):
        logger.error("Linting with markdownlint-cli2 failed. Aborting.")
        sys.exit(1)

    # Formatting
    if not run_command(["ruff", "format", "."], dry_run=args.dry_run):
        logger.error("Formatting with ruff failed. Aborting.")
        sys.exit(1)

    if not run_command(["dprint", "fmt"], dry_run=args.dry_run):
        logger.error("Formatting with dprint failed. Aborting.")
        sys.exit(1)

    if not run_command(["biome", "format", "--write", "."], dry_run=args.dry_run):
        logger.error("Formatting with biome failed. Aborting.")
        sys.exit(1)

    # Staging
    if not run_command(["git", "add", "."], dry_run=args.dry_run):
        logger.error("Staging changes failed. Aborting.")
        sys.exit(1)

    # Committing
    # Check if there are any changes to commit
    if args.dry_run:
        logger.info("[DRY RUN] Skipping git status check and commit.")
        return

    status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_result.stdout:
        logger.info("No changes to commit. Workspace is clean.")
    elif not run_command(["git", "commit", "-m", "chore: finish changes"]):
        logger.error("Committing changes failed. Aborting.")
        sys.exit(1)

    logger.info("Finish changes cycle completed successfully.")


if __name__ == "__main__":
    main()
