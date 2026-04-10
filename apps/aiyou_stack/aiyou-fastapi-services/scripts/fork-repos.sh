#!/bin/bash
# fork-repos.sh - Fork MCP/AI repos to your namespace for analysis
# Usage:
#   ./fork-repos.sh quick     # just MCP TS SDK
#   ./fork-repos.sh core      # MCP SDK + servers + Anthropic quickstarts (RECOMMENDED)
#   ./fork-repos.sh full      # all listed repos
#   ./fork-repos.sh dry-run   # show what would happen (uses core set)

set -euo pipefail

# CONFIGURATION
GH_USER="${GH_USER:-$(gh api user -q .login 2>/dev/null || echo 'your-username')}"
ORG_TARGET="${ORG_TARGET:-$GH_USER}"  # set to org name if org perms confirmed

# MASTER LIST (superset)
REPOS=(
  "anthropics/anthropic-quickstarts"
  "modelcontextprotocol/servers"
  "modelcontextprotocol/typescript-sdk"
  "anthropics/courses"
  "deepseek-ai/DeepSeek-V3"
  "QwenLM/Qwen2.5-Coder"
  "meta-llama/llama-models"
)

# PROFILES
PROFILE="${1:-core}"
DRY_RUN=0

if [[ "$PROFILE" == "dry-run" ]]; then
  DRY_RUN=1
  PROFILE="core"
fi

case "$PROFILE" in
  quick)
    ACTIVE_REPOS=("modelcontextprotocol/typescript-sdk")
    ;;
  core)
    ACTIVE_REPOS=(
      "modelcontextprotocol/typescript-sdk"
      "modelcontextprotocol/servers"
      "anthropics/anthropic-quickstarts"
    )
    ;;
  full)
    ACTIVE_REPOS=("${REPOS[@]}")
    ;;
  *)
    echo "Usage: $0 [quick|core|full|dry-run]"
    exit 1
    ;;
esac

# GitHub CLI required
if ! command -v gh &> /dev/null; then
  echo "ERROR: GitHub CLI not installed. Install: brew install gh"
  exit 1
fi

# Auth check
if ! gh auth status &> /dev/null; then
  echo "ERROR: Not authenticated. Run: gh auth login"
  exit 1
fi

# Rate limit backoff
SLEEP_TIME=1
backoff_sleep() {
  sleep $SLEEP_TIME
  SLEEP_TIME=$((SLEEP_TIME * 2))
  if [[ $SLEEP_TIME -gt 32 ]]; then
    SLEEP_TIME=32
  fi
}

reset_backoff() {
  SLEEP_TIME=1
}

# Fork function
fork_repo() {
  local src_repo=$1
  local repo_name
  repo_name=$(basename "$src_repo")

  echo "→ Handling $src_repo (as $repo_name)..."

  # Check if fork exists under personal or org
  if gh repo view "$GH_USER/$repo_name" &> /dev/null; then
    echo "  ✓ Already present under $GH_USER/$repo_name"
    reset_backoff
    return 0
  fi
  if [[ "$ORG_TARGET" != "$GH_USER" ]] && gh repo view "$ORG_TARGET/$repo_name" &> /dev/null; then
    echo "  ✓ Already present under $ORG_TARGET/$repo_name"
    reset_backoff
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "  [dry-run] Would fork $src_repo -> $ORG_TARGET (clone=false)"
    return 0
  fi

  echo "  → Forking to $ORG_TARGET..."
  if [[ "$ORG_TARGET" == "$GH_USER" ]]; then
    gh repo fork "$src_repo" --clone=false
  else
    gh repo fork "$src_repo" --org="$ORG_TARGET" --clone=false
  fi

  echo "  ✓ Fork requested for $src_repo"
  backoff_sleep
}

echo "=== FORKING (${PROFILE}) TO ORG_TARGET=$ORG_TARGET (GH_USER=$GH_USER) ==="
if [[ $DRY_RUN -eq 1 ]]; then
  echo "Mode: DRY RUN — no forks will actually be created."
fi

for repo in "${ACTIVE_REPOS[@]}"; do
  fork_repo "$repo"
done

echo ""
echo "=== SUMMARY ==="
for repo in "${ACTIVE_REPOS[@]}"; do
  repo_name=$(basename "$repo")
  echo "  https://github.com/$ORG_TARGET/$repo_name"
done

echo ""
echo "=== NEXT ACTIONS ==="
echo "1. Clone TS SDK:"
echo "   gh repo clone $ORG_TARGET/typescript-sdk modelcontext-ts"
echo ""
echo "2. Clone servers (if in profile):"
echo "   gh repo clone $ORG_TARGET/servers mcp-servers"
echo ""
echo "3. Add upstreams:"
echo "   cd modelcontext-ts"
echo "   git remote add upstream https://github.com/modelcontextprotocol/typescript-sdk.git"
echo "   cd ../mcp-servers"
echo "   git remote add upstream https://github.com/modelcontextprotocol/servers.git"
echo ""
echo "4. Sync later with:"
echo "   git fetch upstream && git merge upstream/main"
echo ""
echo "5. Run discovery:"
echo "   python scripts/github_discovery_agent.py --root modelcontext-ts --output mcp-discovery.json"
echo ""
echo "6. Create PNKLN mapping thread:"
echo "   python scripts/atomic_thread_manager.py create --tier PRO --type PROMPT --mission 'Map MCP SDK to PNKLN namespaces'"
