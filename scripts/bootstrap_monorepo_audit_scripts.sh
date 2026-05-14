#!/usr/bin/env bash
# Bootstrap audit scripts — ensures audit_repos.sh is present and executable
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

chmod +x "$MONOREPO/scripts/audit_repos.sh"
echo "audit_repos.sh is ready."
bash "$MONOREPO/scripts/audit_repos.sh"
