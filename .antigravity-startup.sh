#!/bin/bash
TARGET="/Users/pikeymickey/shadowtag-omega-v4-stack/shadowtag-omega-v4"
export PIP_USER=false
export PYTHONNOUSERSITE=1

# Nuke hallucinations (nested git/agent folders only — not the root)
find "$TARGET" -mindepth 2 -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true
find "$TARGET" -mindepth 2 -type d -name ".agent" -exec rm -rf {} + 2>/dev/null || true

# Re-assert rules
mkdir -p "$TARGET/.agent"
cat > "$TARGET/.agent/rules.md" <<RULES
- ROOT: $TARGET
- MODE: ANTIGRAVITY_FORCE
- NO_NESTED_GIT
RULES

echo "Antigravity startup complete. Rules:"
cat "$TARGET/.agent/rules.md"
