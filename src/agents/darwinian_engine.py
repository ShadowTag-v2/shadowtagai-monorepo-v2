# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Darwinian Fitness Engine — Mutation Survival Scoring.

Evaluates BioAgents mutations against measurable fitness:
  1. bench_ms before/after (5% threshold)
  2. lint_score: ruff violation count
  3. dead_code_count: F401/F841
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents.bioagents_agent import FitnessVerdict, Mutation, MutationBatch, MutationType

logger = logging.getLogger("darwinian-engine")

IMPROVEMENT_THRESHOLD_PCT = 5.0
REGRESSION_THRESHOLD_PCT = -1.0


@dataclass
class FitnessSnapshot:
  target: str
  bench_ms: float = 0.0
  lint_violations: int = 0
  dead_code_violations: int = 0
  test_pass_rate: float = 1.0
  timestamp: float = field(default_factory=time.time)


@dataclass
class FitnessReport:
  batch_id: str
  before: dict[str, FitnessSnapshot] = field(default_factory=dict)
  after: dict[str, FitnessSnapshot] = field(default_factory=dict)
  verdicts: dict[str, FitnessVerdict] = field(default_factory=dict)
  elapsed_ms: float = 0.0

  def summary(self) -> dict[str, int]:
    counts = {v.value: 0 for v in FitnessVerdict}
    for verdict in self.verdicts.values():
      counts[verdict.value] += 1
    return counts


class DarwinianEngine:
  def __init__(self, repo_root: Path | None = None, dry_run: bool = False) -> None:
    self._repo_root = repo_root or Path.cwd()
    self._reports: list[FitnessReport] = []
    self._dry_run = dry_run
    self._backups: dict[str, str] = {}  # target -> original content
    logger.info(
      "🧬 Darwinian Engine initialized (root=%s, dry_run=%s)",
      self._repo_root,
      dry_run,
    )

  def snapshot_file(self, target: str) -> FitnessSnapshot:
    """Capture lint/dead-code metrics for a file via ruff."""
    snapshot = FitnessSnapshot(target=target)
    file_path = self._repo_root / target
    if not file_path.exists():
      return snapshot
    try:
      result = subprocess.run(
        ["ruff", "check", "--quiet", "--output-format=json", str(file_path)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(self._repo_root),
      )
      if result.stdout.strip():
        violations = json.loads(result.stdout)
        snapshot.lint_violations = len(violations)
        snapshot.dead_code_violations = sum(
          1 for v in violations if v.get("code", "").startswith(("F401", "F841"))
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
      logger.warning("Ruff snapshot failed for %s: %s", target, e)
    # Benchmark: time how long it takes to import-check the file
    snapshot.bench_ms = self._benchmark_file(file_path)
    return snapshot

  def _benchmark_file(self, file_path: Path) -> float:
    """Lightweight benchmark: time ruff check execution as a proxy for complexity."""
    if not file_path.exists():
      return 0.0
    try:
      start = time.perf_counter()
      subprocess.run(
        ["ruff", "check", "--quiet", str(file_path)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(self._repo_root),
      )
      return (time.perf_counter() - start) * 1000
    except (subprocess.TimeoutExpired, FileNotFoundError):
      return 0.0

  def _backup_file(self, target: str) -> bool:
    """Backup file content before mutation. Returns True if backup succeeded."""
    file_path = self._repo_root / target
    if not file_path.exists():
      return False
    try:
      self._backups[target] = file_path.read_text(encoding="utf-8")
      return True
    except OSError as e:
      logger.warning("Backup failed for %s: %s", target, e)
      return False

  def _revert_file(self, target: str) -> bool:
    """Revert file to pre-mutation state from backup."""
    if target not in self._backups:
      logger.warning("No backup found for %s, cannot revert", target)
      return False
    file_path = self._repo_root / target
    try:
      file_path.write_text(self._backups[target], encoding="utf-8")
      del self._backups[target]
      logger.debug("🔄 Reverted %s from backup", target)
      return True
    except OSError as e:
      logger.error("Revert failed for %s: %s", target, e)
      return False

  def apply_mutation(self, mutation: Mutation) -> bool:
    """Apply a mutation to the filesystem.

    Currently supports:
      - DEAD_CODE_REMOVAL: runs ruff check --select F401,F841 --fix
      - Other types: no-op (plan only, no auto-apply)

    Returns True if the mutation was applied successfully.
    """
    if self._dry_run:
      logger.info("🧪 [DRY RUN] Would apply mutation %s", mutation.mutation_id)
      return False

    file_path = self._repo_root / mutation.target_file
    if not file_path.exists():
      logger.warning("Target file does not exist: %s", mutation.target_file)
      return False

    # Backup before mutation
    if not self._backup_file(mutation.target_file):
      return False

    if mutation.mutation_type == MutationType.DEAD_CODE_REMOVAL:
      try:
        result = subprocess.run(
          ["ruff", "check", "--select", "F401,F841", "--fix", str(file_path)],
          capture_output=True,
          text=True,
          timeout=30,
          cwd=str(self._repo_root),
        )
        logger.info(
          "🧬 Applied dead code fix to %s (exit=%d)",
          mutation.target_file,
          result.returncode,
        )
        return True
      except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error("Mutation apply failed for %s: %s", mutation.mutation_id, e)
        self._revert_file(mutation.target_file)
        return False
    else:
      # Non-dead-code mutations are plan-only; revert backup since no change made
      self._revert_file(mutation.target_file)
      logger.debug(
        "🧬 Mutation %s is plan-only (type=%s)",
        mutation.mutation_id,
        mutation.mutation_type.value,
      )
      return False

  def evaluate_mutation(
    self,
    mutation: Mutation,
    before: FitnessSnapshot,
    after: FitnessSnapshot,
  ) -> FitnessVerdict:
    """Score a mutation against before/after fitness snapshots."""
    mutation.lint_score_before = before.lint_violations
    mutation.lint_score_after = after.lint_violations
    mutation.bench_ms_before = before.bench_ms
    mutation.bench_ms_after = after.bench_ms
    if after.lint_violations > before.lint_violations:
      mutation.verdict = FitnessVerdict.REGRESS
      return FitnessVerdict.REGRESS
    if after.dead_code_violations < before.dead_code_violations:
      mutation.verdict = FitnessVerdict.PROMOTE
      return FitnessVerdict.PROMOTE
    if mutation.bench_ms_before and mutation.bench_ms_after:
      delta = mutation.fitness_delta_pct
      if delta is not None and delta <= -IMPROVEMENT_THRESHOLD_PCT:
        mutation.verdict = FitnessVerdict.PROMOTE
        return FitnessVerdict.PROMOTE
    mutation.verdict = FitnessVerdict.NEUTRAL
    return FitnessVerdict.NEUTRAL

  def evaluate_batch(self, batch: MutationBatch) -> FitnessReport:
    """Evaluate a full mutation batch with real apply/revert when possible."""
    start = time.time()
    report = FitnessReport(batch_id=batch.batch_id)
    # Pre-snapshot all targets
    targets = {m.target_file for m in batch.mutations}
    for target in targets:
      report.before[target] = self.snapshot_file(target)
    for mutation in batch.mutations:
      before = report.before.get(
        mutation.target_file, FitnessSnapshot(target=mutation.target_file)
      )
      # Attempt real apply → snapshot → revert cycle
      applied = self.apply_mutation(mutation)
      if applied:
        after = self.snapshot_file(mutation.target_file)
        self._revert_file(mutation.target_file)
      else:
        # Fallback: use before snapshot as after (no change)
        after = FitnessSnapshot(
          target=mutation.target_file,
          lint_violations=before.lint_violations,
          dead_code_violations=before.dead_code_violations,
          bench_ms=before.bench_ms,
        )
      report.after[mutation.target_file] = after
      verdict = self.evaluate_mutation(mutation, before, after)
      report.verdicts[mutation.mutation_id] = verdict
    report.elapsed_ms = (time.time() - start) * 1000
    self._reports.append(report)
    logger.info("🧬 Batch %s evaluated in %.0fms", batch.batch_id, report.elapsed_ms)
    return report

  def get_diagnostics(self) -> dict[str, Any]:
    total = sum(len(r.verdicts) for r in self._reports)
    promoted = sum(
      sum(1 for v in r.verdicts.values() if v == FitnessVerdict.PROMOTE)
      for r in self._reports
    )
    return {
      "engine": "darwinian",
      "total_evaluated": total,
      "promoted": promoted,
      "survival_rate": promoted / total if total > 0 else 0.0,
    }
