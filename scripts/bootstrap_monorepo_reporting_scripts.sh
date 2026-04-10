#!/usr/bin/env bash
# Bootstrap reporting scripts — ensures generate_report.sh is present and executable
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

chmod +x "$MONOREPO/scripts/generate_report.sh"
echo "generate_report.sh is ready."
bash "$MONOREPO/scripts/generate_report.sh"
