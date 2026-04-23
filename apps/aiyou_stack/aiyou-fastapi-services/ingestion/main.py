"""PNKLN Core Stack - Gemini Ingestion Layer Entry Point

Main entry point for running the ingestion pipeline.
Can be run as a standalone script or deployed as a GKE CronJob.

Usage:
    python -m ingestion.main [--queries "AI,ML"] [--since "2025-11-14T00:00:00Z"]
"""

import asyncio
import sys
from argparse import ArgumentParser
from datetime import datetime

import structlog

# NOTE: Environment variables loaded via `source scripts/load_mcp_secrets.sh`
# or GCP Secret Manager in production. python-dotenv is banned (GEMINI.md §secrets).

from ingestion.core.config import get_config
from ingestion.core.pipeline import IngestionPipeline
from ingestion.delivery.briefing import AMBriefingGenerator


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


logger = structlog.get_logger(__name__)


async def main(queries: list[str] | None = None, since: datetime | None = None) -> int:
    """Run the ingestion pipeline.

    Args:
        queries: Search queries/topics
        since: Only ingest items newer than this timestamp

    Returns:
        Exit code (0 = success, 1 = failure)

    """
    config = get_config()

    # Validate configuration
    missing_keys = config.validate_api_keys()
    if missing_keys:
        logger.error("missing_api_keys", keys=missing_keys)
        return 1

    logger.info(
        "ingestion_starting",
        queries=queries,
        since=since,
        max_items=config.ingestion.max_items_per_run,
        cost_budget=config.ingestion.cost_budget_usd,
    )

    pipeline = None
    briefing_generator = None

    try:
        # Initialize pipeline
        pipeline = IngestionPipeline()

        # Run pipeline
        summary = await pipeline.run(queries=queries, since=since)

        # Check if within budget and runtime limits
        if summary["costs"]["over_budget"]:
            logger.warning(
                "cost_budget_exceeded",
                actual=summary["costs"]["total_usd"],
                budget=config.ingestion.cost_budget_usd,
            )

        if not summary["within_runtime_limit"]:
            logger.warning(
                "runtime_limit_exceeded",
                actual_minutes=summary["runtime_minutes"],
                limit_minutes=config.ingestion.runtime_limit_minutes,
            )

        # Generate AM briefing if enabled
        if config.delivery.recipient_list:
            logger.info("generating_am_briefing")

            briefing_generator = AMBriefingGenerator()
            briefing = await briefing_generator.generate(summary)
            await briefing_generator.deliver(briefing)

        logger.info("ingestion_completed_successfully", summary=summary)

        return 0

    except KeyboardInterrupt:
        logger.info("ingestion_interrupted_by_user")
        return 130

    except Exception as e:
        logger.error("ingestion_failed", error=str(e), exc_info=True)
        return 1

    finally:
        # Cleanup
        if pipeline:
            await pipeline.close()

        if briefing_generator:
            await briefing_generator.close()


def parse_args():
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="PNKLN Gemini Ingestion Layer - Intelligence collection pipeline",
    )

    parser.add_argument(
        "--queries",
        type=str,
        help="Comma-separated search queries (e.g., 'AI,machine learning,tech news')",
    )

    parser.add_argument(
        "--since",
        type=str,
        help="ISO timestamp - only ingest items newer than this (e.g., '2025-11-14T00:00:00Z')",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and credentials without running pipeline",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Parse queries
    queries = None
    if args.queries:
        queries = [q.strip() for q in args.queries.split(",")]

    # Parse since timestamp
    since = None
    if args.since:
        try:
            since = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
        except ValueError:
            logger.error("invalid_since_timestamp", value=args.since)
            sys.exit(1)

    # Dry run mode
    if args.dry_run:
        config = get_config()
        missing = config.validate_api_keys()

        if missing:
            logger.error("dry_run_failed_missing_keys", keys=missing)
            sys.exit(1)
        else:
            logger.info("dry_run_success_all_keys_present")
            sys.exit(0)

    # Run pipeline
    exit_code = asyncio.run(main(queries=queries, since=since))
    sys.exit(exit_code)
