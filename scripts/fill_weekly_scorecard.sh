#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT="${ROOT}/docs/monorepo-weekly-scorecard.generated.md"
DATE_STR="${1:-$(date +%F)}"

cd "${ROOT}"

count_unresolved() {
  if [ -f monorepo_manifest.yaml ]; then
    grep -c "status: unresolved" monorepo_manifest.yaml || true
  else
    echo 999
  fi
}

path_present() {
  [ -e "$1" ] && echo yes || echo no
}

count_denied_dirs() {
  find apps libs -type d \( \
    -name "_PRE_OMEGA_BACKUP_*" -o \
    -name "ShadowTag-Omega" -o \
    -name "arsenal_recovered" -o \
    -name "*-legacy" \
  \) 2>/dev/null | wc -l | tr -d ' '
}

workflow_has_job() {
  local job="$1"
  if [ -f .github/workflows/main.yml ] && grep -q "^  ${job}:" .github/workflows/main.yml; then
    echo yes
  else
    echo no
  fi
}

file_present() {
  [ -f "$1" ] && echo yes || echo no
}

python_count() {
  find "$1" -type f -name '*.py' 2>/dev/null | wc -l | tr -d ' '
}

build_count() {
  find . -type f -name 'BUILD.bazel' 2>/dev/null | wc -l | tr -d ' '
}

proto_count() {
  find contracts proto -type f -name '*.proto' 2>/dev/null | wc -l | tr -d ' '
}

NODE_PRESENT=no
NPM_PRESENT=no
CHROME_PRESENT=no
CHROME_MCP_PRESENT=no
TOKEN_PRESENT=no

command -v node >/dev/null 2>&1 && NODE_PRESENT=yes
command -v npm >/dev/null 2>&1 && NPM_PRESENT=yes
[ -d "/Applications/Google Chrome.app" ] && CHROME_PRESENT=yes
if command -v npx >/dev/null 2>&1 && npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1; then
  CHROME_MCP_PRESENT=yes
fi
[ -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" ] && TOKEN_PRESENT=yes

UNRESOLVED="$(count_unresolved)"
DENIED_COUNT="$(count_denied_dirs)"
CODEOWNERS="$(file_present .github/CODEOWNERS)"
WORKFLOW="$(file_present .github/workflows/main.yml)"
BAZEL_BUILD_JOB="$(workflow_has_job bazel-build)"
BAZEL_TEST_JOB="$(workflow_has_job bazel-test)"
THIRD_PARTY_DOC="$(file_present third_party/README.md)"
CONTRACTS_DOC="$(file_present contracts/README.md)"
MANIFEST_DOC="$(file_present monorepo_manifest.yaml)"
WORKSPACE_DOC="$(file_present Monorepo-Uphillsnowball.code-workspace)"
PYRIGHT_DOC="$(file_present pyrightconfig.json)"

CANONICAL_SCORE=0
[ "$MANIFEST_DOC" = yes ] && CANONICAL_SCORE=$((CANONICAL_SCORE+8))
if [ "$UNRESOLVED" -eq 0 ]; then
  CANONICAL_SCORE=$((CANONICAL_SCORE+12))
elif [ "$UNRESOLVED" -le 2 ]; then
  CANONICAL_SCORE=$((CANONICAL_SCORE+6))
fi

CLEAN_SCORE=0
if [ "$DENIED_COUNT" -eq 0 ]; then
  CLEAN_SCORE=20
elif [ "$DENIED_COUNT" -le 5 ]; then
  CLEAN_SCORE=10
fi

GOV_SCORE=0
[ "$CODEOWNERS" = yes ] && GOV_SCORE=$((GOV_SCORE+5))
[ "$WORKFLOW" = yes ] && GOV_SCORE=$((GOV_SCORE+3))
[ "$BAZEL_BUILD_JOB" = yes ] && GOV_SCORE=$((GOV_SCORE+3))
[ "$BAZEL_TEST_JOB" = yes ] && GOV_SCORE=$((GOV_SCORE+4))

CI_SCORE=0
[ "$BAZEL_BUILD_JOB" = yes ] && CI_SCORE=$((CI_SCORE+7))
[ "$BAZEL_TEST_JOB" = yes ] && CI_SCORE=$((CI_SCORE+8))

THIRD_SCORE=0
[ "$THIRD_PARTY_DOC" = yes ] && THIRD_SCORE=10

CONTRACT_SCORE=0
[ "$CONTRACTS_DOC" = yes ] && CONTRACT_SCORE=5
if [ "$(proto_count)" -gt 0 ]; then
  CONTRACT_SCORE=10
fi

TOOL_SCORE=0
[ "$WORKSPACE_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+2))
[ "$PYRIGHT_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+2))
[ "$MANIFEST_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+1))

MCP_SCORE=0
[ "$NODE_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$NPM_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$CHROME_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$CHROME_MCP_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$TOKEN_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))

TOTAL=$((CANONICAL_SCORE + CLEAN_SCORE + GOV_SCORE + CI_SCORE + THIRD_SCORE + CONTRACT_SCORE + TOOL_SCORE + MCP_SCORE))

cat > "${OUT}" <<REPORT
# Monorepo Weekly Scorecard

## Week of
\`${DATE_STR}\`

## Overall score
- Current week score: \`${TOTAL}/100\`
- Last week score: \`__/100\`
- Delta: \`+/-__\`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 | ${CANONICAL_SCORE} | ${CANONICAL_SCORE} | unresolved repos: ${UNRESOLVED} |
| Live tree cleanliness | 20 | ${CLEAN_SCORE} | ${CLEAN_SCORE} | denied-zone residue count: ${DENIED_COUNT} |
| GitHub governance | 15 | ${GOV_SCORE} | ${GOV_SCORE} | CODEOWNERS=${CODEOWNERS}, workflow=${WORKFLOW} |
| Bazel / CI reliability | 15 | ${CI_SCORE} | ${CI_SCORE} | bazel-build=${BAZEL_BUILD_JOB}, bazel-test=${BAZEL_TEST_JOB} |
| third_party discipline | 10 | ${THIRD_SCORE} | ${THIRD_SCORE} | third_party/README.md=${THIRD_PARTY_DOC} |
| Shared contracts | 10 | ${CONTRACT_SCORE} | ${CONTRACT_SCORE} | contracts doc=${CONTRACTS_DOC}, proto files=$(proto_count) |
| Workspace / tooling stability | 5 | ${TOOL_SCORE} | ${TOOL_SCORE} | workspace=${WORKSPACE_DOC}, pyright=${PYRIGHT_DOC} |
| MCP stack stability | 5 | ${MCP_SCORE} | ${MCP_SCORE} | chrome_mcp=${CHROME_MCP_PRESENT}, token=${TOKEN_PRESENT} |

---

## Examples to audit this week
- Example canonical repo: apps/aiyou_stack/aiyou-fastapi-services
- Example unresolved repo count: ${UNRESOLVED}
- Example denied-zone residue count: ${DENIED_COUNT}
- Example green bazel-build: ${BAZEL_BUILD_JOB}
- Example green bazel-test: ${BAZEL_TEST_JOB}
- Example MCP fixed: chrome-devtools resolvable=${CHROME_MCP_PRESENT}
- Example MCP still timing out: firebase-mcp-server / mcp-toolbox-for-databases / sequential-thinking remain manual-validation items

---

## Quick evidence snapshot

- monorepo_manifest.yaml: ${MANIFEST_DOC}
- .github/CODEOWNERS: ${CODEOWNERS}
- .github/workflows/main.yml: ${WORKFLOW}
- Monorepo-Uphillsnowball.code-workspace: ${WORKSPACE_DOC}
- pyrightconfig.json: ${PYRIGHT_DOC}
- third_party/README.md: ${THIRD_PARTY_DOC}
- contracts/README.md: ${CONTRACTS_DOC}
- Python files under apps: $(python_count apps)
- Python files under libs: $(python_count libs)
- BUILD.bazel files: $(build_count)
- Proto files: $(proto_count)

---

## Executive summary
This scorecard was generated from current repo state rather than hand-written estimates.
The largest remaining blocker is unresolved canonicalization if unresolved repos remain, plus denied-zone residue if backup or legacy trees are still present.
GitHub governance is only partially measurable locally; web UI confirmation is still required for branch protection and required checks.
Next, resolve unresolved repos, remove denied-zone residue from live trees, and verify protected-main enforcement for bazel-build and bazel-test.
REPORT

echo "Wrote ${OUT}"
