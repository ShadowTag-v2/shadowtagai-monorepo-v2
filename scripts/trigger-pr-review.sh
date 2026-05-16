#!/usr/bin/env bash
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# trigger-pr-review.sh — Multi-agent PR review swarm trigger.
# Usage: ./scripts/trigger-pr-review.sh <PR_NUMBER>
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly SWARM_TIMEOUT="${SWARM_TIMEOUT:-600}"
readonly OWNER="ShadowTag-v2"
readonly REPO="shadowtagai-monorepo-v2"
readonly API="https://api.github.com/repos/${OWNER}/${REPO}"

log()  { printf '%s [PR-REVIEW] %s\n' "$(date +%Y-%m-%dT%H:%M:%S)" "$*"; }
die()  { log "FATAL: $*" >&2; exit 1; }

ensure_token() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then return 0; fi
  if [[ -f "${SCRIPT_DIR}/auth_github_app.py" ]]; then
    GITHUB_TOKEN="$(python3 "${SCRIPT_DIR}/auth_github_app.py" 2>/dev/null)" \
      || die "Token generation failed"
    export GITHUB_TOKEN
  else
    die "No GITHUB_TOKEN and no auth_github_app.py"
  fi
}

resolve_pr() {
  local num="${1:-}"
  if [[ -n "${num}" ]]; then echo "${num}"; return; fi
  if [[ -f "${GITHUB_EVENT_PATH:-/dev/null}" ]]; then
    num=$(python3 -c "
import json; f=open('${GITHUB_EVENT_PATH}')
e=json.load(f); print(e.get('pull_request',{}).get('number',''))" 2>/dev/null)
    if [[ -n "${num}" ]]; then echo "${num}"; return; fi
  fi
  local br; br=$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null)
  if [[ -n "${br}" && "${br}" != "main" ]]; then
    num=$(curl -sf -H "Authorization: token ${GITHUB_TOKEN}" \
      "${API}/pulls?head=${OWNER}:${br}&state=open" \
      | python3 -c "import json,sys;p=json.load(sys.stdin);print(p[0]['number'] if p else '')" 2>/dev/null)
    [[ -n "${num}" ]] && { echo "${num}"; return; }
  fi
  die "Pass PR number: $0 <PR_NUMBER>"
}

post_comment() {
  curl -sf -X POST -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    "${API}/issues/$1/comments" \
    -d "{\"body\":$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$2")}" >/dev/null || true
}

main() {
  log "=== PR Review Swarm — Starting ==="
  ensure_token
  local pr; pr=$(resolve_pr "${1:-}")
  log "Targeting PR #${pr}"
  export PR_NUMBER="${pr}"

  local result="/tmp/swarm_result_$$.json"
  if timeout "${SWARM_TIMEOUT}" python3 "${SCRIPT_DIR}/run_swarm.py" \
    --pr-number "${pr}" --output "${result}" \
    ${SKIP_ANE:+--skip-ane} ${SKIP_COLAB:+--skip-colab}; then
    log "Swarm completed"
    if [[ -f "${result}" ]]; then
      local summary
      summary=$(python3 -c "import json;print(json.load(open('${result}')).get('summary','No summary.'))")
      post_comment "${pr}" "${summary}"
      log "Review posted to PR #${pr}"
    fi
  else
    post_comment "${pr}" "⚠️ PR Review Swarm failed (exit $?). Check CI logs."
  fi
  rm -f "${result}" 2>/dev/null || true
  log "=== PR Review Swarm — Complete ==="
}

main "$@"
