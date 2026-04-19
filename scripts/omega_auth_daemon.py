#!/usr/bin/env python3
"""Omega Auth Daemon — Background token refresh for the Kovel Enclave.

Refreshes GCP Application Default Credentials every 3 minutes
to prevent detoken during long coding sessions.

Referenced by: .agent/workflows/live-engine.md

Usage:
    nohup python3 scripts/omega_auth_daemon.py > logs/omega_daemon.log 2>&1 &
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REFRESH_INTERVAL_SECONDS = 180  # 3 minutes
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [OMEGA] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("omega_auth_daemon")

_running = True


def _handle_shutdown(signum, _frame):
    global _running
    logger.info("Received signal %d — shutting down gracefully", signum)
    _running = False


def _refresh_adc() -> bool:
    """Refresh Application Default Credentials via gcloud."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            token_preview = result.stdout.strip()[:12] + "..."
            logger.info("ADC token refreshed: %s", token_preview)
            return True
        else:
            logger.warning("ADC refresh failed: %s", result.stderr.strip()[:200])
            return False
    except subprocess.TimeoutExpired:
        logger.error("ADC refresh timed out (30s)")
        return False
    except FileNotFoundError:
        logger.error("gcloud CLI not found in PATH")
        return False


def _check_compute_sa() -> bool:
    """Verify the compute service account is accessible."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        accounts = [a.strip() for a in result.stdout.strip().split("\n") if a.strip()]
        if accounts:
            logger.info("Active accounts: %s", ", ".join(accounts[:3]))
            return True
        logger.warning("No active gcloud accounts")
        return False
    except Exception as e:
        logger.error("Account check failed: %s", e)
        return False


def main():
    """Main daemon loop — refresh ADC every REFRESH_INTERVAL_SECONDS."""
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 50)
    logger.info("Omega Auth Daemon starting")
    logger.info("Project: %s", os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4"))
    logger.info("Refresh interval: %ds", REFRESH_INTERVAL_SECONDS)
    logger.info("PID: %d", os.getpid())
    logger.info("=" * 50)

    # Initial check
    _check_compute_sa()

    cycle = 0
    while _running:
        cycle += 1
        logger.info("Cycle %d — refreshing ADC", cycle)
        ok = _refresh_adc()

        if not ok and cycle > 1:
            logger.warning("ADC refresh failed on cycle %d — will retry", cycle)

        # Sleep in 1-second increments to allow graceful shutdown
        for _ in range(REFRESH_INTERVAL_SECONDS):
            if not _running:
                break
            time.sleep(1)

    logger.info("Omega Auth Daemon stopped after %d cycles", cycle)


if __name__ == "__main__":
    main()
