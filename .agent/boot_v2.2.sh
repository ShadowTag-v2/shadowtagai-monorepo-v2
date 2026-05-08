#!/bin/bash
# ==============================================================================
# SINGULARITY CORE v2.2 BOOTSTRAP — THE COMPLETE ENGINE
# ==============================================================================
# NOTE: This is a legacy bootstrap script. The canonical boot path is now
# managed by the AGENTS.md operator invariants and the MCP Fleet Vanguard.
# Retained for reference only. Do NOT execute directly.

echo " Booting Antigravity Singularity Engine v2.2..."

# 1. Temporal-Reversal Git State-Machine
echo "[i] Initializing Temporal-Reversal Git State-Machine..."
mkdir -p .git/hooks
cat << 'EOF' > .git/hooks/post-commit
git tag -f latest-stable
EOF
chmod +x .git/hooks/post-commit
git config core.untrackedCache true

# 2. Environment Mappings
export CLAUDE_HOME="$(pwd)/.agent/home_claude"
export CLAUDE_OUTPUTS="$(pwd)/.agent/user_data/outputs"
export SKILLS_DIR="$(pwd)/.agent/skills"
mkdir -p $CLAUDE_HOME $CLAUDE_OUTPUTS $SKILLS_DIR ./data ./output ./tmp

echo "=============================================================================="
echo "  SYSTEM ONLINE: Antigravity IDE v2.2 is fully operational."
echo "=============================================================================="
