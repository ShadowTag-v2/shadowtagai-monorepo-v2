#!/usr/bin/env python3
"""Gemini Scheduler - Run workflows via Gemini Layer instead of GitHub Actions.
Bypasses GitHub Actions billing by using Gemini API directly.
"""

import json

# Add project root to path
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import schedule

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
  import importlib

  _st_mod = importlib.import_module("src.ShadowTag-v2.services.gemini_core")
  GeminiAntigravity = _st_mod.GeminiAntigravity
except (ImportError, ModuleNotFoundError):
  GeminiAntigravity = None

try:
  from agents.jura_protocol import JuraProtocol
except ImportError:
  JuraProtocol = None

try:
  from agents.bugbot import BugBot
except ImportError:
  BugBot = None


class GeminiScheduler:
  """Run scheduled tasks through Gemini layer instead of GitHub Actions."""

  def __init__(self) -> None:
    self.gemini = None
    self.jura = None
    self.bugbot = BugBot()
    self.log_file = Path(__file__).parent.parent / "logs" / "scheduler.log"
    self.log_file.parent.mkdir(exist_ok=True)

  def _init_gemini(self) -> bool:
    """Initialize Gemini on first use (lazy loading)."""
    if self.gemini is None:
      try:
        self.gemini = GeminiAntigravity()
        self.jura = JuraProtocol()
        return True
      except Exception as e:
        self._log(f"Gemini init failed: {e}")
        return False
    return True

  def _log(self, message: str) -> None:
    """Log to file and stdout."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_entry = f"[{timestamp}] {message}"

    with open(self.log_file, "a") as f:
      f.write(log_entry + "\n")

  def run_ingestion(self):
    """Run the ingestion workflow (replaces GitHub Actions 'Ingestion (hourly)')."""
    self._log("Starting ingestion run")

    # Step 1: Static analysis (no Gemini needed)
    self._log("Running BugBot analysis")
    bugbot_results = self.bugbot.full_scan("src/")

    # Step 2: Initialize Gemini for AI tasks
    if not self._init_gemini():
      self._log("Skipping AI tasks - Gemini unavailable")
      return {"status": "partial", "bugbot": bugbot_results, "gemini": "unavailable"}

    # Step 3: AI-powered code review
    self._log("Running Jura assessment")
    try:
      # Quick assessment of recent changes
      assessment = self.jura.quick_assess(
        "Review codebase health based on BugBot results: "
        + json.dumps(bugbot_results, default=str)[:1000]
      )
    except Exception as e:
      assessment = {"error": str(e)}

    # Step 4: Generate summary
    self._log("Generating summary")
    try:
      summary = self.gemini.generate_text(
        f"""Summarize this code health report in 2-3 sentences:
                BugBot Score: {bugbot_results.get("health_score", 0)}/100
                Issues: {bugbot_results.get("total_issues", 0)}
                Jura Assessment: {assessment.get("recommendation", "N/A")}
                """,
        json_output=False,
      )
    except Exception as e:
      summary = f"Summary generation failed: {e}"

    result = {
      "status": "complete",
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "health_score": bugbot_results.get("health_score", 0),
      "total_issues": bugbot_results.get("total_issues", 0),
      "jura_recommendation": assessment.get("recommendation", "N/A"),
      "summary": summary,
    }

    self._log(f"Ingestion complete: {result['health_score']}/100")

    # Save results
    results_file = (
      self.log_file.parent
      / f"ingestion_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(results_file, "w") as f:
      json.dump(result, f, indent=2)

    return result

  def run_judge_evaluation(self, candidate_id: str, proof: dict):
    """Run Jura evaluation on demand."""
    if not self._init_gemini():
      return {"status": "error", "message": "Gemini unavailable"}

    self._log(f"Jura evaluation for {candidate_id}")
    passed, reasoning = self.jura.administer_exam(candidate_id, 0, proof)

    return {"candidate": candidate_id, "passed": passed, "reasoning": reasoning}

  def start_scheduler(self, interval_minutes: int = 60) -> None:
    """Start the scheduler loop."""
    self._log(f"Starting scheduler with {interval_minutes} minute interval")

    # Schedule ingestion
    schedule.every(interval_minutes).minutes.do(self.run_ingestion)

    # Run immediately on start
    self.run_ingestion()

    # Loop
    while True:
      schedule.run_pending()
      time.sleep(60)


def main() -> None:
  """Run scheduler or single task."""
  import argparse

  parser = argparse.ArgumentParser(description="Gemini Scheduler")
  parser.add_argument(
    "--run-once", action="store_true", help="Run ingestion once and exit"
  )
  parser.add_argument(
    "--interval", type=int, default=60, help="Interval in minutes (default: 60)"
  )

  args = parser.parse_args()

  scheduler = GeminiScheduler()

  if args.run_once:
    scheduler.run_ingestion()
  else:
    scheduler.start_scheduler(args.interval)


if __name__ == "__main__":
  main()
