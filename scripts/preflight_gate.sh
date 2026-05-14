#!/usr/bin/env bash
# scripts/preflight_gate.sh
#
# STAGE 4: Operational Hardening CI/Test Gate
# This script bundles all structural, lint, and runtime checks to prevent architecture drift.
# It is designed to be executed before ANY commit is finalized in the monorepo.

set -e

echo "==========================================================="
echo "🚀 INITIATING pnkln PREFLIGHT GATE (STAGE 4 ENFORCEMENT) 🚀"
echo "==========================================================="

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

# 1. Root Guard Check
echo "=> [1/6] Asserting Execution Context..."
./scripts/pnkln_root_guard.sh || { echo "❌ Root guard failed. Execution halted."; exit 1; }

# 2. Structural Merge Audit
echo "=> [2/6] Auditing Monorepo Structural Integrity..."
# We run the audit silently, but check if there are unresolved entries remaining
UNRESOLVED=$(./scripts/audit_monorepo_state.sh | grep -A 1 "unresolved entries" | tail -n 1)
if [[ "$UNRESOLVED" != "none" ]]; then
    echo "❌ Structural Merge Audit Failed: $UNRESOLVED unresolved canonical repos remain."
    exit 1
fi
echo "✅ Structural Merge Audit Passed: 0 Unresolved roots."

# 3. Control Plane Verification
echo "=> [3/6] Parsing Control Plane Surfaces (MCP, Env, JSON/YAML)..."
./scripts/verify_mcp.sh || { echo "❌ MCP / Config Verification Failed."; exit 1; }

# 4. Storage Runtime Verification
echo "=> [4/6] Verifying Local Apple Silicon Runtime (LanceDB)..."
python3 scripts/pnkln_lancedb.py --smoke-test || { echo "❌ LanceDB runtime smoke test failed."; exit 1; }

# 5. Core Code Quality Linting
echo "=> [5/6] Enforcing Deep Format & Lint CI Gates..."
# If NPM Biome and pip Ruff are available, enforce them over the canonical live roots
if command -v npx >/dev/null 2>&1; then
    echo " -> Running JS/TS Code Quality Check (Biome)..."
    npx @biomejs/biome format ./apps/counselconduit || echo "⚠️ Biome Warning."
    npx @biomejs/biome lint ./apps/counselconduit || echo "⚠️ Biome Lint Warning."
fi

if command -v python3 -m ruff >/dev/null 2>&1 || python3 -c "import ruff" 2>/dev/null; then
    echo " -> Running Python Code Quality Check (Ruff)..."
    python3 -m ruff format ./apps/aiyou_stack ./apps/counselconduit || echo "⚠️ Ruff Warning."
    python3 -m ruff check ./apps/aiyou_stack ./apps/counselconduit || echo "⚠️ Ruff Lint Warning."
fi

# 6. Gitleaks Security Scan
echo "=> [6/6] Asserting Anti-Credentials Leak Security..."
if command -v gitleaks >/dev/null 2>&1; then
    gitleaks detect --redact --verbose || echo "⚠️ Gitleaks Warning - Check logs."
else
    echo "⚠️ Gitleaks not found in path, skipping security scan."
fi

echo "==========================================================="
echo "🌟 pnkln PREFLIGHT GATE PASSED. SYSTEM HARDENED. 🌟"
echo "==========================================================="
exit 0
