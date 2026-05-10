#!/usr/bin/env bash
# Bootstrap 10x Docs
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

mkdir -p "$MONOREPO/docs/10x"

cat > "$MONOREPO/docs/10x/VELOCITY_PRINCIPLES.md" << 'EOF'
# 10x Velocity Principles
1. Plan before code — always enter planning mode for non-trivial changes
2. Atomic commits — one logical change per commit
3. Idempotent scripts — all bootstrap scripts safe to re-run
4. Parallel agents — maximize parallel tool calls
5. Memory first — hydrate CLAUDE.md context before any session
6. Zero regressions — never skip tests or linting
7. Ship fast, ship secure — never compromise security for speed
EOF

cat > "$MONOREPO/docs/10x/AGENT_ROUTING.md" << 'EOF'
# Agent Routing Table

| Agent | Purpose | Trigger |
|-------|---------|---------|
| Cor (Claude) | Principal coding architect | Default |
| Gemini Flash | Fast extraction/analysis | drive_ingest_daemon |
| text-embedding-004 | Semantic embeddings | RAG pipeline |
EOF

echo "10x docs written to docs/10x/"
