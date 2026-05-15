#!/usr/bin/env bash
set -euo pipefail

# clone-nextwave-reference-repos.sh
#
# Reference-only clone script for Monorepo OS v3.1/v3.5 hardening.
#
# Usage:
#   scripts/clone-nextwave-reference-repos.sh --dry-run
#   scripts/clone-nextwave-reference-repos.sh --group ci_proof
#   scripts/clone-nextwave-reference-repos.sh --all
#   UPDATE=1 scripts/clone-nextwave-reference-repos.sh --all
#
# Policy:
#   - Clone into external_repos/upstream only.
#   - Never vendor these repos into product source.
#   - Never GitNexus-index external_repos by default.
#   - Any transplant requires Beads issue, license review, ToolGateway approval,
#     tests, and evidence.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

DEST="${DEST:-${ROOT}/external_repos/upstream}"
REPORT_DIR="${ROOT}/.reports/external_repos"
LOG_FILE="${REPORT_DIR}/nextwave-clone-log.tsv"
FRAGMENT="${REPORT_DIR}/nextwave_manifest_fragment.yaml"

MODE="all"
DRY_RUN="${DRY_RUN:-0}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --all)
      MODE="all"
      shift
      ;;
    --group)
      MODE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: $0 [--dry-run] [--all] [--group <name>]" >&2
      exit 2
      ;;
  esac
done

mkdir -p "${DEST}" "${REPORT_DIR}"
touch "${LOG_FILE}"

record() {
  local status="$1"
  local group="$2"
  local repo="$3"
  local target="$4"
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${status}" "${group}" "${repo}" "${target}" >> "${LOG_FILE}"
}

repo_exists_remote() {
  local repo="$1"
  git ls-remote --exit-code "https://github.com/${repo}.git" HEAD >/dev/null 2>&1
}

default_branch_for() {
  local repo="$1"
  git ls-remote --symref "https://github.com/${repo}.git" HEAD 2>/dev/null \
    | awk '/^ref:/ {sub("refs/heads/","",$2); print $2; exit}'
}

clone_repo() {
  local group="$1"
  local repo="$2"
  local org name target branch status

  org="${repo%%/*}"
  name="${repo##*/}"
  target="${DEST}/${group}/${org}/${name}"

  if [ "${DRY_RUN}" = "1" ]; then
    echo "[DRY] ${group}: ${repo} -> ${target}"
    record "dry-run" "${group}" "${repo}" "${target}"
    return 0
  fi

  if ! repo_exists_remote "${repo}"; then
    echo "WARN: remote not found: ${repo}" >&2
    record "missing-remote" "${group}" "${repo}" "${target}"
    return 0
  fi

  mkdir -p "$(dirname "${target}")"

  if [ -d "${target}/.git" ]; then
    echo "== Exists: ${repo}"
    if [ "${UPDATE:-0}" = "1" ]; then
      git -C "${target}" fetch --depth=1 origin >/dev/null 2>&1 || true
      record "updated" "${group}" "${repo}" "${target}"
    else
      record "exists" "${group}" "${repo}" "${target}"
    fi
    return 0
  fi

  branch="$(default_branch_for "${repo}" || true)"

  echo "== Cloning ${repo}"
  set +e
  if [ -n "${branch}" ]; then
    git clone \
      --depth=1 \
      --filter=blob:none \
      --single-branch \
      --branch "${branch}" \
      "https://github.com/${repo}.git" \
      "${target}"
  else
    git clone \
      --depth=1 \
      --filter=blob:none \
      --single-branch \
      "https://github.com/${repo}.git" \
      "${target}"
  fi
  status="$?"
  set -e

  if [ "${status}" -eq 0 ]; then
    record "cloned" "${group}" "${repo}" "${target}"
  else
    echo "WARN: failed to clone ${repo}" >&2
    record "failed" "${group}" "${repo}" "${target}"
  fi
}

clone_list() {
  local group="$1"
  shift
  local repo
  for repo in "$@"; do
    clone_repo "${group}" "${repo}"
  done
}

write_fragment() {
  cat > "${FRAGMENT}" <<'YAML'
# Next-wave reference repos for Monorepo OS v3.1/v3.5.
# Copy groups into external_repos/upstream_manifest.yaml only after review.
# These repos are reference/evaluation only.

policy:
  destination: external_repos/upstream
  clone_depth: 1
  canonical_source: false
  git_tracked: false
  transplant_requires:
    - beads_issue
    - license_review
    - toolgateway_approval
    - tests
    - evidence

groups:
  ci_proof:
    - rhysd/actionlint
    - zizmorcore/zizmor
    - step-security/harden-runner
    - reviewdog/reviewdog

  policy_contracts:
    - open-policy-agent/opa
    - open-policy-agent/conftest

  supply_chain:
    - ossf/scorecard
    - slsa-framework/slsa-github-generator
    - sigstore/cosign
    - anchore/syft
    - anchore/grype
    - google/osv-scanner
    - trufflesecurity/trufflehog

  static_analysis:
    - semgrep/semgrep
    - semgrep/semgrep-rules
    - ast-grep/ast-grep
    - github/codeql-action
    - openrewrite/rewrite

  iac_security:
    - bridgecrewio/checkov
    - terraform-linters/tflint

  dependency_automation:
    - renovatebot/renovate
    - renovatebot/github-action

  mcp_runtime:
    - modelcontextprotocol/python-sdk
    - modelcontextprotocol/typescript-sdk
    - modelcontextprotocol/conformance
YAML
}

# ── Group arrays ──────────────────────────────────────────────────────

CI_PROOF_REPOS=(
  rhysd/actionlint
  zizmorcore/zizmor
  step-security/harden-runner
  reviewdog/reviewdog
)

POLICY_CONTRACT_REPOS=(
  open-policy-agent/opa
  open-policy-agent/conftest
)

SUPPLY_CHAIN_REPOS=(
  ossf/scorecard
  slsa-framework/slsa-github-generator
  sigstore/cosign
  anchore/syft
  anchore/grype
  google/osv-scanner
  trufflesecurity/trufflehog
)

STATIC_ANALYSIS_REPOS=(
  semgrep/semgrep
  semgrep/semgrep-rules
  ast-grep/ast-grep
  github/codeql-action
  openrewrite/rewrite
)

IAC_SECURITY_REPOS=(
  bridgecrewio/checkov
  terraform-linters/tflint
)

DEPENDENCY_AUTOMATION_REPOS=(
  renovatebot/renovate
  renovatebot/github-action
)

MCP_RUNTIME_REPOS=(
  modelcontextprotocol/python-sdk
  modelcontextprotocol/typescript-sdk
  modelcontextprotocol/conformance
)

# ── Execute ───────────────────────────────────────────────────────────

write_fragment

case "${MODE}" in
  all)
    clone_list ci_proof "${CI_PROOF_REPOS[@]}"
    clone_list policy_contracts "${POLICY_CONTRACT_REPOS[@]}"
    clone_list supply_chain "${SUPPLY_CHAIN_REPOS[@]}"
    clone_list static_analysis "${STATIC_ANALYSIS_REPOS[@]}"
    clone_list iac_security "${IAC_SECURITY_REPOS[@]}"
    clone_list dependency_automation "${DEPENDENCY_AUTOMATION_REPOS[@]}"
    clone_list mcp_runtime "${MCP_RUNTIME_REPOS[@]}"
    ;;
  ci_proof)
    clone_list ci_proof "${CI_PROOF_REPOS[@]}"
    ;;
  policy_contracts)
    clone_list policy_contracts "${POLICY_CONTRACT_REPOS[@]}"
    ;;
  supply_chain)
    clone_list supply_chain "${SUPPLY_CHAIN_REPOS[@]}"
    ;;
  static_analysis)
    clone_list static_analysis "${STATIC_ANALYSIS_REPOS[@]}"
    ;;
  iac_security)
    clone_list iac_security "${IAC_SECURITY_REPOS[@]}"
    ;;
  dependency_automation)
    clone_list dependency_automation "${DEPENDENCY_AUTOMATION_REPOS[@]}"
    ;;
  mcp_runtime)
    clone_list mcp_runtime "${MCP_RUNTIME_REPOS[@]}"
    ;;
  *)
    echo "Unknown group: ${MODE}" >&2
    exit 2
    ;;
esac

echo
echo "Clone log: ${LOG_FILE}"
echo "Manifest fragment: ${FRAGMENT}"
echo "Done."
