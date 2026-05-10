#!/usr/bin/env bash
set -euo pipefail

# secret-scan.sh — Unified Secret Scanner Wrapper
#
# Routes secret scanning through the scanner succession:
#   Primary:           Betterleaks (fast, agent-oriented)
#   Fallback:          Gitleaks (legacy compatibility)
#   Deep verification: TruffleHog (full-history forensics)
#
# Usage:
#   scripts/secret-scan.sh staged       # pre-commit / pre-push
#   scripts/secret-scan.sh dir          # working tree scan
#   scripts/secret-scan.sh history      # full-history + TruffleHog verification
#
# Referenced by: push-with-app-gates.sh, tool_contracts/repo.secret_scan.yaml,
#                operator invariant #115

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

MODE="${1:-staged}"
REPORT_DIR=".reports/secrets"
mkdir -p "${REPORT_DIR}"

have() {
  command -v "$1" >/dev/null 2>&1
}

# ── Betterleaks (primary) ────────────────────────────────────────────────────

run_betterleaks_staged() {
  betterleaks git --pre-commit --staged --redact \
    --report-path="${REPORT_DIR}/betterleaks-staged.json" \
    --report-format=json .
}

run_betterleaks_dir() {
  betterleaks dir --redact \
    --report-path="${REPORT_DIR}/betterleaks-dir.json" \
    --report-format=json .
}

run_betterleaks_history() {
  betterleaks git --log-opts="--all" --redact \
    --report-path="${REPORT_DIR}/betterleaks-history.json" \
    --report-format=json .
}

# ── Gitleaks (fallback) ──────────────────────────────────────────────────────

run_gitleaks_staged_fallback() {
  echo "WARN: Betterleaks unavailable; falling back to Gitleaks." >&2
  gitleaks git --redact \
    --report-path="${REPORT_DIR}/gitleaks-staged.json" \
    --report-format=json .
}

run_gitleaks_dir_fallback() {
  echo "WARN: Betterleaks unavailable; falling back to Gitleaks." >&2
  gitleaks dir --redact \
    --report-path="${REPORT_DIR}/gitleaks-dir.json" \
    --report-format=json .
}

run_gitleaks_history_fallback() {
  echo "WARN: Betterleaks unavailable; falling back to Gitleaks." >&2
  gitleaks git --log-opts="--all" --redact \
    --report-path="${REPORT_DIR}/gitleaks-history.json" \
    --report-format=json .
}

# ── Dispatch ─────────────────────────────────────────────────────────────────

case "${MODE}" in
  staged)
    if have betterleaks; then
      run_betterleaks_staged
    elif have gitleaks; then
      run_gitleaks_staged_fallback
    else
      echo "ERROR: neither betterleaks nor gitleaks is installed." >&2
      exit 127
    fi
    ;;

  dir|working-tree|working_tree)
    if have betterleaks; then
      run_betterleaks_dir
    elif have gitleaks; then
      run_gitleaks_dir_fallback
    else
      echo "ERROR: neither betterleaks nor gitleaks is installed." >&2
      exit 127
    fi
    ;;

  history|full-history|full_history)
    if have betterleaks; then
      run_betterleaks_history
    elif have gitleaks; then
      run_gitleaks_history_fallback
    else
      echo "ERROR: neither betterleaks nor gitleaks is installed." >&2
      exit 127
    fi

    # Deep verification layer (TruffleHog)
    if have trufflehog; then
      echo "Running TruffleHog deep verification..."
      trufflehog git file://. --only-verified --json \
        > "${REPORT_DIR}/trufflehog-history.json" || true
    else
      echo "WARN: trufflehog not installed; skipped deep verification." >&2
    fi
    ;;

  *)
    echo "Usage: scripts/secret-scan.sh [staged|dir|history]" >&2
    exit 2
    ;;
esac

echo "Secret scan complete. Reports in ${REPORT_DIR}"
