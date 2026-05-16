# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Main ingestion pipeline orchestrator."""

import asyncio
import logging
from datetime import datetime

from src.collectors import (
  NewsAPICollector,
  RSSCollector,
  TwitterCollector,
  YouTubeCollector,
)
from src.gates import QualityGateChecker
from src.models import IngestedItem
from src.monitoring import APICallCost, CostTracker, MetricsCollector

logging.basicConfig(
  level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
  """
  Main pipeline orchestrator for Gemini Ingestion Layer.

  Runtime target: ≤45 minutes/night
  Hard timeout: 60 minutes

  """

  TARGET_RUNTIME_MINUTES = 45
  HARD_TIMEOUT_MINUTES = 60
  PER_SOURCE_TIMEOUT_SECONDS = 300  # 5 minutes

  def __init__(self):
    """Initialize pipeline."""
    self.collectors = [
      YouTubeCollector(),
      TwitterCollector(),
      NewsAPICollector(),
      RSSCollector(),
    ]
    self.cost_tracker = CostTracker()
    self.metrics = MetricsCollector()
    self.quality_gates = QualityGateChecker()
    self.all_items: list[IngestedItem] = []

  async def collect_from_source(
    self, collector
  ) -> tuple[str, list[IngestedItem], list[str]]:
    """
    Collect from a single source with timeout.

    Args:
        collector: Source collector instance

    Returns:
        Tuple of (source_name, items, errors)

    """
    source_name = collector.source_name

    try:
      # Check health first
      if not await collector.check_health():
        logger.warning(f"Health check failed for {source_name}")
        return (source_name, [], ["Health check failed"])

      # Collect with per-source timeout
      items = await asyncio.wait_for(
        collector.collect_with_retry(), timeout=self.PER_SOURCE_TIMEOUT_SECONDS
      )

      logger.info(
        f"✅ Collected {len(items)} items from {source_name}",
        extra={"source": source_name, "items": len(items)},
      )

      # Track costs
      for item in items:
        if item.cost > 0:
          cost = APICallCost(
            timestamp=datetime.now(),
            source=source_name,
            endpoint="/collect",
            method="GET",
            cost=item.cost,
            items_returned=1,
          )
          self.cost_tracker.add_cost(cost)

      return (source_name, items, collector._errors)

    except TimeoutError:
      logger.error(f"⏱️ Timeout collecting from {source_name}")
      return (source_name, [], [f"Timeout after {self.PER_SOURCE_TIMEOUT_SECONDS}s"])
    except Exception as e:
      logger.error(f"❌ Error collecting from {source_name}: {e}")
      return (source_name, [], [str(e)])

  async def run_collection(self) -> list[IngestedItem]:
    """
    Run collection from all sources in parallel.

    Returns:
        List of all collected items

    """
    logger.info("🚀 Starting collection from all sources")

    # Run all collectors in parallel
    tasks = [self.collect_from_source(collector) for collector in self.collectors]
    results = await asyncio.gather(*tasks)

    # Aggregate results
    all_items = []
    for source_name, items, errors in results:
      all_items.extend(items)
      self.metrics.record_items(source_name, items)
      if errors:
        self.metrics.record_errors(source_name, errors)

    logger.info(f"📊 Collection complete: {len(all_items)} total items")
    return all_items

  async def run(self) -> dict:
    """
    Run the complete ingestion pipeline.

    Returns:
        Pipeline run summary

    """
    logger.info("=" * 80)
    logger.info("🌟 Gemini Ingestion Layer - Pipeline Starting")
    logger.info("=" * 80)

    # Start metrics tracking
    self.metrics.start_run()
    start_time = datetime.now()

    try:
      # Phase 1: Collection (target: 30 minutes)
      logger.info("\n📥 Phase 1: Source Collection")
      self.all_items = await self.run_collection()

      # Phase 2: Quality Gates (target: 5 minutes)
      logger.info("\n🚦 Phase 2: Quality Gates")
      gate_results = self.quality_gates.check_all(self.all_items)
      gate_summary = self.quality_gates.get_summary()

      logger.info(f"Quality Gates: {gate_summary['overall_status'].upper()}")
      for result in gate_results:
        logger.info(f"  {result.message}")

      # Phase 3: Cost Analysis
      logger.info("\n💰 Phase 3: Cost Analysis")
      budget_status = self.cost_tracker.check_budget_status()
      logger.info(f"Budget Status: {budget_status['overall_status'].upper()}")
      for alert in budget_status["alerts"]:
        logger.log(
          logging.CRITICAL if alert["level"] == "critical" else logging.WARNING,
          f"  {alert['message']}",
        )

      # End metrics tracking
      self.metrics.end_run()
      end_time = datetime.now()
      runtime_minutes = (end_time - start_time).total_seconds() / 60

      # Pipeline summary
      summary = {
        "status": "completed",
        "runtime_minutes": round(runtime_minutes, 2),
        "target_runtime": self.TARGET_RUNTIME_MINUTES,
        "under_target": runtime_minutes <= self.TARGET_RUNTIME_MINUTES,
        "metrics": self.metrics.get_summary(),
        "quality_gates": gate_summary,
        "budget_status": budget_status,
        "timestamp": datetime.now().isoformat(),
      }

      logger.info("\n" + "=" * 80)
      logger.info(f"✨ Pipeline Complete in {runtime_minutes:.1f} minutes")
      logger.info(
        f"   Target: {self.TARGET_RUNTIME_MINUTES} min | Status: {'✅ ON TARGET' if summary['under_target'] else '⚠️ OVER TARGET'}"
      )
      logger.info("=" * 80)

      return summary

    except Exception as e:
      logger.exception(f"❌ Pipeline failed: {e}")
      self.metrics.end_run()
      return {
        "status": "failed",
        "error": str(e),
        "metrics": self.metrics.get_summary() if self.metrics.current_run else {},
      }


async def main():
  """Main entry point for pipeline."""
  pipeline = IngestionPipeline()
  summary = await pipeline.run()

  # Print final summary
  if summary["status"] == "completed":
    pass


if __name__ == "__main__":
  asyncio.run(main())
