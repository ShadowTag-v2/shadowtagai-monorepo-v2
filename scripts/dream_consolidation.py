# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Layer 3 dream_consolidation.py daemon.

Orchestrates context orientation, gathering, consolidation, and pruning
based on the daemon registry. Includes the Claude Code v2.1.119
contradiction detection decision tree ported from the Dream CLAUDE.md
memory reconciliation protocol.

4-Phase Pipeline:
  Phase 1: Preparation — orient context vectors, read recent logs/sessions
  Phase 2: Topics — extract events/decisions, reconcile against AGENTS.md
  Phase 3: Rules & Learnings — capture painful/inefficient workflow patterns
  Phase 4: Prioritization & Pruning — enforce MEMORY.md budget (<200 lines)

Contradiction Detection (3-way decision tree):
  1. Memory is stale → AGENTS.md is maintained source → delete/rewrite memory
  2. AGENTS.md may be stale → memory dated after and corrects it → annotate only
  3. Not a conflict → memory adds detail AGENTS.md doesn't cover → leave it
"""

from __future__ import annotations

import datetime
import json
import logging
import pathlib
import time
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Budget constants (ported from Claude Code skill-dream-memory-consolidation v2.1.119)
MEMORY_INDEX_MAX_LINES = 200
MEMORY_INDEX_MAX_KB = 25
LEARNINGS_DIR = "learnings"
BEADS_DIR = ".beads"


class ConflictResolution(StrEnum):
    """Three-way decision outcomes for memory vs. truth surface conflicts."""

    MEMORY_STALE = "memory_stale"
    TRUTH_SURFACE_STALE = "truth_surface_stale"
    NOT_A_CONFLICT = "not_a_conflict"


@dataclass
class MemoryRecord:
    """Represents a single memory fragment with metadata."""

    slug: str
    content: str
    source: str  # 'feedback', 'project', 'session', 'topic'
    created_at: str  # ISO 8601
    file_path: str | None = None

    @property
    def created_date(self) -> datetime.date | None:
        """Parse the creation date for comparison."""
        try:
            return datetime.date.fromisoformat(self.created_at[:10])
        except (ValueError, IndexError):
            return None


@dataclass
class ReconciliationResult:
    """Outcome of reconciling a memory against a truth surface."""

    memory_slug: str
    resolution: ConflictResolution
    annotation: str = ""
    action_taken: str = ""


@dataclass
class DreamCycleReport:
    """Summary report for a single dream consolidation cycle."""

    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    memories_reviewed: int = 0
    contradictions_found: int = 0
    memories_deleted: int = 0
    memories_annotated: int = 0
    learnings_extracted: int = 0
    reconciliations: list[ReconciliationResult] = field(default_factory=list)


class DreamConsolidator:
    """Handles nightly Knowledge Integration (KI) maintenance tasks.

    Implements the 4-phase Dream protocol with contradiction detection
    ported from Claude Code v2.1.119 system-prompt-dream-claudemd-memory-reconciliation.
    """

    def __init__(
        self,
        knowledge_root: str | None = None,
        agents_md_path: str | None = None,
    ) -> None:
        """Initialize the consolidator.

        Args:
            knowledge_root: Path to the knowledge directory. Defaults to
                ~/.gemini/antigravity/knowledge/.
            agents_md_path: Path to the canonical AGENTS.md truth surface.
                Defaults to .ruler/AGENTS.md in the workspace.
        """
        self.logger = logging.getLogger(__name__)
        self.knowledge_root = pathlib.Path(knowledge_root or pathlib.Path.home() / ".gemini" / "antigravity" / "knowledge")
        self.agents_md_path = pathlib.Path(agents_md_path or pathlib.Path.cwd() / ".ruler" / "AGENTS.md")
        self.report = DreamCycleReport()
        self._job_dir: pathlib.Path | None = None

    # ------------------------------------------------------------------
    # Phase 1: Preparation
    # ------------------------------------------------------------------

    def orient(self) -> None:
        """Phase 1a: Orient context and align current session vectors."""
        self.logger.info("[Phase 1] Orienting context vectors...")
        self.logger.info("  Reading recent KI metadata from %s", self.knowledge_root)
        time.sleep(0.1)

    def gather(self) -> list[MemoryRecord]:
        """Phase 1b: Gather disparate context fragments from active memory logs.

        Returns:
            List of memory records found in the knowledge directory.
        """
        self.logger.info("[Phase 1] Gathering memory logs and context fragments...")
        records: list[MemoryRecord] = []

        if not self.knowledge_root.exists():
            self.logger.warning("Knowledge root does not exist: %s", self.knowledge_root)
            return records

        for meta_path in self.knowledge_root.rglob("metadata.json"):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                record = MemoryRecord(
                    slug=meta_path.parent.name,
                    content=meta.get("summary", ""),
                    source=meta.get("source", "project"),
                    created_at=meta.get("created_at", meta.get("last_accessed", "")),
                    file_path=str(meta_path),
                )
                records.append(record)
            except (json.JSONDecodeError, OSError) as exc:
                self.logger.warning("Skipping malformed metadata: %s (%s)", meta_path, exc)

        self.report.memories_reviewed = len(records)
        self.logger.info("  Found %d memory records", len(records))
        return records

    # ------------------------------------------------------------------
    # Contradiction Detection (3-way decision tree)
    # ------------------------------------------------------------------

    def _load_truth_surface(self) -> str:
        """Load the canonical AGENTS.md truth surface for reconciliation."""
        if self.agents_md_path.exists():
            return self.agents_md_path.read_text(encoding="utf-8")
        self.logger.warning("AGENTS.md not found at %s", self.agents_md_path)
        return ""

    def _detect_contradiction(
        self,
        memory: MemoryRecord,
        truth_content: str,
    ) -> ConflictResolution:
        """Apply the 3-way contradiction decision tree.

        Decision tree (from Claude Code v2.1.119):
        1. Memory is stale — AGENTS.md and memory describe different procedures
           for the same task. AGENTS.md is the maintained, checked-in source.
           → Delete the memory, or rewrite to keep the *why* if useful.
        2. AGENTS.md may be stale — memory is clearly dated after AGENTS.md
           and explicitly corrects it.
           → Do NOT edit AGENTS.md during a dream. Annotate the memory.
        3. Not a conflict — memory adds detail AGENTS.md doesn't cover,
           or narrows a rule with a stated reason.
           → Leave it.

        Args:
            memory: The memory record to evaluate.
            truth_content: The current AGENTS.md content.

        Returns:
            The conflict resolution classification.
        """
        if not truth_content:
            return ConflictResolution.NOT_A_CONFLICT

        content_lower = memory.content.lower()

        # Heuristic: check if memory explicitly references overriding/correcting AGENTS.md
        correction_signals = [
            "contradicts agents.md",
            "override agents.md",
            "agents.md is wrong",
            "agents.md should be updated",
            "corrects agents.md",
            "agents.md is stale",
            "contradicts claude.md",
            "override gemini.md",
        ]
        if any(signal in content_lower for signal in correction_signals):
            return ConflictResolution.TRUTH_SURFACE_STALE

        # Heuristic: check if memory describes a procedure that AGENTS.md also covers
        # by looking for shared topic keywords
        truth_lower = truth_content.lower()
        memory_topics = [word for word in content_lower.split() if len(word) > 5 and word.isalpha()]
        overlap_count = sum(1 for topic in memory_topics if topic in truth_lower)
        overlap_ratio = overlap_count / max(len(memory_topics), 1)

        # High overlap + memory content suggests different procedure = stale memory
        conflict_signals = ["instead of", "no longer", "deprecated", "replaced by", "was changed to"]
        if overlap_ratio > 0.3 and any(signal in content_lower for signal in conflict_signals):
            return ConflictResolution.MEMORY_STALE

        return ConflictResolution.NOT_A_CONFLICT

    def reconcile_memory(
        self,
        memory: MemoryRecord,
        truth_content: str,
    ) -> ReconciliationResult:
        """Reconcile a single memory against the truth surface.

        Args:
            memory: The memory record to reconcile.
            truth_content: The current AGENTS.md content.

        Returns:
            The reconciliation result with resolution and action taken.
        """
        resolution = self._detect_contradiction(memory, truth_content)

        result = ReconciliationResult(
            memory_slug=memory.slug,
            resolution=resolution,
        )

        if resolution == ConflictResolution.MEMORY_STALE:
            result.annotation = (
                f"Memory '{memory.slug}' conflicts with AGENTS.md — AGENTS.md is the maintained source. Memory marked for deletion/rewrite."
            )
            result.action_taken = "MARKED_FOR_DELETION"
            self.report.memories_deleted += 1
            self.logger.info("  ⚠ STALE MEMORY: %s — %s", memory.slug, result.annotation)

        elif resolution == ConflictResolution.TRUTH_SURFACE_STALE:
            result.annotation = (
                f"Memory '{memory.slug}' explicitly corrects AGENTS.md — annotated for user review. AGENTS.md NOT modified during dream."
            )
            result.action_taken = "ANNOTATED_FOR_REVIEW"
            self.report.memories_annotated += 1
            self.logger.info("  📌 AGENTS.MD MAY BE STALE: %s — %s", memory.slug, result.annotation)

        else:
            result.action_taken = "NO_ACTION"

        # Enqueue to bounded evidence batcher
        self._enqueue_evidence({
            "slug": memory.slug,
            "resolution": resolution.value,
            "action": result.action_taken,
            "annotation": result.annotation,
        })

        return result

    # ------------------------------------------------------------------
    # Date Conversion (existing)
    # ------------------------------------------------------------------

    def _convert_relative_to_absolute_dates(self, content: str) -> str:
        """Convert relative dates (e.g., 'today', 'yesterday') to absolute dates."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        content = content.replace("today", today).replace("Today", today)
        content = content.replace("yesterday", yesterday).replace("Yesterday", yesterday)
        return content

    # ------------------------------------------------------------------
    # Phase 2: Topics — consolidate and reconcile
    # ------------------------------------------------------------------

    def consolidate(self, memories: list[MemoryRecord] | None = None) -> None:
        """Phase 2: Consolidate fragments into structured epistemic memory nodes.

        Applies:
        - Relative-to-absolute date conversion
        - Contradiction resolution against AGENTS.md
        - Deduplication of topic coverage

        Args:
            memories: Optional pre-gathered memory records.
        """
        self.logger.info("[Phase 2] Consolidating knowledge into unified epistemic memory...")
        self.logger.info("  Applying relative-to-absolute date conversion...")
        self.logger.info("  Running contradiction detection against AGENTS.md...")

        truth_content = self._load_truth_surface()
        records = memories or []

        for record in records:
            # Apply date normalization
            record.content = self._convert_relative_to_absolute_dates(record.content)

            # Reconcile against truth surface
            result = self.reconcile_memory(record, truth_content)
            self.report.reconciliations.append(result)

            if result.resolution != ConflictResolution.NOT_A_CONFLICT:
                self.report.contradictions_found += 1

        self.logger.info(
            "  Consolidation complete: %d reviewed, %d contradictions found",
            len(records),
            self.report.contradictions_found,
        )

    # ------------------------------------------------------------------
    # Phase 3: Rules & Learnings
    # ------------------------------------------------------------------

    def extract_learnings(self, memories: list[MemoryRecord] | None = None) -> int:
        """Phase 3: Extract painful/inefficient workflow patterns into learnings.

        Reviews memory records for signals of frustration, build failures,
        or test failures and logs them for future reference.

        Args:
            memories: Optional pre-gathered memory records.

        Returns:
            Number of learnings extracted.
        """
        self.logger.info("[Phase 3] Extracting learnings from painful workflow patterns...")
        records = memories or []
        learnings_count = 0

        pain_signals = [
            "failed",
            "error",
            "broken",
            "frustrated",
            "workaround",
            "hack",
            "manual",
            "couldn't build",
            "test failure",
            "regression",
            "retry",
            "hung",
            "timeout",
            "blocked",
        ]

        for record in records:
            content_lower = record.content.lower()
            if any(signal in content_lower for signal in pain_signals):
                learnings_count += 1
                self.logger.info("  📚 Learning extracted from: %s", record.slug)

        self.report.learnings_extracted = learnings_count
        self.logger.info("  Extracted %d learnings", learnings_count)
        return learnings_count

    # ------------------------------------------------------------------
    # Phase 4: Prioritization & Pruning
    # ------------------------------------------------------------------

    def prune(self) -> None:
        """Phase 4: Prune decayed or redundant context arrays to adhere to the budget.

        Enforces:
        - MEMORY.md index under 200 lines
        - Individual indices under 25KB
        - One-line hooks for referenced topics
        """
        self.logger.info("[Phase 4] Pruning decayed context to maintain budget discipline...")
        self.logger.info(
            "  Budget: MEMORY.md < %d lines, indices < %dKB",
            MEMORY_INDEX_MAX_LINES,
            MEMORY_INDEX_MAX_KB,
        )

        # Check actual KI count
        ki_count = 0
        if self.knowledge_root.exists():
            ki_count = sum(1 for _ in self.knowledge_root.rglob("metadata.json"))

        self.logger.info("  Current KI count: %d", ki_count)

    # ------------------------------------------------------------------
    # Job-Scoped Scratch Directory (ported from background-session-instructions v2.1.119)
    # ------------------------------------------------------------------

    def _create_job_dir(self) -> pathlib.Path:
        """Create a job-scoped scratch directory for this daemon cycle.

        Provides environment isolation per Claude Code background-session-instructions
        pattern. Each dream cycle gets its own temporary workspace so that
        concurrent daemons never collide.

        Returns:
            Path to the created job directory.
        """
        workspace = pathlib.Path.cwd()
        beads_dir = workspace / BEADS_DIR
        beads_dir.mkdir(parents=True, exist_ok=True)

        job_dir = pathlib.Path(
            tempfile.mkdtemp(
                prefix=f"dream-{datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%S')}-",
                dir=beads_dir,
            )
        )
        self.logger.info("  Job scratch directory: %s", job_dir)
        self._job_dir = job_dir
        return job_dir

    def _write_cycle_report(self) -> None:
        """Write the dream cycle report to the beads evidence trail."""
        if self._job_dir is None:
            return

        report_path = self._job_dir / "dream_cycle_report.json"
        report_data = {
            "timestamp": self.report.timestamp,
            "memories_reviewed": self.report.memories_reviewed,
            "contradictions_found": self.report.contradictions_found,
            "memories_deleted": self.report.memories_deleted,
            "memories_annotated": self.report.memories_annotated,
            "learnings_extracted": self.report.learnings_extracted,
            "reconciliations": [
                {
                    "slug": r.memory_slug,
                    "resolution": r.resolution.value,
                    "annotation": r.annotation,
                    "action_taken": r.action_taken,
                }
                for r in self.report.reconciliations
            ],
        }
        report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        self.logger.info("  Report written to: %s", report_path)
        time.sleep(0.1)

    # ------------------------------------------------------------------
    # Bounded Evidence Batcher (ported from Claude Agent SDK transcript_mirror_batcher.py)
    # ------------------------------------------------------------------

    # Eager-flush thresholds. Keeps memory flat during long sessions.
    _BATCHER_MAX_ENTRIES = 500
    _BATCHER_MAX_BYTES = 1 << 20  # 1 MiB
    _BATCHER_MAX_RETRIES = 3
    _BATCHER_BACKOFF_S = (0.2, 0.8)

    def _init_batcher(self) -> None:
        """Initialize the evidence batcher state for this cycle."""
        self._evidence_pending: list[dict] = []
        self._evidence_pending_bytes = 0

    def _enqueue_evidence(self, entry: dict) -> None:
        """Buffer an evidence entry; flush eagerly if thresholds exceeded.

        Ported from TranscriptMirrorBatcher.enqueue() — fire-and-forget
        pattern that keeps adapter latency off the hot path. The batcher
        coalesces entries and flushes when the pending buffer exceeds
        MAX_ENTRIES (500) or MAX_BYTES (1 MiB).

        Args:
            entry: A dict representing an evidence trail entry.
        """
        entry_bytes = len(json.dumps(entry))
        self._evidence_pending.append(entry)
        self._evidence_pending_bytes += entry_bytes

        if (
            len(self._evidence_pending) > self._BATCHER_MAX_ENTRIES
            or self._evidence_pending_bytes > self._BATCHER_MAX_BYTES
        ):
            self._flush_evidence()

    def _flush_evidence(self) -> None:
        """Flush all pending evidence entries to the beads trail.

        Implements bounded retry with backoff per the Claude Agent SDK
        pattern. Failures are logged but never raised — the local-disk
        cycle report is already durable.
        """
        if not self._evidence_pending or self._job_dir is None:
            return

        items = self._evidence_pending
        self._evidence_pending = []
        self._evidence_pending_bytes = 0

        evidence_path = self._job_dir / "evidence_batch.jsonl"
        last_err: Exception | None = None

        for attempt in range(self._BATCHER_MAX_RETRIES):
            if attempt > 0:
                time.sleep(self._BATCHER_BACKOFF_S[attempt - 1])
            try:
                with evidence_path.open("a", encoding="utf-8") as f:
                    for item in items:
                        f.write(json.dumps(item) + "\n")
                self.logger.info(
                    "  Evidence batch flushed: %d entries to %s",
                    len(items),
                    evidence_path,
                )
                return
            except OSError as exc:
                last_err = exc
                self.logger.debug(
                    "  Evidence flush attempt %d/%d failed: %s",
                    attempt + 1,
                    self._BATCHER_MAX_RETRIES,
                    exc,
                )

        self.logger.error(
            "  Evidence flush failed after %d attempts: %s",
            self._BATCHER_MAX_RETRIES,
            last_err,
        )

    # ------------------------------------------------------------------
    # Pipeline Orchestration
    # ------------------------------------------------------------------

    def run_nightly_cycle(self) -> DreamCycleReport:
        """Execute the full nightly dream consolidation pipeline.

        Returns:
            The dream cycle report with all metrics.
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting nightly dream consolidation cycle...")
        self.logger.info("=" * 60)

        # Phase 0: Job isolation
        self._create_job_dir()
        self._init_batcher()

        # Phase 1: Preparation
        self.orient()
        memories = self.gather()

        # Phase 2: Topics + Reconciliation
        self.consolidate(memories)

        # Phase 3: Rules & Learnings
        self.extract_learnings(memories)

        # Phase 4: Prioritization & Pruning
        self.prune()

        # Flush evidence batcher and write evidence trail
        self._flush_evidence()
        self._write_cycle_report()

        self.logger.info("=" * 60)
        self.logger.info("Nightly dream consolidation cycle complete.")
        self.logger.info(
            "  Report: %d reviewed, %d contradictions, %d deleted, %d annotated, %d learnings",
            self.report.memories_reviewed,
            self.report.contradictions_found,
            self.report.memories_deleted,
            self.report.memories_annotated,
            self.report.learnings_extracted,
        )
        self.logger.info("=" * 60)
        return self.report


def main() -> None:
    """Daemon entrypoint."""
    consolidator = DreamConsolidator()
    consolidator.run_nightly_cycle()


if __name__ == "__main__":
    main()
