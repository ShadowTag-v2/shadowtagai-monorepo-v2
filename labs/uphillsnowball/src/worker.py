# labs/uphillsnowball/src/worker.py
"""Temporal Worker — Entry point for durable execution (Items 14, 15).

Registers all workflows and activities with the Temporal server
and starts the worker loop. Includes a health check HTTP endpoint.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from temporalio.client import Client
from temporalio.worker import Worker

from src.activities import (
  j1_shadowtag_dct_embed,
  j2_shaping_ops_recon,
  j39_splinter_information_ops,
  j3_decisive_ops_strike,
  j3_n_autoresearch_execute,
  j3_roc_drill_prepare,
  j4_logistics_repair,
  j5_draft_opord_and_backbrief,
  j5_mdmp_plan,
  j6_sustaining_ops_audit,
  j9_assess_and_syndicate,
  notify_commander_pwa,
)
from src.activities.j3_roc_drill import j3_roc_drill_sandbox
from src.workflows.fm3_0_temporal_mdo import MultiDomainTheaterCampaign

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("pnkln-worker")

TEMPORAL_ADDR = os.getenv("TEMPORAL_ADDR", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TASK_QUEUE", "pnkln-theater-campaign")
HEALTH_PORT = int(os.getenv("HEALTH_PORT", "8080"))

# ── Health state ──────────────────────────────────────────────
_healthy = False


async def healthz(request: web.Request) -> web.Response:
  """Health check endpoint (Item 20)."""
  if _healthy:
    return web.json_response(
      {"status": "healthy", "worker": "pnkln-temporal", "queue": TASK_QUEUE},
      status=200,
    )
  return web.json_response({"status": "starting"}, status=503)


async def readyz(request: web.Request) -> web.Response:
  """Readiness probe — confirms worker is accepting tasks."""
  if _healthy:
    return web.json_response({"ready": True}, status=200)
  return web.json_response({"ready": False}, status=503)


async def run_health_server() -> None:
  """Start the HTTP health check server."""
  app = web.Application()
  app.router.add_get("/healthz", healthz)
  app.router.add_get("/readyz", readyz)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", HEALTH_PORT)
  await site.start()
  logger.info("🏥 Health server listening on port %d", HEALTH_PORT)


async def main() -> None:
  """Connect to Temporal and start the worker."""
  global _healthy

  logger.info(
    "🚀 Starting pnkln Temporal worker — addr=%s ns=%s queue=%s",
    TEMPORAL_ADDR,
    TEMPORAL_NAMESPACE,
    TASK_QUEUE,
  )

  # Start health server first
  await run_health_server()

  # Connect to Temporal
  client = await Client.connect(
    TEMPORAL_ADDR,
    namespace=TEMPORAL_NAMESPACE,
  )

  # All activities registered with the worker
  activities = [
    j5_draft_opord_and_backbrief,
    j5_mdmp_plan,
    j2_shaping_ops_recon,
    j3_decisive_ops_strike,
    j3_roc_drill_prepare,
    j3_roc_drill_sandbox,
    j3_n_autoresearch_execute,
    j4_logistics_repair,
    j6_sustaining_ops_audit,
    j1_shadowtag_dct_embed,
    j9_assess_and_syndicate,
    j39_splinter_information_ops,
    notify_commander_pwa,
  ]

  worker = Worker(
    client,
    task_queue=TASK_QUEUE,
    workflows=[MultiDomainTheaterCampaign],
    activities=activities,
    activity_executor=ThreadPoolExecutor(max_workers=10),
  )

  # Signal the health endpoint
  _healthy = True
  logger.info("✅ Worker registered and healthy. Polling task queue: %s", TASK_QUEUE)

  # Graceful shutdown
  shutdown_event = asyncio.Event()

  def _handle_signal(sig: int, frame) -> None:
    logger.info("🛑 Received signal %s. Shutting down gracefully...", sig)
    shutdown_event.set()

  signal.signal(signal.SIGINT, _handle_signal)
  signal.signal(signal.SIGTERM, _handle_signal)

  # Run worker until shutdown
  async with worker:
    await shutdown_event.wait()

  logger.info("👋 Worker shutdown complete.")


if __name__ == "__main__":
  asyncio.run(main())
