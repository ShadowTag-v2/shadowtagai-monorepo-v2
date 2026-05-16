#!/usr/bin/env bash
set -euo pipefail

echo "🌱 Seeding full pnkln monorepo..."

mkdir -p apps/counselconduit labs/uphillsnowball docs/judge6-reports scripts prompts .antigravity/rules core

# Core canonical files (all previous raw blocks)
# Ensure file exists before copying over itself or creating it if missing
if [ ! -f .antigravity/rules/cor-antigravity.mdc ]; then
  touch .antigravity/rules/cor-antigravity.mdc
fi
cp -f .antigravity/rules/cor-antigravity.mdc .antigravity/rules/cor-antigravity.mdc

cat > monorepo_manifest.yaml << 'EOF'
workspace: pnkln
product: apps/counselconduit
lab: labs/uphillsnowball
mcp-truth: antigravity-mcp-config.json
judge6-gate: active
EOF

echo "Monorepo seeded with Judge-6, Cor.Rules, cinematic loop, and all skills."
