#!/usr/bin/env bash
# run_ingest_pipeline.sh
# Full pipeline: all ingest sources → corpus → rag_evolve loop
# Usage: bash scripts/run_ingest_pipeline.sh [--skip-drive] [--skip-web]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PY="${REPO}/.venv/bin/python3"
[ -f "$PY" ] || PY="$(which python3)"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Phase 1: Downloads archive extraction
log "Phase 1: Downloads ingest..."
"$PY" "$REPO/scripts/ingest_downloads.py" || log "WARN: ingest_downloads partial"

# Phase 2: Apply rules/control plane overlays
log "Phase 2: Apply ingested rules..."
"$PY" "$REPO/scripts/apply_ingested_rules.py" || log "WARN: apply_rules partial"

# Phase 3a: Web whitepaper ingest (82 PDFs: NIST/DoD/Kaggle/arXiv)
if [[ "${1:-}" != "--skip-web" ]]; then
  log "Phase 3a: Web ingest daemon..."
  "$PY" "$REPO/scripts/web_ingest_daemon.py"
  "$PY" "$REPO/core/rag_evolve.py" --post-ingest web
fi

# Phase 3b: Google Drive ingest (ANE-gated)
if [[ "${1:-}" != "--skip-drive" ]]; then
  log "Phase 3b: Drive ingest runner..."
  "$PY" "$REPO/scripts/drive_ingest_runner.py"
  "$PY" "$REPO/core/rag_evolve.py" --post-ingest drive
fi

# Phase 3c: alphaXiv live arXiv ingest (new)
if [ -f "$REPO/scripts/alphaxiv_ingest_daemon.py" ]; then
  log "Phase 3c: alphaXiv live research ingest..."
  "$PY" "$REPO/scripts/alphaxiv_ingest_daemon.py"
  "$PY" "$REPO/core/rag_evolve.py" --post-ingest alphaxiv
fi

# Phase 4: Legacy threads (MPS/sentence_transformers)
log "Phase 4: Legacy thread ingest (MPS)..."
"$PY" "$REPO/scripts/ingest_legacy_threads_mps.py" || log "WARN: legacy MPS partial"

# Phase 5: ANE Beads classification
log "Phase 5: ANE beads ingest..."
"$PY" "$REPO/scripts/ane_beads_ingest.py" || log "WARN: ANE beads partial"

# Phase 6+7: Final corpus intelligence loop (if any phase wrote new rows)
log "Phase 7: Corpus intelligence loop..."
"$PY" "$REPO/core/rag_evolve.py" --loop

log "Pipeline complete. Reports in artifacts/corpus-intel/"
