#!/usr/bin/env bash
# Hardened Antigravity Integration Script
# Persists the "ant" gated logic, compliance hooks, and monorepo sync against Claude overwrites.

set -euo pipefail

MONOREPO_ROOT="${MONOREPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

echo "=== 1. Extracting Ant-Gated Logic ==="
rg -B 5 -A 10 "process\.env\.USER_TYPE === 'ant'" "$MONOREPO_ROOT/scratch/claude_code_src/src" > "$MONOREPO_ROOT/scratch/ant_gated_logic.txt" || true

echo "=== 2. Applying Dual-License Copyright Headers (Python & TSX) ==="
python3 "$MONOREPO_ROOT/scripts/add_copyright.py"

echo "=== 3. Executing Omni-Autolint Daemon ==="
# Fix pyproject.toml before ruff if necessary
find "$MONOREPO_ROOT" -name "pyproject.toml" -exec sed -i '' 's/src-path/src/g' {} + 2>/dev/null || true
python3 "$MONOREPO_ROOT/scripts/gca_autolint_daemon.py" --yes

echo "=== 4. Running SkillOps Audit ==="
bash "$MONOREPO_ROOT/scripts/skills-audit.sh"

echo "=== 5. Running Compliance Copy Scan ==="
bash "$MONOREPO_ROOT/scripts/compliance_copy_scan_weekly.sh"

echo "=== 6. Validating Core Architecture (pytest) ==="
/opt/homebrew/bin/python3.14 -m pytest "$MONOREPO_ROOT/apps/counselconduit/tests/test_dispatch_Cor_Claude_Code_6_integration.py"

echo "=== 7. Securing GitOps Push ==="
python3 "$MONOREPO_ROOT/scripts/auth_github_app.py" --push

echo "Hardening Sequence Complete."
