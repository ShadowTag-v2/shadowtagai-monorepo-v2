#!/usr/bin/env bash
ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
mkdir -p "$ROOT/.agents/skills/epistemic-memory-kernel"

cat > "$ROOT/monorepo_manifest.yaml" <<'EOF'
version: 11.0 # Antigravity Handoff
active_silos:
  - id: shadowtag_core
    path: packages/core
    status: locked
    owner: pnkln-backend
  - id: ag_ui_components
    path: packages/ag-ui
    status: active_development
    owner: pnkln-frontend
EOF

cat > "$ROOT/MERGE_STATUS.md" <<'EOF'
# Handoff Merge Tracker
| Stage | Owner | Status |
|---|---|---|
| Monorepo Core Manifest | Antigravity | DONE |
| KovelAI Integration | Antigravity | PENDING |
| UI Component Rollout | Claude | PENDING |
EOF

cat > "$ROOT/antigravity-mcp-config.json" <<'EOF'
{
  "version": "1.0",
  "mcpServers": {
    "shadowtag-core": {
      "path": "apps/counselconduit",
      "tools": ["StitchMCP", "chrome-devtools-mcp"]
    }
  }
}
EOF

cat > "$ROOT/operator_invariants.json" <<'EOF'
{
  "platform": "macOS",
  "arch": "apple-silicon"
}
EOF

cat > "$ROOT/package.json" <<'EOF'
{
  "name": "uphillsnowball",
  "version": "11.0.0",
  "scripts": {
    "build": "echo 'Building Monorepo'",
    "deploy": "firebase deploy"
  }
}
EOF

echo "[OK] wrote updated pnkln pack to $ROOT"
