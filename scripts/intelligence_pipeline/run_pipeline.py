"""
Intelligence Pipeline Orchestrator

Wires 2,856 ingested LanceDB docs against the codebase, git history, and biz plans.

Usage:
    python3 scripts/intelligence_pipeline/run_pipeline.py
    python3 scripts/intelligence_pipeline/run_pipeline.py --skip-step 2
    python3 scripts/intelligence_pipeline/run_pipeline.py --start-from 5
    python3 scripts/intelligence_pipeline/run_pipeline.py --top-n 5
    python3 scripts/intelligence_pipeline/run_pipeline.py --dry-run
    python3 scripts/intelligence_pipeline/run_pipeline.py --report-only

Steps:
  1  domain_tagger       — classify 2,856 docs → crossref.db::doc_domains
  2  codebase_embedder   — embed .py/.go/.ts → LanceDB::code_files   (~3 hrs)
  3  cross_domain_matcher — doc→code, doc→doc, doc→commit matches
  4  gap_analyzer        — gap_matrix (Type A/B/C)
  5  synthesis_report    — Gemini Flash → JSON+MD action queue
  6  memory_injector     — inject to CLAUDE.md
  7  github_sync         — push branch + create PRs
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

RUN_LOG_DIR = REPO_ROOT / "data" / "intelligence_pipeline"


@dataclass
class PipelineConfig:
    dry_run: bool = False
    skip_steps: set = field(default_factory=set)
    start_from: int = 1
    top_n: int = 50
    report_only: bool = False


def write_run_log(stats: dict, start_time: float) -> None:
    """Write pipeline execution log to data/intelligence_pipeline/."""
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = RUN_LOG_DIR / f"pipeline_run_{ts}.json"
    stats["elapsed_seconds"] = round(time.time() - start_time, 2)
    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Run log: {log_path}")


def run_step(step_num: int, label: str, fn, cfg: PipelineConfig, stats: dict) -> bool:
    """[Step N] Execute a pipeline step with skip/dry-run logic."""
    if step_num < cfg.start_from:
        logger.info(f"[Step {step_num}] {label} — SKIPPED (start_from={cfg.start_from})")
        return True
    if step_num in cfg.skip_steps:
        logger.info(f"[Step {step_num}] {label} — SKIPPED (--skip-step)")
        return True
    if cfg.dry_run:
        logger.info(f"[Step {step_num}] {label} — DRY RUN (would execute)")
        return True

    logger.info(f"[Step {step_num}] {label} — STARTING")
    t0 = time.time()
    try:
        result = fn(cfg)
        elapsed = round(time.time() - t0, 2)
        stats[label] = {"status": "ok", "elapsed": elapsed}
        logger.info(f"[Step {step_num}] {label} — DONE ({elapsed}s)")
        return True
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        stats[label] = {"status": "error", "error": str(e), "elapsed": elapsed}
        logger.error(f"[Step {step_num}] {label} — FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Intelligence Pipeline Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Log steps without executing")
    parser.add_argument("--skip-step", type=int, action="append", default=[], help="Skip step N")
    parser.add_argument("--start-from", type=int, default=1, help="Start from step N")
    parser.add_argument("--top-n", type=int, default=50, help="Top N gaps to process")
    parser.add_argument("--report-only", action="store_true", help="Only run report steps (4-5)")
    args = parser.parse_args()

    cfg = PipelineConfig(
        dry_run=args.dry_run,
        skip_steps=set(args.skip_step),
        start_from=args.start_from,
        top_n=args.top_n,
        report_only=args.report_only,
    )

    if cfg.report_only:
        cfg.start_from = max(cfg.start_from, 4)
        cfg.skip_steps.update({6, 7})

    # Lazy imports to avoid loading heavy deps for --help
    from scripts.intelligence_pipeline.domain_tagger import run_domain_tagger
    from scripts.intelligence_pipeline.codebase_embedder import run_codebase_embedder
    from scripts.intelligence_pipeline.cross_domain_matcher import run_cross_domain_matcher
    from scripts.intelligence_pipeline.gap_analyzer import run_gap_analyzer
    from scripts.intelligence_pipeline.synthesis_report import run_synthesis_report
    from scripts.intelligence_pipeline.memory_injector import run_memory_injector
    from scripts.intelligence_pipeline.github_sync import run_github_sync

    steps = [
        (1, "domain_tagger", run_domain_tagger),
        (2, "codebase_embedder", run_codebase_embedder),
        (3, "cross_domain_matcher", run_cross_domain_matcher),
        (4, "gap_analyzer", run_gap_analyzer),
        (5, "synthesis_report", run_synthesis_report),
        (6, "memory_injector", run_memory_injector),
        (7, "github_sync", run_github_sync),
    ]

    stats: dict = {}
    start_time = time.time()
    logger.info("Intelligence Pipeline — starting")

    for step_num, label, fn in steps:
        ok = run_step(step_num, label, fn, cfg, stats)
        if not ok:
            logger.error(f"Pipeline halted at step {step_num}")
            break

    write_run_log(stats, start_time)
    logger.info("Intelligence Pipeline — finished")


if __name__ == "__main__":
    main()
