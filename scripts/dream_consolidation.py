#!/usr/bin/env python3
"""KAIROS Dream Memory Consolidation Daemon.
=========================================
Implements the enhanced 8-phase Dream protocol for KI system maintenance.
Adapted from Claude Code v2.1.98 + memory-kernel integration.

Phases:
  1. Orient        — Scan KI index, read metadata, map current state
  2. Gather        — Read session logs, identify drifted memories
  2.5 Activate     — Spreading activation for collision detection
  3. Consolidate   — Merge learnings, resolve contradictions, date normalize
  3.5 Promote      — Belief promotion pipeline + conflict detection
  4. Prune         — Enforce size limits, remove orphaned artifacts
  4.5 Measure      — Operational closure metrics + generate views
  5. Gitleaks      — Nightly production secret scan
  6. Archive       — NotebookLM archive

Usage:
  python dream_consolidation.py --ki-dir ~/.gemini/antigravity/knowledge
  python dream_consolidation.py --dry-run  # Preview changes without writing
"""

import contextlib
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# --- KI Engine Integration ---------------------------------------------------
# Falls back gracefully if ki_engine is not available
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.ki_engine.activation import spread_activation
    from core.ki_engine.closure import compute_closure
    from core.ki_engine.decay import rank_kis  # noqa: F811 — used by future phases
    from core.ki_engine.events import EventAction, append_event  # noqa: F811 — used by future phases
    from core.ki_engine.promotion import detect_conflicts, promote_beliefs
    from core.ki_engine.schema import KIMetadata
    from core.ki_engine.views import generate_all_views

    HAS_KI_ENGINE = True
except ImportError:
    HAS_KI_ENGINE = False

# --- Configuration -----------------------------------------------------------

INDEX_MAX_KB = 25
ARTIFACT_MAX_KB = 10
MAX_INDEX_ENTRIES = 200
DRY_RUN = "--dry-run" in sys.argv


# --- Data Models -------------------------------------------------------------


@dataclass
class KIEntry:
    """Represents a single Knowledge Item."""

    name: str
    summary: str
    created_at: str
    updated_at: str
    references: list = field(default_factory=list)
    path: str = ""
    size_kb: float = 0.0
    artifact_count: int = 0


@dataclass
class DreamReport:
    """Tracks all actions taken during a Dream cycle."""

    phase: str = ""
    ki_scanned: int = 0
    contradictions_found: int = 0
    dates_normalized: int = 0
    artifacts_pruned: int = 0
    size_violations: list = field(default_factory=list)
    orphaned_artifacts: list = field(default_factory=list)
    actions: list = field(default_factory=list)


# --- Phase 1: Orient ---------------------------------------------------------


def orient(ki_dir: Path) -> list[KIEntry]:
    """Scan KI directory, read metadata, build inventory."""
    entries = []

    if not ki_dir.exists():
        return entries

    for ki_path in sorted(ki_dir.iterdir()):
        if not ki_path.is_dir():
            continue

        metadata_file = ki_path / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            with open(metadata_file) as f:
                meta = json.load(f)

            artifacts_dir = ki_path / "artifacts"
            artifact_count = 0
            total_size = 0

            if artifacts_dir.exists():
                for artifact in artifacts_dir.iterdir():
                    if artifact.is_file():
                        artifact_count += 1
                        total_size += artifact.stat().st_size

            entry = KIEntry(
                name=meta.get("name", ki_path.name),
                summary=meta.get("summary", ""),
                created_at=meta.get("createdAt", ""),
                updated_at=meta.get("updatedAt", ""),
                references=meta.get("references", []),
                path=str(ki_path),
                size_kb=round(total_size / 1024, 2),
                artifact_count=artifact_count,
            )
            entries.append(entry)

        except (json.JSONDecodeError, KeyError):
            pass

    return entries


# --- Phase 2: Gather ---------------------------------------------------------


def gather(entries: list[KIEntry], report: DreamReport) -> dict:
    """Identify issues: relative dates, size violations, contradictions."""
    issues = {
        "relative_dates": [],
        "size_violations": [],
        "stale_entries": [],
        "orphaned": [],
    }

    relative_date_patterns = [
        "yesterday",
        "today",
        "last week",
        "last month",
        "this morning",
        "earlier",
        "recently",
        "a few days ago",
        "last night",
        "this week",
        "next week",
    ]

    now = datetime.now(UTC)

    for entry in entries:
        # Check for relative dates in summaries
        summary_lower = entry.summary.lower()
        for pattern in relative_date_patterns:
            if pattern in summary_lower:
                issues["relative_dates"].append(
                    {
                        "ki": entry.name,
                        "pattern": pattern,
                        "path": entry.path,
                    },
                )
                report.dates_normalized += 1

        # Check size limits
        if entry.size_kb > ARTIFACT_MAX_KB:
            issues["size_violations"].append(
                {
                    "ki": entry.name,
                    "size_kb": entry.size_kb,
                    "limit_kb": ARTIFACT_MAX_KB,
                },
            )
            report.size_violations.append(entry.name)

        # Check for stale entries (>30 days since last update)
        if entry.updated_at:
            try:
                updated = datetime.fromisoformat(entry.updated_at)
                age_days = (now - updated).days
                if age_days > 30:
                    issues["stale_entries"].append(
                        {
                            "ki": entry.name,
                            "age_days": age_days,
                            "updated_at": entry.updated_at,
                        },
                    )
            except (ValueError, TypeError):
                pass

    report.ki_scanned = len(entries)

    return issues


# --- Phase 3: Consolidate ----------------------------------------------------


def consolidate(entries: list[KIEntry], issues: dict, report: DreamReport) -> None:
    """Resolve contradictions, normalize dates, merge duplicates."""
    # Check for potential contradictions (same topic, different claims)
    names_seen = {}
    for entry in entries:
        # Extract key tokens from name
        tokens = set(entry.name.lower().split())
        for prev_name, prev_tokens in names_seen.items():
            overlap = tokens & prev_tokens
            if len(overlap) >= 3:  # Significant overlap
                report.contradictions_found += 1
                report.actions.append(f"POTENTIAL CONTRADICTION: '{entry.name}' may overlap with '{prev_name}' (shared tokens: {overlap})")
        names_seen[entry.name] = tokens

    # Report relative dates that need manual conversion
    for rd in issues["relative_dates"]:
        report.actions.append(f"RELATIVE DATE: '{rd['pattern']}' found in '{rd['ki']}' — convert to absolute ISO-8601 date")


# --- Phase 4: Prune ----------------------------------------------------------


def prune(entries: list[KIEntry], issues: dict, report: DreamReport) -> None:
    """Enforce size limits, remove orphans, trim index."""
    # Report size violations
    for sv in issues["size_violations"]:
        report.actions.append(f"SIZE VIOLATION: '{sv['ki']}' is {sv['size_kb']}KB (limit: {sv['limit_kb']}KB) — consider splitting")

    # Check for orphaned artifacts (artifacts dir but no metadata reference)
    for entry in entries:
        artifacts_dir = Path(entry.path) / "artifacts"
        if not artifacts_dir.exists():
            continue

        # Get referenced artifact paths
        referenced_paths = set()
        for ref in entry.references:
            if isinstance(ref, dict) and ref.get("type") == "file":
                referenced_paths.add(ref.get("path", ""))

        # Check for unreferenced artifacts
        for artifact in artifacts_dir.iterdir():
            if artifact.is_file():
                rel_path = str(artifact.relative_to(Path(entry.path).parent))
                if rel_path not in referenced_paths and artifact.name != ".gitkeep":
                    report.orphaned_artifacts.append(str(artifact))
                    report.artifacts_pruned += 1

    # Index size check
    total_summary_kb = sum(len(e.summary.encode()) / 1024 for e in entries)
    if total_summary_kb > INDEX_MAX_KB:
        report.actions.append(f"INDEX SIZE: Total summaries are {total_summary_kb:.1f}KB (limit: {INDEX_MAX_KB}KB) — prune oldest entries")

    if len(entries) > MAX_INDEX_ENTRIES:
        report.actions.append(f"INDEX COUNT: {len(entries)} entries (limit: {MAX_INDEX_ENTRIES}) — archive oldest")


# --- Phase 2.5: Activate (memory-kernel integration) -------------------------


def activate(entries: list[KIEntry], ki_dir: Path, report: DreamReport) -> None:
    """Run spreading activation for collision detection."""
    if not HAS_KI_ENGINE:
        return

    # Load enhanced metadata
    ki_metas = []
    for entry in entries:
        metadata_file = Path(entry.path) / "metadata.json"
        if metadata_file.exists():
            with contextlib.suppress(json.JSONDecodeError, OSError):
                ki_metas.append(KIMetadata.load(metadata_file))

    if not ki_metas:
        return

    # Collect all tags for seeding
    all_tags = set()
    for ki in ki_metas:
        all_tags.update(ki.tags)

    # Run activation with top 5 most common tags as seeds
    from collections import Counter

    tag_counts = Counter()
    for ki in ki_metas:
        tag_counts.update(ki.tags)
    seed_tags = {tag for tag, _ in tag_counts.most_common(5)}

    result = spread_activation(ki_metas, seed_tags=seed_tags, steps=2)

    if result.collisions:
        for collision in result.collisions[:5]:
            report.actions.append(f"COLLISION: {collision.description}")
    else:
        pass


# --- Phase 3.5: Promote + Detect Conflicts -----------------------------------


def promote_and_detect(entries: list[KIEntry], ki_dir: Path, report: DreamReport) -> None:
    """Run belief promotion and conflict detection."""
    if not HAS_KI_ENGINE:
        return

    ki_metas = []
    for entry in entries:
        metadata_file = Path(entry.path) / "metadata.json"
        if metadata_file.exists():
            with contextlib.suppress(json.JSONDecodeError, OSError):
                ki_metas.append(KIMetadata.load(metadata_file))

    # Promotion pipeline
    promo_result = promote_beliefs(ki_metas, ki_dir=ki_dir, dry_run=DRY_RUN)
    if promo_result.promoted:
        for name in promo_result.promoted:
            report.actions.append(f"PROMOTED: '{name}' belief → fact (confidence ≥ 0.9)")

    # Conflict detection
    conflict_result = detect_conflicts(ki_metas)
    if conflict_result.detected:
        for c in conflict_result.detected:
            report.actions.append(f"CONFLICT: {c.ki_a} ↔ {c.ki_b}: {c.reason}")
            report.contradictions_found += 1


# --- Phase 4.5: Closure Metrics + Views --------------------------------------


def measure_and_render(entries: list[KIEntry], ki_dir: Path, report: DreamReport) -> None:
    """Compute closure metrics and generate views."""
    if not HAS_KI_ENGINE:
        return

    ki_metas = []
    for entry in entries:
        metadata_file = Path(entry.path) / "metadata.json"
        if metadata_file.exists():
            with contextlib.suppress(json.JSONDecodeError, OSError):
                ki_metas.append(KIMetadata.load(metadata_file))

    # Closure metrics
    closure = compute_closure(ki_metas, ki_dir=ki_dir)
    for pred in closure.predictions:
        if pred.status == "degraded":
            report.actions.append(f"CLOSURE WARNING: {pred.tool} — {pred.detail}")

    # Generate views
    if not DRY_RUN:
        views_dir = ki_dir / "_views"
        generate_all_views(ki_metas, views_dir)
    else:
        pass


# --- Main --------------------------------------------------------------------


def run_dream_cycle(ki_dir: Path) -> DreamReport:
    """Execute the full enhanced Dream consolidation cycle."""
    report = DreamReport()

    # Phase 1: Orient
    report.phase = "orient"
    entries = orient(ki_dir)

    # Phase 2: Gather
    report.phase = "gather"
    issues = gather(entries, report)

    # Phase 2.5: Activate (spreading activation for collision detection)
    report.phase = "activate"
    activate(entries, ki_dir, report)

    # Phase 3: Consolidate
    report.phase = "consolidate"
    consolidate(entries, issues, report)

    # Phase 3.5: Promote + Detect
    report.phase = "promote"
    promote_and_detect(entries, ki_dir, report)

    # Phase 4: Prune
    report.phase = "prune"
    prune(entries, issues, report)

    # Phase 4.5: Measure + Views
    report.phase = "measure"
    measure_and_render(entries, ki_dir, report)

    # Report
    report.phase = "complete"

    if report.actions:
        for _i, _action in enumerate(report.actions, 1):
            pass

    return report


if __name__ == "__main__":
    ki_dir = Path(
        os.environ.get(
            "KI_DIR",
            os.path.expanduser("~/.gemini/antigravity/knowledge"),
        ),
    )

    if len(sys.argv) > 1 and sys.argv[1] not in ("--dry-run", "--migrate"):
        ki_dir = Path(sys.argv[1])

    # Optional: run migration first
    if "--migrate" in sys.argv:
        from core.ki_engine.migration import migrate_ki_metadata

        mig_result = migrate_ki_metadata(ki_dir, dry_run=DRY_RUN)

    report = run_dream_cycle(ki_dir)

    # Phase 5a: Rebuild FTS5 search index
    if DRY_RUN:
        pass
    else:
        try:
            from core.ki_engine.fts_index import reindex_all

            fts_count = reindex_all(ki_dir)
        except Exception as e:
            report.actions.append(f"FTS5: Reindex failed — {e}")

    # Phase 5b: Gitleaks nightly production scan
    repo_root = Path(__file__).resolve().parent.parent
    guardian_script = repo_root / "scripts" / "gitleaks_guardian.py"
    if guardian_script.exists():
        import subprocess as _sp

        gl_report = repo_root / ".beads" / f"gitleaks_nightly_{datetime.now(UTC).strftime('%Y%m%d')}.md"
        cmd = [
            sys.executable,
            str(guardian_script),
            "--mode",
            "scan",
            "--scope",
            "production",
            "--output",
            str(gl_report),
        ]
        if DRY_RUN:
            pass
        else:
            result = _sp.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                pass
            else:
                if result.stdout:
                    pass
                report.actions.append(f"GITLEAKS: Production scan found issues — review {gl_report}")
    else:
        pass

    # Phase 6: Archive to NotebookLM Master Brain (if available)
    try:
        from notebooklm import NotebookLM  # noqa: F401 — used conditionally for archive

        # Master Brain ID from session config
        master_brain_id = os.environ.get(
            "NOTEBOOKLM_BRAIN_ID",
            "default",
        )
        report_text = (
            f"# Dream Consolidation Report — {datetime.now(UTC).isoformat()}\n"
            f"KIs scanned: {report.ki_scanned}\n"
            f"Contradictions: {report.contradictions_found}\n"
            f"Dates to normalize: {report.dates_normalized}\n"
            f"Size violations: {len(report.size_violations)}\n"
            f"Orphaned artifacts: {report.artifacts_pruned}\n"
            f"Actions: {len(report.actions)}\n"
        )
        if not DRY_RUN:
            pass
            # NotebookLM upload would happen here when API is live
        else:
            pass
    except ImportError:
        pass

    # Exit with error if critical issues found
    if report.contradictions_found > 3 or len(report.size_violations) > 5:
        sys.exit(1)
    sys.exit(0)
