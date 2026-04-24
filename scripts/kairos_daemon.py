#!/usr/bin/env python3
"""KAIROS Daemon — Background Autonomous Agent Controller.

Runs in continuous mode, executing scheduled maintenance tasks:
  1. Dream Consolidation (nightly) — KI maintenance
  2. Dead code audit (daily)  — ruff F401/F841 sweep (V22 Pruned — vulture removed)
  3. Health check (every 5 min) — GCP auth, dylib presence, LanceDB integrity
  4. Loop Steward handoff (on-demand) — autonomous task continuation

Usage:
    python scripts/kairos_daemon.py               # foreground
    python scripts/kairos_daemon.py --daemon       # background (nohup)
    python scripts/kairos_daemon.py --once         # single cycle then exit
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import pathlib
import random
import signal
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [KAIROS] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("kairos")

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
BEADS_DIR = REPO_ROOT / ".beads"
HEARTBEAT_FILE = BEADS_DIR / "kairos_heartbeat.json"

VAULT_DIR = REPO_ROOT / "vault"

# Task intervals (seconds)
HEALTH_CHECK_INTERVAL = 300  # 5 minutes
DREAM_INTERVAL = 86400  # 24 hours
DEAD_CODE_INTERVAL = 86400  # 24 hours
LOOP_STEWARD_INTERVAL = 300  # 5 minutes
STANDUP_INTERVAL = 86400  # 24 hours
VAULT_INGEST_INTERVAL = 300  # 5 minutes
QUARANTINE_PURGE_INTERVAL = 3600  # 1 hour
AUTOLINT_INTERVAL = 86400  # 24 hours

# Jitter range (±30s) to prevent thundering herd — TACSOP B8
JITTER_SECONDS = 30


def _jittered(interval: float) -> float:
    """Add ±JITTER_SECONDS random offset to an interval."""
    return interval + random.uniform(-JITTER_SECONDS, JITTER_SECONDS)


_running = True


def _signal_handler(sig: int, _frame: object) -> None:
    global _running
    logger.info("Received signal %d, shutting down gracefully...", sig)
    _running = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ---------------------------------------------------------------------------
# Task implementations
# ---------------------------------------------------------------------------


def health_check() -> dict:
    """Run system health checks. Returns status dict."""
    checks: dict[str, str] = {}

    # 1. GCP ADC
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        checks["gcp_adc"] = "ok" if result.returncode == 0 else "expired"
    except subprocess.TimeoutExpired, FileNotFoundError:
        checks["gcp_adc"] = "missing"

    # 2. ANE dylib
    dylib = REPO_ROOT / "third_party" / "ANE" / "bridge" / "libane_bridge.dylib"
    checks["ane_dylib"] = "ok" if dylib.exists() else "missing"

    # 3. LanceDB data
    lancedb_dir = REPO_ROOT / "data" / "lancedb"
    checks["lancedb"] = "ok" if lancedb_dir.exists() and any(lancedb_dir.iterdir()) else "empty"

    # 4. Vault directory
    vault_ingest = VAULT_DIR / "ingest"
    checks["vault"] = "ok" if vault_ingest.exists() else "missing"

    # 5. Git status clean
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(REPO_ROOT),
        )
        dirty_count = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        checks["git_dirty"] = f"{dirty_count} files" if dirty_count > 0 else "clean"
    except subprocess.TimeoutExpired, FileNotFoundError:
        checks["git_dirty"] = "unknown"

    # 6. Git fetch --prune (GitHub-first context: keep remote refs fresh)
    try:
        fetch_result = subprocess.run(
            ["git", "fetch", "--prune", "origin"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        checks["git_fetch"] = "ok" if fetch_result.returncode == 0 else "failed"
    except subprocess.TimeoutExpired, FileNotFoundError:
        checks["git_fetch"] = "timeout"

    logger.info("Health: %s", json.dumps(checks))
    return checks


def run_dream_consolidation() -> bool:
    """Execute dream_consolidation.py if it exists."""
    script = SCRIPTS_DIR / "dream_consolidation.py"
    if not script.exists():
        logger.warning("dream_consolidation.py not found, skipping")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            logger.info("Dream consolidation completed successfully")
            return True
        logger.error("Dream consolidation failed: %s", result.stderr[:500])
        return False
    except subprocess.TimeoutExpired:
        logger.exception("Dream consolidation timed out (300s)")
        return False


def run_dead_code_audit() -> bool:
    """Execute dead-code-audit.sh."""
    script = SCRIPTS_DIR / "dead-code-audit.sh"
    if not script.exists():
        logger.warning("dead-code-audit.sh not found, skipping")
        return False
    try:
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            logger.info("Dead code audit completed")
            return True
        logger.warning("Dead code audit found issues: %s", result.stdout[-500:])
        return True  # Still "succeeded" even if violations found
    except subprocess.TimeoutExpired:
        logger.exception("Dead code audit timed out (120s)")
        return False


def run_loop_steward() -> bool:
    """Execute loop_steward.py single cycle if it exists."""
    script = SCRIPTS_DIR / "loop_steward.py"
    if not script.exists():
        logger.warning("loop_steward.py not found, skipping")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--once"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        logger.info("Loop steward cycle: exit=%d", result.returncode)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.exception("Loop steward timed out (60s)")
        return False


def run_standup_report() -> bool:
    """Generate and post standup report via gws CLI."""
    gws_cmd = "gws"
    try:
        result = subprocess.run(
            [gws_cmd, "workflow", "+standup-report"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
            env={**os.environ, "PATH": f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"},
        )
        if result.returncode == 0:
            logger.info("Standup report posted successfully")
            return True
        logger.warning("Standup report failed: %s", result.stderr[:300])
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning("Standup report skipped: %s", e)
        return False


def run_vault_ingest() -> bool:
    """Process new files in vault/ingest/ via zero-trust pipeline."""
    script = SCRIPTS_DIR / "vault" / "zero_trust_pipeline.py"
    ingest_dir = VAULT_DIR / "ingest"
    if not script.exists():
        logger.warning("zero_trust_pipeline.py not found, skipping vault ingest")
        return False
    if not ingest_dir.exists():
        return True  # Nothing to do
    files = [f for f in ingest_dir.iterdir() if f.is_file() and f.name != ".gitkeep"]
    if not files:
        return True  # Nothing to do
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--scan-dir", str(ingest_dir)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO_ROOT),
        )
        logger.info("Vault ingest: %d files, exit=%d", len(files), result.returncode)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.exception("Vault ingest timed out (120s)")
        return False


def run_quarantine_purge() -> bool:
    """Delete quarantine files older than 24 hours."""
    quarantine_dir = VAULT_DIR / "quarantine"
    if not quarantine_dir.exists():
        return True
    import time as _time

    now = _time.time()
    purged = 0
    for path in quarantine_dir.iterdir():
        if path.is_file() and path.name != ".gitkeep":
            age_hours = (now - path.stat().st_mtime) / 3600
            if age_hours > 24:
                path.unlink()
                purged += 1
    if purged > 0:
        logger.info("Quarantine purge: removed %d stale file(s)", purged)
    return True


def run_omni_autolint() -> bool:
    """Execute gca_autolint_daemon.py in headless dry-run + JSON mode."""
    script = SCRIPTS_DIR / "gca_autolint_daemon.py"
    if not script.exists():
        logger.warning("gca_autolint_daemon.py not found, skipping")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--dry-run", "--json"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            logger.info("Omni-Autolint completed successfully")
            return True
        logger.error("Omni-Autolint failed: %s", result.stderr[:500])
        return False
    except subprocess.TimeoutExpired:
        logger.exception("Omni-Autolint timed out (600s)")
        return False


def write_heartbeat(status: dict) -> None:
    """Write heartbeat file for monitoring."""
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    heartbeat = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),  # noqa: UP017
        "pid": os.getpid(),
        "status": status,
    }
    HEARTBEAT_FILE.write_text(json.dumps(heartbeat, indent=2))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main_loop(once: bool = False) -> None:
    """KAIROS main execution loop."""
    logger.info("KAIROS daemon starting (PID %d)", os.getpid())
    logger.info("Repo root: %s", REPO_ROOT)

    last_health = 0.0
    last_dream = 0.0
    last_dead_code = 0.0
    last_steward = 0.0
    last_standup = 0.0
    last_vault_ingest = 0.0
    last_quarantine_purge = 0.0
    last_autolint = 0.0

    cycle = 0
    while _running:
        cycle += 1
        now = time.time()
        status: dict[str, str] = {"cycle": str(cycle)}

        # Health check (every 5 min, jittered)
        if now - last_health >= _jittered(HEALTH_CHECK_INTERVAL):
            status["health"] = json.dumps(health_check())
            last_health = now

        # Dream consolidation (daily, only between 2-4 AM local)
        hour = datetime.datetime.now().hour
        if now - last_dream >= _jittered(DREAM_INTERVAL) and 2 <= hour <= 4:
            run_dream_consolidation()
            last_dream = now
            status["dream"] = "ran"

        # Dead code audit (daily, during off-hours)
        if now - last_dead_code >= _jittered(DEAD_CODE_INTERVAL) and 1 <= hour <= 5:
            run_dead_code_audit()
            last_dead_code = now
            status["dead_code"] = "ran"

        # Loop steward (every 5 min)
        if now - last_steward >= _jittered(LOOP_STEWARD_INTERVAL):
            run_loop_steward()
            last_steward = now
            status["steward"] = "ran"

        # Standup report (daily, at 8 AM local)
        if now - last_standup >= _jittered(STANDUP_INTERVAL) and hour == 8:
            run_standup_report()
            last_standup = now
            status["standup"] = "ran"

        # Vault ingest sweep (every 5 min)
        if now - last_vault_ingest >= _jittered(VAULT_INGEST_INTERVAL):
            run_vault_ingest()
            last_vault_ingest = now
            status["vault_ingest"] = "ran"

        # Quarantine purge (every hour)
        if now - last_quarantine_purge >= _jittered(QUARANTINE_PURGE_INTERVAL):
            run_quarantine_purge()
            last_quarantine_purge = now
            status["quarantine_purge"] = "ran"

        # Omni-Autolint (daily, during off-hours 3-5 AM)
        if now - last_autolint >= _jittered(AUTOLINT_INTERVAL) and 3 <= hour <= 5:
            run_omni_autolint()
            last_autolint = now
            status["autolint"] = "ran"

        write_heartbeat(status)

        if once:
            logger.info("Single cycle complete, exiting")
            break

        # Sleep 30s between cycles
        for _ in range(30):
            if not _running:
                break
            time.sleep(1)

    logger.info("KAIROS daemon stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description="KAIROS Background Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as background process")
    parser.add_argument("--once", action="store_true", help="Single cycle then exit")
    args = parser.parse_args()

    if args.daemon:
        pid = os.fork()
        if pid > 0:
            logger.info("KAIROS daemon forked (PID %d)", pid)
            sys.exit(0)
        os.setsid()
        main_loop(once=False)
    else:
        main_loop(once=args.once)


if __name__ == "__main__":
    main()
