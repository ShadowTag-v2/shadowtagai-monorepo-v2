#!/bin/bash
# PNKLN Task Runner
# Executes doctrine validation and financial projections

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "PNKLN // TASK RUNNER"
echo "========================================"

# Run Monte Carlo projection
echo ""
echo "📊 Running Portfolio Monte Carlo..."
python3 "$SCRIPT_DIR/Notebooks/pnkln_PortfolioMonteCarlo.py"

# Run CodePMCS if available
echo ""
echo "🔧 Running CodePMCS inspection..."
python3 "$SCRIPT_DIR/codepmcs.py" "$SCRIPT_DIR/.." 2>/dev/null || echo "   (CodePMCS deps not installed)"

# Launch mission
echo ""
echo "🚀 Launching Squadron..."
python3 "$SCRIPT_DIR/pnkln_mission_start.py"

echo ""
echo "========================================"
echo "✅ PNKLN TASKS COMPLETE"
echo "========================================"
