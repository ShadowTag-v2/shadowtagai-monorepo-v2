#!/bin/bash
# setup_n-autoresearch/Kosmos/BioAgents.sh
# ----------------------------------------------------
# PURPOSE: Unifies Quibbler across CLI and IDE layers
# AUTHOR: n-autoresearch/Kosmos/BioAgents Arch Team
# ----------------------------------------------------

echo "🐒 Initializing n-autoresearch/Kosmos/BioAgents Protocol..."

# 1. Install Quibbler (The Brain)
pip install -U quibbler

# 2. Configure Quibbler Core (The Constitution)
# We use Haiku 4.5 for speed (p99 < 90ms)
mkdir -p ~/.quibbler
cat > ~/.quibbler/config.json << EOF
{
  "model": "claude-haiku-4-5-20251001",
  "storage_path": ".quibbler/rules.md",
  "learning_mode": "active"
}
EOF

# 3. Inject CLI Hooks (The Bouncer)
# Forces Claude Code to listen to Quibbler
quibbler add

# 4. Configure MCP for IDEs (The Consultant)
# This allows Antigravity & VS Code to "see" the rules
mkdir -p .vscode
cat > .vscode/mcp.json << EOF
{
  "mcpServers": {
    "quibbler": {
      "command": "quibbler",
      "args": ["mcp"],
      "env": {
        "QUIBBLER_MODEL": "claude-haiku-4-5-20251001"
      }
    }
  }
}
EOF

# 5. Seed the Doctrine (The Law)
# Don't start empty. Give Judge#6 a baseline.
mkdir -p .quibbler
if [ ! -f .quibbler/rules.md ]; then
    echo "# n-autoresearch/Kosmos/BioAgents Doctrine" > .quibbler/rules.md
    echo "- RULE: All async functions must have try/catch blocks." >> .quibbler/rules.md
    echo "- RULE: No hardcoded secrets; use env vars." >> .quibbler/rules.md
    echo "- RULE: Comments must explain 'WHY', not 'WHAT'." >> .quibbler/rules.md
fi

echo "✅ n-autoresearch/Kosmos/BioAgents Protocol Active."
echo "   - CLI: Hooks Enforced"
echo "   - IDE: MCP Server Ready"
echo "   - BRAIN: Haiku 4.5 Configured"
