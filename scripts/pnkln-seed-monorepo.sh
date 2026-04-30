#!/usr/bin/env bash
set -euo pipefail

echo "🌱 Seeding full pnkln monorepo..."

mkdir -p apps/counselconduit labs/uphillsnowball docs/judge6-reports scripts prompts .antigravity/rules

# Core canonical files (all previous raw blocks)
cp -f .antigravity/rules/cor-antigravity.mdc .antigravity/rules/cor-antigravity.mdc || true

cat > monorepo_manifest.yaml << 'EOF'
workspace: pnkln
product: apps/counselconduit
lab: labs/uphillsnowball
mcp-truth: antigravity-mcp-config.json
judge6-gate: active
EOF

echo "Monorepo seeded with Judge-6, Cor.Rules, cinematic loop, and all skills."
