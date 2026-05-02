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
import asyncio
import datetime
import json
import logging
import os
import pathlib
import random
import re
import signal
import subprocess
import sys
import time
from typing import Any
import contextlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [KAIROS] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("kairos")

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_SUGGESTION_WORDS = 12  # Matches speculation_engine.suggestion.MAX_SUGGESTION_WORDS
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Bootstrap monorepo packages for deferred imports (speculation_engine, etc.)
# REPO_ROOT must be on sys.path FIRST so that `from packages.X` absolute
# imports used inside packages/ (e.g. prompt_assembler → packages.prompt_sections)
# resolve correctly. Then packages/ so direct `import prompt_assembler` works.
_repo_root_str = str(REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
_packages_dir = str(REPO_ROOT / "packages")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)
BEADS_DIR = REPO_ROOT / ".beads"
HEARTBEAT_FILE = BEADS_DIR / "kairos_heartbeat.json"

VAULT_DIR = REPO_ROOT / "vault"

# Task intervals (seconds)
HEALTH_CHECK_INTERVAL = 300  # 5 minutes
DREAM_INTERVAL = 86400  # 24 hours
DISK_SKILL_DREAM_INTERVAL = 604800  # 7 days (weekly deep scan)
DEAD_CODE_INTERVAL = 86400  # 24 hours
LOOP_STEWARD_INTERVAL = 300  # 5 minutes
STANDUP_INTERVAL = 86400  # 24 hours
VAULT_INGEST_INTERVAL = 300  # 5 minutes
QUARANTINE_PURGE_INTERVAL = 3600  # 1 hour
AUTOLINT_INTERVAL = 86400  # 24 hours
OOB_REPORT_CHECK_INTERVAL = 600  # 10 minutes
PROMPT_VALIDATION_INTERVAL = 3600  # 1 hour — periodic prompt assembly check
PROACTIVE_SUGGESTION_INTERVAL = 900  # 15 min — speculation prefetch cycle

# Disk-Skill Dream resource limits
DISK_SKILL_AST_TIMEOUT = 900  # 15-minute cap for deep AST scans
DISK_SKILL_MAX_FILES = 5000  # Cap file count for ast-grep sweeps

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
# Secret resolution (GCP Secret Manager → os.environ)
# ---------------------------------------------------------------------------


def _resolve_gemini_api_key() -> str | None:
    """Resolve GEMINI_API_KEY from env or GCP Secret Manager.

    Priority chain:
      1. os.environ["GEMINI_API_KEY"]    — already set (interactive shells)
      2. gcloud secrets access            — launchd / daemon mode
      3. None                             — fails gracefully, logged

    Per secrets_manager_doctrine: no hardcoded keys. Secret Manager is the
    sole credential source for daemonized execution.
    """
    existing = os.environ.get("GEMINI_API_KEY")
    if existing:
        return existing

    project = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
    try:
        result = subprocess.run(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                "latest",
                "--secret=gemini-api-key",
                f"--project={project}",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            api_key = result.stdout.strip()
            os.environ["GEMINI_API_KEY"] = api_key
            logger.info("GEMINI_API_KEY resolved from GCP Secret Manager")
            return api_key
        logger.warning(
            "Secret Manager returned rc=%d: %s",
            result.returncode,
            result.stderr.strip()[:200],
        )
    except FileNotFoundError:
        logger.warning("gcloud CLI not found — cannot resolve GEMINI_API_KEY")
    except subprocess.TimeoutExpired:
        logger.warning("Secret Manager access timed out (15s)")
    except Exception as e:
        logger.warning("Failed to resolve GEMINI_API_KEY from Secret Manager: %s", e)

    return None


# ---------------------------------------------------------------------------
# Task implementations
# ---------------------------------------------------------------------------


def _init_sleep_guard() -> None:
    """Start hardware sleep prevention via caffeinate (macOS only)."""
    try:
        from prevent_sleep import start_prevent_sleep, is_preventing_sleep

        start_prevent_sleep()
        if is_preventing_sleep():
            logger.info("Sleep prevention: ACTIVE (caffeinate engaged)")
        else:
            logger.info("Sleep prevention: skipped (non-Darwin or caffeinate unavailable)")
    except ImportError:
        logger.warning("prevent_sleep package not available")


def _shutdown_sleep_guard() -> None:
    """Release the sleep prevention assertion."""
    try:
        from prevent_sleep import stop_prevent_sleep

        stop_prevent_sleep()
        logger.info("Sleep prevention: released")
    except ImportError:
        pass


def _validate_prompt_assembly() -> bool:
    """Periodically validate that the system prompt assembler works.

    Catches import errors, malformed sections, and registry failures
    early rather than at agent invocation time.
    """
    try:
        from prompt_assembler import assemble_system_prompt
        from prompt_assembler.assembler import PromptConfig

        config = PromptConfig(
            cwd=str(REPO_ROOT),
            model_id="gemini-3.1-flash-lite-preview-thinking",
        )
        sections = asyncio.run(assemble_system_prompt(config))
        if not sections:
            logger.error("Prompt assembly returned 0 sections")
            return False
        logger.info(
            "Prompt assembly: %d sections, ~%d chars",
            len(sections),
            sum(len(s) for s in sections),
        )
        return True
    except Exception as e:
        logger.error("Prompt assembly validation failed: %s", e)
        return False


def _estimate_context_budget() -> dict[str, int]:
    """Use token_estimation to report current context budget metrics."""
    try:
        from token_estimation import rough_token_estimate

        # Estimate tokens for key config files
        metrics: dict[str, int] = {}
        for name, path in [
            ("AGENTS.md", REPO_ROOT / "AGENTS.md"),
            ("GEMINI.md", REPO_ROOT / "GEMINI.md"),
            ("manifest", REPO_ROOT / "monorepo_manifest.yaml"),
        ]:
            if path.exists():
                content = path.read_text(errors="replace")
                metrics[name] = rough_token_estimate(content)
        logger.info("Token budget: %s", json.dumps(metrics))
        return metrics
    except ImportError:
        logger.warning("token_estimation package not available")
        return {}


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


def run_dream_consolidation(tier: str = "light") -> bool:
    """Execute dream_consolidation.py.

    Args:
        tier: "light" for daily interactive KI maintenance,
              "disk-skill" for deep AST extraction (weekly).
    """
    script = SCRIPTS_DIR / "dream_consolidation.py"
    if not script.exists():
        logger.warning("dream_consolidation.py not found, skipping")
        return False

    timeout = 300 if tier == "light" else DISK_SKILL_AST_TIMEOUT
    logger.info("Starting %s dream (timeout=%ds)", tier, timeout)

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            logger.info("%s dream completed successfully", tier.title())
            return True
        logger.error("%s dream failed: %s", tier.title(), result.stderr[:500])
        return False
    except subprocess.TimeoutExpired:
        logger.exception("%s dream timed out (%ds)", tier.title(), timeout)
        return False


def _load_ast_grep_rules() -> list[dict]:
    """Load ast-grep rules from externalized YAML config.

    Falls back to a minimal default if the config file is missing.
    """
    rules_path = REPO_ROOT / "config" / "ast_grep_rules.yaml"
    if not rules_path.exists():
        logger.warning("ast-grep rules file not found: %s", rules_path)
        return [{"id": "unused-def", "language": "python", "rule": {"kind": "function_definition"}}]

    try:
        # Use yaml if available, otherwise fall back to JSON-compatible subset
        try:
            import yaml  # noqa: F811

            with open(rules_path) as f:
                config = yaml.safe_load(f)
            return config.get("rules", [])
        except ImportError:
            logger.warning("PyYAML not installed, using fallback rule")
            return [{"id": "unused-def", "language": "python", "rule": {"kind": "function_definition"}}]
    except (OSError, ValueError) as e:
        logger.warning("Failed to load ast-grep rules: %s", e)
        return [{"id": "unused-def", "language": "python", "rule": {"kind": "function_definition"}}]


def run_disk_skill_dream() -> bool:
    """Execute deep AST extraction over the full repo.

    This is the heavy tier that runs weekly during off-peak hours.
    It performs:
      1. ast-grep structural analysis on all Python/TS files
      2. Full dependency graph extraction
      3. Dead symbol cross-reference against KI entries

    Unlike the light dream, this tier doesn't share compute with
    a waiting user, so it can afford expensive operations.
    """
    # Phase 1: ast-grep deep scan (if available)
    ast_grep_bin = "ast-grep"
    try:
        # Verify ast-grep is installed
        check = subprocess.run(
            [ast_grep_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if check.returncode != 0:
            logger.warning("ast-grep not available, skipping disk-skill phase 1")
            return run_dream_consolidation(tier="disk-skill")
    except FileNotFoundError, subprocess.TimeoutExpired:
        logger.warning("ast-grep binary not found")
        return run_dream_consolidation(tier="disk-skill")

    # Count files to process (cap at DISK_SKILL_MAX_FILES)
    py_files = list(REPO_ROOT.rglob("*.py"))
    ts_files = list(REPO_ROOT.rglob("*.ts"))
    tsx_files = list(REPO_ROOT.rglob("*.tsx"))
    all_files = py_files + ts_files + tsx_files

    # Filter out node_modules, .venv, etc.
    filtered = [
        f for f in all_files if not any(part in f.parts for part in ("node_modules", ".venv", "venv", "__pycache__", ".git", "dist", "build"))
    ]
    logger.info("Disk-Skill Dream: %d files to scan (capped at %d)", len(filtered), DISK_SKILL_MAX_FILES)

    # Phase 2: Load externalized rules and run ast-grep scan
    rules = _load_ast_grep_rules()
    scan_report_path = BEADS_DIR / f"disk_skill_scan_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}.json"  # noqa: UP017
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

    # Run each Python rule through ast-grep
    all_findings = []
    for rule in rules:
        if rule.get("language") != "python":
            continue
        try:
            rule_json = json.dumps(rule)
            result = subprocess.run(
                [
                    ast_grep_bin,
                    "scan",
                    "--rule",
                    rule_json,
                    "--json",
                    str(REPO_ROOT),
                ],
                capture_output=True,
                text=True,
                timeout=DISK_SKILL_AST_TIMEOUT,
                cwd=str(REPO_ROOT),
            )
            if result.stdout:
                try:
                    findings = json.loads(result.stdout)
                    all_findings.extend(findings if isinstance(findings, list) else [findings])
                except json.JSONDecodeError:
                    pass
        except subprocess.TimeoutExpired:
            logger.exception("Disk-Skill AST scan timed out for rule '%s' (%ds)", rule.get("id", "?"), DISK_SKILL_AST_TIMEOUT)
        except FileNotFoundError:
            logger.warning("ast-grep binary disappeared during scan")
            break

    if all_findings:
        scan_report_path.write_text(json.dumps(all_findings, indent=2))
        logger.info("Disk-Skill AST scan: %d findings written to %s", len(all_findings), scan_report_path)
    else:
        logger.info("Disk-Skill AST scan: no findings")

    # Phase 3: Run the standard dream with extended timeout
    return run_dream_consolidation(tier="disk-skill")


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


def check_oob_reports() -> bool:
    """Check for new OOB dream reports and log summaries.

    Monitors .beads/ for dream_report_*.md files and logs their
    key metrics. This enables KAIROS to react to dream findings
    without tight coupling to the dream daemon itself.
    """
    if not BEADS_DIR.exists():
        return True

    reports = sorted(BEADS_DIR.glob("dream_report_*.md"), reverse=True)
    if not reports:
        return True

    # Only process the latest report
    latest = reports[0]
    try:
        content = latest.read_text()
        # Extract key metrics from the markdown report
        for line in content.splitlines():
            if line.startswith("- **"):
                logger.info("OOB Dream: %s", line.strip("- "))
    except OSError:
        pass

    return True


def process_webhook_events() -> bool:
    """Process webhook-driven events from .beads/events/ queue.

    This is the stub for future SSE/Webhook relay integration.
    Events are JSON files dropped into .beads/events/ by external
    systems (e.g., GitHub App webhooks, PR notifications).

    Each event file is processed exactly once and archived.
    """
    events_dir = BEADS_DIR / "events"
    if not events_dir.exists():
        return True

    archive_dir = events_dir / "processed"
    archive_dir.mkdir(exist_ok=True)

    processed = 0
    for event_file in sorted(events_dir.glob("*.json")):
        if not event_file.is_file():
            continue
        try:
            event = json.loads(event_file.read_text())
            event_type = event.get("type", "unknown")
            logger.info("Processing event: %s (type=%s)", event_file.name, event_type)

            # Route by event type
            if event_type == "pr_review_requested":
                logger.info("PR review event: %s", event.get("pr_url", "N/A"))
            elif event_type == "deploy_complete":
                logger.info("Deploy event: %s", event.get("service", "N/A"))
            elif event_type == "secret_rotation":
                logger.info("Secret rotation event: %s", event.get("secret_name", "N/A"))
            else:
                logger.info("Unknown event type: %s", event_type)

            # Archive the processed event
            dest = archive_dir / event_file.name
            event_file.rename(dest)
            processed += 1
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to process event %s: %s", event_file.name, e)

    if processed > 0:
        logger.info("Processed %d webhook event(s)", processed)
    return True


RESEARCH_SWEEP_INTERVAL = 21600  # 6 hours


# Predefined research topics for autonomous sweeps
_RESEARCH_TOPICS = [
    "Latest Python 3.14 features and migration patterns",
    "Gemini API SDK updates and breaking changes",
    "Firebase Hosting CDN performance optimization",
    "Cloud Run cold start reduction strategies",
    "OpenTelemetry Python SDK best practices 2026",
]


def run_research_sweep() -> bool:
    """Execute an autonomous GeminiResearchSweep via the orchestrator.

    Uses the SpeculativeResearchOrchestrator to run a short
    background research sweep on the next topic in the rotation.
    Results are logged to .beads/research_sweep.jsonl.
    """
    try:
        from speculation_engine.orchestrator import (
            SpeculativeResearchOrchestrator,
            SpeculativeResearchConfig,
        )
    except ImportError:
        logger.warning("speculation_engine not importable, skipping research sweep")
        return False

    # Rotate through topics
    topic_index_file = BEADS_DIR / "research_topic_index.txt"
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        idx = int(topic_index_file.read_text().strip()) if topic_index_file.exists() else 0
    except ValueError, OSError:
        idx = 0
    topic = _RESEARCH_TOPICS[idx % len(_RESEARCH_TOPICS)]
    topic_index_file.write_text(str((idx + 1) % len(_RESEARCH_TOPICS)))

    # Rate limit check
    try:
        from speculation_engine.firestore_persistence import check_sweep_rate_limit, record_sweep_invocation

        if not check_sweep_rate_limit():
            logger.info("Research sweep rate-limited, skipping")
            return False
    except ImportError:
        pass  # No rate limiting if persistence module unavailable

    logger.info("Research sweep starting: '%s'", topic)
    start = time.time()

    try:
        orchestrator = SpeculativeResearchOrchestrator(
            workspace=str(REPO_ROOT),
            config=SpeculativeResearchConfig(
                speculate_during_research=False,
                speculate_during_synthesis=False,
                use_cow_overlay=False,
            ),
        )
        sweep = orchestrator.research_sweep
        result = sweep.run(topic, timeout=600)  # 10 min cap for KAIROS

        duration = time.time() - start
        # Log the result to .beads/ evidence trail
        log_path = BEADS_DIR / "research_sweep.jsonl"
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),  # noqa: UP017
            "topic": topic,
            "duration_seconds": round(duration, 1),
            "report_length": len(result.report_text),
            "agent": result.agent,
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Persist to Firestore (fail-open)
        try:
            from speculation_engine.firestore_persistence import persist_sweep_result

            doc_id = persist_sweep_result(
                result,
                session_id=f"kairos-{os.getpid()}-{int(start)}",
                pipeline_mode="research_sweep",
                status="completed",
            )
            if doc_id:
                logger.info("SweepResult persisted to Firestore: %s", doc_id)
        except Exception as fs_err:
            logger.debug("Firestore persistence skipped: %s", fs_err)

        # Record invocation for rate limiting
        with contextlib.suppress(Exception):
            record_sweep_invocation()

        logger.info(
            "Research sweep completed: %s (%.1fs, %d chars)",
            topic,
            duration,
            len(result.report_text),
        )
        return True
    except Exception as e:
        logger.error("Research sweep failed: %s", e)
        return False


def _run_sweep_with_topic(topic: str) -> bool:
    """Run a research sweep with a specific custom topic.

    Same infrastructure as ``run_research_sweep()`` but uses the caller's topic
    instead of rotating through ``_RESEARCH_TOPICS``.
    """
    try:
        from speculation_engine.orchestrator import (
            SpeculativeResearchOrchestrator,
            SpeculativeResearchConfig,
        )
    except ImportError:
        logger.warning("speculation_engine not importable, skipping research sweep")
        return False

    # Rate limit check
    try:
        from speculation_engine.firestore_persistence import check_sweep_rate_limit, record_sweep_invocation

        if not check_sweep_rate_limit():
            logger.info("Custom research sweep rate-limited, skipping")
            return False
    except ImportError:
        pass

    logger.info("Custom research sweep starting: '%s'", topic)
    start = time.time()

    try:
        orchestrator = SpeculativeResearchOrchestrator(
            workspace=str(REPO_ROOT),
            config=SpeculativeResearchConfig(
                speculate_during_research=False,
                speculate_during_synthesis=False,
                use_cow_overlay=False,
            ),
        )
        sweep = orchestrator.research_sweep
        result = sweep.run(topic, timeout=600)

        duration = time.time() - start
        log_path = BEADS_DIR / "research_sweep.jsonl"
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),  # noqa: UP017
            "topic": topic,
            "duration_seconds": round(duration, 1),
            "report_length": len(result.report_text),
            "agent": result.agent,
            "source": "sweep-now",
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Persist to Firestore (fail-open)
        try:
            from speculation_engine.firestore_persistence import persist_sweep_result

            doc_id = persist_sweep_result(
                result,
                session_id=f"sweep-now-{os.getpid()}-{int(start)}",
                pipeline_mode="research_sweep",
                status="completed",
            )
            if doc_id:
                logger.info("SweepResult persisted to Firestore: %s", doc_id)
        except Exception as fs_err:
            logger.debug("Firestore persistence skipped: %s", fs_err)

        # Record invocation for rate limiting
        with contextlib.suppress(Exception):
            record_sweep_invocation()

        # Print report to stdout for --sweep-now users
        print(f"\n{'=' * 72}")
        print(f"Research Sweep: {topic}")
        print(f"Duration: {duration:.1f}s | Report: {len(result.report_text)} chars")
        print(f"{'=' * 72}\n")
        print(result.report_text[:2000])
        if len(result.report_text) > 2000:
            print(f"\n... ({len(result.report_text) - 2000} chars truncated)")

        return True
    except Exception as e:
        logger.error("Custom research sweep failed: %s", e)
        return False


def _probe_bridge_health() -> dict[str, Any]:
    """Probe the speculation engine bridge for liveness.

    Returns a dict with import health, orchestrator init, sweep readiness,
    API key availability, and consumer status.
    Used by ``--bridge-health`` CLI flag and ``context_status.py --bridge-health``.
    """
    result: dict[str, Any] = {
        "healthy": False,
        "importable": False,
        "orchestrator_init": False,
        "sweep_ready": False,
        "api_key_resolved": False,
        "consumer_ready": False,
        "suggestion_cached": False,
        "error": None,
    }

    # 1) Import check
    try:
        from speculation_engine.orchestrator import (  # noqa: F401
            SpeculativeResearchOrchestrator,
            SpeculativeResearchConfig,
        )
        from speculation_engine.gemini_bridge import (  # noqa: F401
            GeminiResearchSweep,
            GeminiPairProgrammer,
            PipelineMode,
        )

        result["importable"] = True
    except ImportError as e:
        result["error"] = f"import: {e}"
        return result

    # 2) Orchestrator init
    try:
        orch = SpeculativeResearchOrchestrator(
            workspace=str(REPO_ROOT),
            config=SpeculativeResearchConfig(
                speculate_during_research=False,
                speculate_during_synthesis=False,
                use_cow_overlay=False,
            ),
        )
        result["orchestrator_init"] = True
    except Exception as e:
        result["error"] = f"orchestrator: {e}"
        return result

    # 3) Sweep accessor
    try:
        _ = orch.research_sweep  # Lazy-init the GeminiResearchSweep
        result["sweep_ready"] = True
    except Exception as e:
        result["error"] = f"sweep: {e}"
        return result

    # 4) API key resolution
    api_key = _resolve_gemini_api_key()
    result["api_key_resolved"] = bool(api_key)
    if not api_key:
        result["error"] = "GEMINI_API_KEY: not in env, Secret Manager unreachable"

    # 5) Consumer health
    try:
        from speculation_engine.consumer import SuggestionConsumer

        consumer = SuggestionConsumer()
        result["consumer_ready"] = True
        entry = consumer.get_suggestion()
        result["suggestion_cached"] = entry is not None
        if entry:
            result["suggestion_age_s"] = round(entry.age_seconds, 1)
            result["suggestion_preview"] = entry.text[:50]
    except ImportError as e:
        result["error"] = f"consumer import: {e}"

    result["healthy"] = (
        result["importable"] and result["orchestrator_init"] and result["sweep_ready"] and result["api_key_resolved"] and result["consumer_ready"]
    )
    return result


def run_proactive_suggestion_probe() -> bool:
    """Run a proactive suggestion prefetch cycle.

    Architecture (ported from Claude Code v2.1.91 promptSuggestion.ts):
      1. Load recent conversation state from the latest .beads/ evidence.
      2. Construct a daemon-mode SessionState (no interactive gates).
      3. Invoke try_generate_suggestion with a lightweight Gemini bridge callback.
      4. Cache the result in .beads/suggestion_cache.json for next session pickup.
      5. Log telemetry to .beads/speculation_telemetry.jsonl.

    Returns True if a suggestion was generated and cached, False otherwise.
    """
    try:
        from speculation_engine.suggestion import (
            SuggestionConfig,
            SessionState,
            SuggestionResult,
            try_generate_suggestion,
        )
        from speculation_engine.telemetry import log_suggestion_event
    except ImportError as e:
        logger.warning("Proactive suggestion: import failed — %s", e)
        return False

    # Build a daemon-appropriate session state:
    #   - Override interactive gate: daemon IS the proactive engine
    #   - Set assistant_turn_count high to bypass too-few-turns gate
    #   - No pending permissions, no plan mode
    state = SessionState(
        suggestion_enabled=True,
        pending_permission=False,
        elicitation_active=False,
        plan_mode=False,
        rate_limited=False,
        assistant_turn_count=10,  # Bypass MIN_ASSISTANT_TURNS check
        last_response_error=False,
        last_request_tokens=0,  # Low token count = warm cache
    )

    config = SuggestionConfig(
        enabled=True,
        feature_flag_enabled=True,
        is_interactive=True,  # Daemon acts as proactive interactive proxy
        is_swarm_leader=True,
        env_override=None,
        min_assistant_turns=0,  # Override: daemon bypasses turn gate
    )

    # Gather recent messages from .beads/ conversation artifacts
    messages = _gather_recent_messages()
    if not messages:
        logger.debug("Proactive suggestion: no recent messages, skipping")
        log_suggestion_event(event="proactive_prefetch", status="no_messages")
        return False

    # Two-tier generation callback:
    #   Tier 1: Direct generateContent (lightweight, always available)
    #   Tier 2: Interactions API (stateful, requires enablement)
    # Tier 1 is preferred for single-turn suggestion inference.
    def _generate_fn(msgs: list[dict], prompt: str) -> tuple[str | None, str | None]:
        # Resolve API key from env or GCP Secret Manager
        api_key = _resolve_gemini_api_key()
        if not api_key:
            logger.warning("Proactive generate_fn: no GEMINI_API_KEY available")
            return (None, None)

        # Use the last 3 messages as context seed
        context_msgs = msgs[-3:] if len(msgs) > 3 else msgs
        context_text = "\n".join(m.get("content", "")[:200] for m in context_msgs)
        full_prompt = f"{prompt}\n\nRecent context:\n{context_text}"

        system_instruction = (
            "You predict the developer's next action. "
            "STRICT FORMAT: Reply with ONLY a single short phrase, 2-12 words. "
            "NO periods. NO multiple sentences. NO explanations. NO quotation marks. "
            "NO prefixes like 'Suggestion:'. Just the raw action phrase.\n"
            "GOOD examples: 'Run the test suite', 'Add error handling to the parser', "
            "'Deploy to staging', 'Fix the import statement', 'Refactor auth middleware'\n"
            "BAD examples: 'I suggest running tests. Then deploy.', "
            "'Here is my suggestion: run tests', 'Let me help you with that'"
        )

        gen_id = f"proactive-{int(time.time())}"

        # Tier 1: Direct generateContent — lightweight, always works
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.3,
                    "max_output_tokens": 50,
                },
            )
            result_text = response.text if hasattr(response, "text") else None
            if result_text and result_text.strip():
                # Post-process: strip quotes, trailing periods, cap at 12 words
                cleaned = result_text.strip().strip("\"'`").rstrip(".")
                # Take only the first sentence fragment (before any sentence boundary)
                first_frag = re.split(r"[.!?]\s+", cleaned)[0].strip()
                words = first_frag.split()
                if len(words) > MAX_SUGGESTION_WORDS:
                    first_frag = " ".join(words[:MAX_SUGGESTION_WORDS])
                if first_frag:
                    logger.info("Tier 1 (generateContent) suggestion: '%s'", first_frag[:60])
                    return (first_frag, gen_id)
            logger.debug("Tier 1 returned empty text, trying Tier 2")
        except ImportError:
            logger.warning("google-genai SDK not installed — cannot generate suggestions")
            return (None, None)
        except Exception as e:
            logger.warning("Tier 1 (generateContent) failed: %s: %s", type(e).__name__, e)

        # Tier 2: Interactions API — stateful, richer but requires enablement
        try:
            from speculation_engine.gemini_bridge import GeminiPairProgrammer

            pair = GeminiPairProgrammer(api_key=api_key)
            session = pair.start_session(
                system_prompt=system_instruction,
                model="gemini-3-flash-preview",
            )
            result = pair.send(full_prompt, session=session)
            result_text = getattr(result, "text", None)
            if result_text and result_text.strip():
                logger.info("Tier 2 (Interactions) suggestion: '%s'", result_text.strip()[:60])
                return (result_text.strip(), gen_id)
            logger.debug(
                "Tier 2 returned empty text (result=%s, outputs=%s)",
                type(result).__name__,
                getattr(result, "outputs", "N/A"),
            )
        except Exception as e:
            logger.warning("Tier 2 (Interactions API) failed: %s: %s", type(e).__name__, e)

        return (None, None)

    result: SuggestionResult = try_generate_suggestion(
        messages=messages,
        state=state,
        config=config,
        generate_fn=_generate_fn,
    )

    # Cache the result
    cache_file = BEADS_DIR / "suggestion_cache.json"
    try:
        BEADS_DIR.mkdir(parents=True, exist_ok=True)
        cache_entry = {
            "timestamp": time.time(),
            "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "suggestion": result.suggestion,
            "suppressed": result.suppressed,
            "suppress_reason": result.suppress_reason.value if result.suppress_reason else None,
            "filtered": result.filtered,
            "filter_reason": result.filter_reason.value if result.filter_reason else None,
            "generation_time_ms": round(result.generation_time_ms, 1),
        }
        with open(cache_file, "w") as f:
            json.dump(cache_entry, f, indent=2)
    except Exception as e:
        logger.debug("Failed to write suggestion cache: %s", e)

    # Telemetry
    log_suggestion_event(
        event="proactive_prefetch",
        status="generated" if result.suggestion else "empty",
        suppressed=result.suppressed,
        filtered=result.filtered,
        generation_time_ms=round(result.generation_time_ms, 1),
    )

    if result.suggestion:
        logger.info(
            "Proactive suggestion cached: '%s...' (%.0fms)",
            result.suggestion[:40],
            result.generation_time_ms,
        )
        return True

    logger.debug(
        "Proactive suggestion: no result (suppressed=%s, filtered=%s)",
        result.suppressed,
        result.filtered,
    )
    return False


def _gather_recent_messages() -> list[dict]:
    """Gather recent conversation messages from .beads/ evidence trail.

    Reads the most recent entries from .beads/conversation_history.jsonl
    (if available) or synthesizes a minimal context from the heartbeat.
    """
    history_file = BEADS_DIR / "conversation_history.jsonl"
    messages: list[dict] = []

    if history_file.exists():
        try:
            with open(history_file) as f:
                lines = f.readlines()
            # Take last 10 entries
            for line in lines[-10:]:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if "content" in entry:
                    messages.append({"role": entry.get("role", "user"), "content": entry["content"]})
        except Exception:
            pass

    # Fallback: synthesize minimal context from heartbeat
    if not messages and HEARTBEAT_FILE.exists():
        try:
            hb = json.loads(HEARTBEAT_FILE.read_text())
            # Create a synthetic "last session" context
            messages.append(
                {
                    "role": "user",
                    "content": f"Continue working on the project. Last status: {hb.get('status', {})}",
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": "Ready to continue. What would you like to work on next?",
                }
            )
        except Exception:
            pass

    return messages


def write_heartbeat(status: dict) -> None:
    """Write heartbeat file for monitoring.

    Includes a treeify diagnostic snapshot for human-readable
    health at a glance from ``tail -f .beads/kairos_heartbeat.json``.
    """
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

    # Build tree diagnostic from status dict
    tree_text = ""
    try:
        import importlib

        treeify_mod = importlib.import_module("agnt_utils.treeify")
        tree_data = {
            "KAIROS Heartbeat": {
                "PID": str(os.getpid()),
                "Cycle": status.get("cycle", "?"),
                **{k: v for k, v in status.items() if k != "cycle"},
            }
        }
        tree_text = treeify_mod.treeify(tree_data, show_values=True, max_depth=5)
    except Exception:
        tree_text = "(treeify unavailable)"

    heartbeat = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),  # noqa: UP017
        "pid": os.getpid(),
        "status": status,
        "tree_diagnostic": tree_text,
    }
    HEARTBEAT_FILE.write_text(json.dumps(heartbeat, indent=2))
    logger.debug("Heartbeat tree:\n%s", tree_text)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main_loop(once: bool = False, timeout: int | None = None) -> None:
    """KAIROS main execution loop.

    Args:
        once: If True, run a single cycle then exit.
        timeout: Maximum runtime in seconds. None means no limit.
    """
    logger.info("KAIROS daemon starting (PID %d)", os.getpid())
    logger.info("Repo root: %s", REPO_ROOT)

    # --- Startup wiring ---
    _init_sleep_guard()
    _validate_prompt_assembly()
    _estimate_context_budget()

    last_health = 0.0
    last_dream = 0.0
    last_disk_skill_dream = 0.0
    last_dead_code = 0.0
    last_steward = 0.0
    last_standup = 0.0
    last_vault_ingest = 0.0
    last_quarantine_purge = 0.0
    last_autolint = 0.0
    last_oob_check = 0.0
    last_webhook_check = 0.0
    last_prompt_validation = 0.0
    last_token_budget = 0.0
    last_proactive_suggestion = 0.0
    last_research_sweep = 0.0

    deadline = (time.time() + timeout) if timeout else None
    cycle = 0
    while _running:
        if deadline and time.time() >= deadline:
            logger.info("Timeout reached (%ds), shutting down gracefully...", timeout)
            break
        cycle += 1
        now = time.time()
        status: dict[str, str] = {"cycle": str(cycle)}

        # Health check (every 5 min, jittered)
        if now - last_health >= _jittered(HEALTH_CHECK_INTERVAL):
            status["health"] = json.dumps(health_check())
            last_health = now

        # Light Dream consolidation (daily, only between 2-4 AM local)
        hour = datetime.datetime.now().hour
        if now - last_dream >= _jittered(DREAM_INTERVAL) and 2 <= hour <= 4:
            run_dream_consolidation(tier="light")
            last_dream = now
            status["dream"] = "light_ran"

        # Disk-Skill Dream (weekly, broader off-peak window 1-5 AM)
        if now - last_disk_skill_dream >= _jittered(DISK_SKILL_DREAM_INTERVAL) and 1 <= hour <= 5:
            run_disk_skill_dream()
            last_disk_skill_dream = now
            status["disk_skill_dream"] = "ran"

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

        # OOB report monitor (every 10 min)
        if now - last_oob_check >= _jittered(OOB_REPORT_CHECK_INTERVAL):
            check_oob_reports()
            last_oob_check = now
            status["oob_check"] = "ran"

        # Webhook event processor (every 5 min)
        if now - last_webhook_check >= _jittered(LOOP_STEWARD_INTERVAL):
            process_webhook_events()
            last_webhook_check = now

        # Prompt assembly validation (hourly)
        if now - last_prompt_validation >= _jittered(PROMPT_VALIDATION_INTERVAL):
            if _validate_prompt_assembly():
                status["prompt_assembly"] = "ok"
            else:
                status["prompt_assembly"] = "FAILED"
            last_prompt_validation = now

        # Token budget estimation (hourly, staggered 30min after prompt)
        if now - last_token_budget >= _jittered(PROMPT_VALIDATION_INTERVAL):
            budget = _estimate_context_budget()
            status["token_budget"] = json.dumps(budget) if budget else "unavailable"
            last_token_budget = now
            status["webhook_events"] = "ran"

        # Proactive suggestion prefetch (every 15 min, skip off-peak)
        if now - last_proactive_suggestion >= _jittered(PROACTIVE_SUGGESTION_INTERVAL) and 6 <= hour <= 23:
            if run_proactive_suggestion_probe():
                status["proactive_suggestion"] = "cached"
            else:
                status["proactive_suggestion"] = "empty"
            last_proactive_suggestion = now

        # Research sweep (every 6 hours, off-peak 1-6 AM)
        if now - last_research_sweep >= _jittered(RESEARCH_SWEEP_INTERVAL) and 1 <= hour <= 6:
            if run_research_sweep():
                status["research_sweep"] = "completed"
            else:
                status["research_sweep"] = "skipped_or_failed"
            last_research_sweep = now

        write_heartbeat(status)

        if once:
            logger.info("Single cycle complete, exiting")
            break

        # Sleep 30s between cycles
        for _ in range(30):
            if not _running:
                break
            time.sleep(1)

    # --- Shutdown wiring ---
    _shutdown_sleep_guard()
    logger.info("KAIROS daemon stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description="KAIROS Background Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as background process")
    parser.add_argument("--once", action="store_true", help="Single cycle then exit")
    parser.add_argument(
        "--tier",
        choices=["light", "disk-skill"],
        default=None,
        help="Run a specific dream tier immediately and exit",
    )
    parser.add_argument(
        "--bridge-health",
        action="store_true",
        help="Probe speculation engine bridge health and exit",
    )
    parser.add_argument(
        "--probe-suggestions",
        action="store_true",
        help="Run a proactive suggestion prefetch cycle and exit",
    )
    parser.add_argument(
        "--sweep-now",
        action="store_true",
        help="Run an immediate research sweep and exit (ignores schedule)",
    )
    parser.add_argument(
        "--sweep-topic",
        type=str,
        default=None,
        help="Custom topic for --sweep-now (overrides rotation)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Maximum runtime in seconds (bounded execution)",
    )
    args = parser.parse_args()

    # Bridge health probe — quick liveness check and exit
    if args.bridge_health:
        logger.info("Bridge health probe")
        status = _probe_bridge_health()
        print(json.dumps(status, indent=2))
        sys.exit(0 if status.get("healthy") else 1)

    # Proactive suggestion probe — run one cycle and exit
    if args.probe_suggestions:
        logger.info("Proactive suggestion probe triggered")
        success = run_proactive_suggestion_probe()
        print(
            json.dumps(
                {
                    "success": success,
                    "cache_file": str(BEADS_DIR / "suggestion_cache.json"),
                },
                indent=2,
            )
        )
        sys.exit(0 if success else 1)

    # On-demand research sweep — run immediately and exit
    if args.sweep_now:
        logger.info("On-demand research sweep triggered")
        if args.sweep_topic:
            # Override the rotation topic with the custom one
            success = _run_sweep_with_topic(args.sweep_topic)
        else:
            success = run_research_sweep()
        sys.exit(0 if success else 1)

    # Manual tier invocation — run the specified tier and exit
    if args.tier:
        logger.info("Manual tier invocation: %s", args.tier)
        if args.tier == "light":
            success = run_dream_consolidation(tier="light")
        else:
            success = run_disk_skill_dream()
        sys.exit(0 if success else 1)

    if args.daemon:
        pid = os.fork()
        if pid > 0:
            logger.info("KAIROS daemon forked (PID %d)", pid)
            sys.exit(0)
        os.setsid()
        main_loop(once=False, timeout=args.timeout)
    else:
        main_loop(once=args.once, timeout=args.timeout)


if __name__ == "__main__":
    main()
