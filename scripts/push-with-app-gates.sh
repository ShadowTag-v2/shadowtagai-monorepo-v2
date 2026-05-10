#!/usr/bin/env bash
set -euo pipefail

# push-with-app-gates.sh
#
# Governed GitHub push path for the Monorepo Operating System.
#
# This script is intentionally conservative:
# - It does not bypass GitHub file-size limits.
# - It does not bypass Git LFS budget limits.
# - It does not print or persist GitHub App installation tokens.
# - It runs source/artifact, secret, bloat, Buildifier, optional Bazel, and
#   remote-head checks before invoking scripts/auth_github_app.py.
#
# Usage:
#   scripts/push-with-app-gates.sh
#
# Environment:
#   REMOTE=origin
#   BRANCH=main
#   AUTH_PUSH_CMD="python scripts/auth_github_app.py --push"
#   SKIP_FORMAT=1
#   SKIP_SECRET_SCAN=1
#   SKIP_BAZEL_QUERY=1
#   ALLOW_DIRTY=1
#
# Referenced by: operator invariant #105, #106, tool_contracts/github_push.yaml

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
AUTH_PUSH_CMD="${AUTH_PUSH_CMD:-python scripts/auth_github_app.py --push}"

EVIDENCE_DIR=".agent/evidence/push"
REPORT_DIR=".reports"
BAZEL_REPORT_DIR="${REPORT_DIR}/bazel"
PUSH_TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_FILE="${EVIDENCE_DIR}/${PUSH_TS}-push.json"

mkdir -p "${EVIDENCE_DIR}" "${BAZEL_REPORT_DIR}" "${REPORT_DIR}/secrets"

log() {
  printf '\n== %s ==\n' "$*"
}

run_optional() {
  local desc="$1"
  shift

  log "${desc}"
  if "$@"; then
    echo "OK: ${desc}"
  else
    echo "WARN: ${desc} failed or unavailable."
    return 0
  fi
}

require_file() {
  local path="$1"
  if [ ! -f "${path}" ]; then
    echo "ERROR: required file missing: ${path}" >&2
    exit 1
  fi
}

# ── Phase 1: State ──────────────────────────────────────────────────────────

log "Push gate: state"
echo "root=${ROOT}"
echo "remote=${REMOTE}"
echo "branch=${BRANCH}"

git rev-parse --is-inside-work-tree >/dev/null

HEAD_BEFORE="$(git rev-parse HEAD)"
CURRENT_BRANCH="$(git branch --show-current || true)"

if [ "${CURRENT_BRANCH}" != "${BRANCH}" ]; then
  echo "WARN: current branch '${CURRENT_BRANCH}' differs from target branch '${BRANCH}'."
fi

log "Fetch remote"
git fetch "${REMOTE}" "${BRANCH}" --prune

REMOTE_HEAD_BEFORE="$(git rev-parse "${REMOTE}/${BRANCH}")"

log "Git status before"
git status --short

log "Outgoing commits"
git log --oneline --decorate "${REMOTE}/${BRANCH}..HEAD" || true

log "Changed files against remote"
CHANGED_FILES="$(git diff --name-only "${REMOTE}/${BRANCH}...HEAD" || true)"
if [ -n "${CHANGED_FILES}" ]; then
  echo "${CHANGED_FILES}"
else
  echo "No committed changes ahead of ${REMOTE}/${BRANCH}."
fi

# ── Phase 2: Required gate files ────────────────────────────────────────────

log "Required gate files"
require_file "scripts/prepush-bloat-gate.sh"

if [ ! -f "scripts/classify-upload-payload.sh" ]; then
  echo "WARN: scripts/classify-upload-payload.sh missing; falling back to built-in checks."
fi

if [ ! -f "scripts/check-buildifier.sh" ]; then
  echo "WARN: scripts/check-buildifier.sh missing; Buildifier gate will be skipped unless Bazel files changed and buildifier is available."
fi

if [ ! -f "scripts/auth_github_app.py" ]; then
  echo "ERROR: scripts/auth_github_app.py missing. Cannot push via GitHub App token." >&2
  exit 1
fi

# ── Phase 3: Forbidden tracked paths ────────────────────────────────────────

log "Forbidden tracked paths"
FORBIDDEN_TRACKED="$(
  {
    git ls-files archive 2>/dev/null || true
    git ls-files external_repos 2>/dev/null || true
    git ls-files external_sdks 2>/dev/null || true
    git ls-files reference_architectures/raw 2>/dev/null || true
    git ls-files third_party/raw 2>/dev/null || true
    git ls-files venv 2>/dev/null || true
    git ls-files .venv 2>/dev/null || true
    git ls-files .gitnexus 2>/dev/null || true
    git ls-files .mypy_cache 2>/dev/null || true
    git ls-files .ruff_cache 2>/dev/null || true
    git ls-files node_modules 2>/dev/null || true
  } | sort -u
)"

if [ -n "${FORBIDDEN_TRACKED}" ]; then
  echo "${FORBIDDEN_TRACKED}"
  echo "ERROR: forbidden local/artifact paths are tracked. Remove with git rm --cached before pushing." >&2
  exit 1
fi

echo "No forbidden tracked paths detected."

# ── Phase 4: Secret-bearing tracked files ────────────────────────────────────

log "Secret-bearing tracked files"
SECRET_TRACKED="$(
  git ls-files \
    '.env' '.env.*' '*.pem' '*.key' 'client_secret*.json' '*service-account*.json' \
    2>/dev/null || true
)"

if [ -n "${SECRET_TRACKED}" ]; then
  echo "${SECRET_TRACKED}"
  echo "ERROR: potential secret-bearing files are tracked." >&2
  exit 1
fi

echo "No obvious secret-bearing tracked files detected."

# ── Phase 5: File size gates ────────────────────────────────────────────────

log "Tracked files over 95 MiB (hard block — GitHub blocks >100 MiB)"
TRACKED_OVER_95="$(
  git ls-files -z \
    | xargs -0 -I{} find "{}" -type f -size +95M -print 2>/dev/null \
    | sort || true
)"

if [ -n "${TRACKED_OVER_95}" ]; then
  echo "${TRACKED_OVER_95}"
  echo "ERROR: tracked files over 95 MiB. GitHub blocks regular Git files over 100 MiB." >&2
  exit 1
fi

echo "No tracked files over 95 MiB."

log "Tracked files over 50 MiB (warning — GitHub warns >50 MiB)"
TRACKED_OVER_50="$(
  git ls-files -z \
    | xargs -0 -I{} find "{}" -type f -size +50M -print 2>/dev/null \
    | sort || true
)"

if [ -n "${TRACKED_OVER_50}" ]; then
  echo "${TRACKED_OVER_50}"
  echo "WARN: tracked files over 50 MiB may trigger GitHub warnings."
else
  echo "No tracked files over 50 MiB."
fi

# ── Phase 6: Upload payload classification ───────────────────────────────────

if [ -f "scripts/classify-upload-payload.sh" ]; then
  run_optional "Upload payload classification" bash scripts/classify-upload-payload.sh
fi

# ── Phase 7: Pre-push bloat gate ─────────────────────────────────────────────

log "Pre-push bloat gate"
bash scripts/prepush-bloat-gate.sh

# ── Phase 8: Buildifier / Bazel format gate ──────────────────────────────────

BAZEL_CHANGED="$(
  printf '%s\n' "${CHANGED_FILES}" \
    | grep -E '(^|/)(BUILD|BUILD\.bazel|WORKSPACE|WORKSPACE\.bazel|MODULE\.bazel|.*\.bzl)$' || true
)"

if [ -n "${BAZEL_CHANGED}" ] && [ -z "${SKIP_FORMAT:-}" ]; then
  log "Bazel/Starlark files changed"
  echo "${BAZEL_CHANGED}"

  if [ -x "scripts/format-buildifier.sh" ]; then
    bash scripts/format-buildifier.sh
  fi

  if [ -x "scripts/check-buildifier.sh" ]; then
    bash scripts/check-buildifier.sh
  elif command -v buildifier >/dev/null 2>&1; then
    echo "${BAZEL_CHANGED}" | xargs buildifier -mode=check
  else
    echo "ERROR: Bazel/Starlark files changed but no Buildifier gate available." >&2
    exit 1
  fi
else
  log "Buildifier gate"
  if [ -n "${SKIP_FORMAT:-}" ]; then
    echo "Skipped by SKIP_FORMAT=1."
  else
    echo "No Bazel/Starlark changes detected."
  fi
fi

# ── Phase 9: Secret scan (Betterleaks primary → Gitleaks fallback) ───────────

log "Secret scan"
if [ -n "${SKIP_SECRET_SCAN:-}" ]; then
  echo "Skipped by SKIP_SECRET_SCAN=1."
else
  if [ -x "scripts/secret-scan.sh" ]; then
    bash scripts/secret-scan.sh staged
    bash scripts/secret-scan.sh dir
  else
    # Direct fallback if wrapper is missing
    if command -v betterleaks >/dev/null 2>&1; then
      betterleaks scan . || true
    elif command -v gitleaks >/dev/null 2>&1; then
      gitleaks protect --staged || true
    else
      echo "WARN: no secret scanner found."
    fi
  fi
fi

# ── Phase 10: LFS status ────────────────────────────────────────────────────

log "LFS status"
git lfs status 2>/dev/null || true
git lfs ls-files 2>/dev/null || true

if git lfs status 2>&1 | grep -qi 'budget\|quota\|exceeded'; then
  echo "ERROR: possible LFS budget/quota failure detected." >&2
  exit 1
fi

# ── Phase 11: Optional Bazel index/build graph check ─────────────────────────

log "Optional Bazel index/build graph check"
if [ -n "${SKIP_BAZEL_QUERY:-}" ]; then
  echo "Skipped by SKIP_BAZEL_QUERY=1."
elif command -v bazel >/dev/null 2>&1; then
  {
    bazel query //packages/... || true
    bazel query //libs/... || true
    bazel query //tools/... || true
  } > "${BAZEL_REPORT_DIR}/${PUSH_TS}-query.txt" 2>&1
  echo "Wrote ${BAZEL_REPORT_DIR}/${PUSH_TS}-query.txt"
else
  echo "WARN: bazel not found."
fi

# ── Phase 12: Remote head re-check (race detection) ─────────────────────────

log "Remote head re-check before push"
git fetch "${REMOTE}" "${BRANCH}" --prune
REMOTE_HEAD_NOW="$(git rev-parse "${REMOTE}/${BRANCH}")"

if [ "${REMOTE_HEAD_NOW}" != "${REMOTE_HEAD_BEFORE}" ]; then
  echo "ERROR: remote head changed during preflight." >&2
  echo "before=${REMOTE_HEAD_BEFORE}" >&2
  echo "now=${REMOTE_HEAD_NOW}" >&2
  exit 1
fi

# ── Phase 13: Push via GitHub App token wrapper ──────────────────────────────

log "Push via GitHub App token wrapper"
# shellcheck disable=SC2086
${AUTH_PUSH_CMD}

# ── Phase 14: Verify remote after push ───────────────────────────────────────

log "Verify remote after push"
git fetch "${REMOTE}" "${BRANCH}" --prune
REMOTE_HEAD_AFTER="$(git rev-parse "${REMOTE}/${BRANCH}")"
REMAINING="$(git log --oneline "${REMOTE}/${BRANCH}..HEAD" || true)"
STATUS_AFTER="$(git status --short || true)"

if [ -n "${REMAINING}" ]; then
  echo "ERROR: unpushed commits remain after push:"
  echo "${REMAINING}"
  PUSH_RESULT="incomplete"
else
  echo "All commits pushed."
  PUSH_RESULT="pushed"
fi

# ── Phase 15: Write evidence packet ─────────────────────────────────────────

log "Write evidence"
python3 - <<PY
import json
import pathlib
import subprocess
import datetime

def run(cmd: str) -> str:
    return subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

payload = {
    "type": "github.push",
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "remote": "${REMOTE}",
    "branch": "${BRANCH}",
    "head_before": "${HEAD_BEFORE}",
    "head_after": run("git rev-parse HEAD"),
    "remote_head_before": "${REMOTE_HEAD_BEFORE}",
    "remote_head_after": "${REMOTE_HEAD_AFTER}",
    "result": "${PUSH_RESULT}",
    "remaining_unpushed": """${REMAINING}""",
    "status_after": """${STATUS_AFTER}""",
    "changed_files_against_remote_before": """${CHANGED_FILES}""",
    "tracked_over_50_mib": """${TRACKED_OVER_50}""".splitlines() if """${TRACKED_OVER_50}""" else [],
    "tracked_over_95_mib": """${TRACKED_OVER_95}""".splitlines() if """${TRACKED_OVER_95}""" else [],
    "forbidden_tracked": """${FORBIDDEN_TRACKED}""".splitlines() if """${FORBIDDEN_TRACKED}""" else [],
    "secret_tracked": """${SECRET_TRACKED}""".splitlines() if """${SECRET_TRACKED}""" else [],
    "auth": {
        "method": "github_app_installation_token",
        "token_printed": False,
        "token_persisted": False
    },
    "reports": {
        "bazel_query": "${BAZEL_REPORT_DIR}/${PUSH_TS}-query.txt"
    }
}

path = pathlib.Path("${EVIDENCE_FILE}")
path.write_text(json.dumps(payload, indent=2, sort_keys=True))
print(path)
PY

echo "Evidence: ${EVIDENCE_FILE}"

if [ "${PUSH_RESULT}" != "pushed" ]; then
  exit 1
fi

echo "Push gate complete."
