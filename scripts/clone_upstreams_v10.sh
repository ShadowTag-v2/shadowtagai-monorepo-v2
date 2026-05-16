#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-external_repos}"

mkdir -p "$ROOT/runtime" "$ROOT/authority" "$ROOT/references"

clone_or_skip() {
  local url="$1"
  local dest="$2"
  if [ -d "$dest/.git" ] || [ -d "$dest" ]; then
    echo "[skip] $dest already exists"
  else
    echo "[clone] $url -> $dest"
    git clone "$url" "$dest"
  fi
}

echo "[info] Cloning runtime repos"
clone_or_skip https://github.com/maderix/ANE.git "$ROOT/runtime/ANE"
clone_or_skip https://github.com/patmakesapps/CortexLTM.git "$ROOT/runtime/CortexLTM"
clone_or_skip https://github.com/patmakesapps/CortexUI.git "$ROOT/runtime/CortexUI"
clone_or_skip https://github.com/steveyegge/beads.git "$ROOT/runtime/beads"
clone_or_skip https://github.com/pgvector/pgvector.git "$ROOT/runtime/pgvector"
clone_or_skip https://github.com/postgres/postgres.git "$ROOT/runtime/postgres"
clone_or_skip https://github.com/docker-library/postgres.git "$ROOT/runtime/docker-postgres"
clone_or_skip https://github.com/grafana/grafana.git "$ROOT/runtime/grafana"
clone_or_skip https://github.com/payloadcms/payload.git "$ROOT/runtime/payload"
clone_or_skip https://github.com/prettier/prettier-vscode.git "$ROOT/runtime/prettier-vscode"

echo "[info] Cloning authority repos"
clone_or_skip git@github.com:ehanc69/erik-hancock-llm-memory.git "$ROOT/authority/erik-hancock-llm-memory"
clone_or_skip git@github.com:ehanc69/pnkln.git "$ROOT/authority/pnkln"
clone_or_skip git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git "$ROOT/authority/Monorepo-Uphillsnowball"
clone_or_skip git@github.com:ehanc69/aiyou-fastapi-services.git "$ROOT/authority/aiyou-fastapi-services"
clone_or_skip git@github.com:ehanc69/cosmic-crab-payload.git "$ROOT/authority/cosmic-crab-payload"
clone_or_skip git@github.com:ehanc69/Pipeline.git "$ROOT/authority/Pipeline"
clone_or_skip git@github.com:ehanc69/nascent-apollo.git "$ROOT/authority/nascent-apollo"

echo "[info] Cloning reference repos"
clone_or_skip https://github.com/GantisStorm/essentials-claude-code.git "$ROOT/references/essentials-claude-code"
clone_or_skip https://github.com/miqcie/grepai-beads-helpers.git "$ROOT/references/grepai-beads-helpers"
clone_or_skip https://github.com/JPM1118/Threadwork.git "$ROOT/references/Threadwork"
clone_or_skip https://github.com/akng8/beads-templates.git "$ROOT/references/beads-templates"
clone_or_skip https://github.com/CortexReach/memory-lancedb-pro.git "$ROOT/references/memory-lancedb-pro"
clone_or_skip https://github.com/Toowiredd/claude-skills-automation.git "$ROOT/references/claude-skills-automation"

cat <<EOF

[done] Clone layout created under: $ROOT

Runtime repos:
  - ANE
  - CortexLTM
  - CortexUI
  - beads
  - pgvector
  - postgres
  - docker-postgres
  - grafana
  - payload
  - prettier-vscode

Authority repos:
  - erik-hancock-llm-memory
  - pnkln
  - Monorepo-Uphillsnowball
  - aiyou-fastapi-services
  - cosmic-crab-payload
  - Pipeline
  - nascent-apollo

Reference repos:
  - essentials-claude-code
  - grepai-beads-helpers
  - Threadwork
  - beads-templates
  - memory-lancedb-pro
  - claude-skills-automation

Rule:
  authority-current.json + authority atoms stay canonical.
  authority/ repos inform canonical memory.
  runtime/ repos power the stack.
  references/ repos are patterns only.
EOF
