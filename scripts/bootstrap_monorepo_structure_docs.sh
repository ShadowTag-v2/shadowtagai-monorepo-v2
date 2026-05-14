#!/usr/bin/env bash
# Bootstrap Monorepo Structure Docs
set -euo pipefail
MONOREPO=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

mkdir -p "$MONOREPO/docs"

cat > "$MONOREPO/docs/STRUCTURE.md" << 'EOF'
# Monorepo Structure

## Root: Monorepo-Uphillsnowball

```
Monorepo-Uphillsnowball/
├── apps/
│   └── aiyou_stack/          # Primary app namespace
│       ├── cosmic-crab-payload/  # Folded in from playground/cosmic-crab
│       └── ...               # Other AiYou stack apps
├── memory/
│   ├── antigravity-knowledge/  # Folded in from ~/antigravity-knowledge
│   └── ...                   # Other memory/knowledge files
├── docs/
│   ├── bundles/              # Unzipped artifact bundles
│   ├── governance/           # GUARDRAILS.md and policy docs
│   ├── 10x/                  # Velocity principles and agent routing
│   └── STRUCTURE.md          # This file
├── scripts/
│   ├── bootstrap_*.sh        # Idempotent bootstrap scripts
│   ├── audit_repos.sh        # Repo size audit
│   └── generate_report.sh    # Markdown report generator
├── libs/                     # Shared libraries
├── third_party/              # Vendored/cloned external repos
├── infra/                    # Infrastructure configs
├── packages/                 # Shared packages
├── src/                      # Source code
└── tests/                    # Test suites
```

## Naming Conventions
- app namespaces: lowercase_snake_case
- scripts: verb_noun.sh pattern
- docs: UPPER_SNAKE_CASE.md for governance, Title_Case.md for guides

## Fold-in Policy
All external repos must be folded into apps/aiyou_stack/ or third_party/
with --exclude='.git' to strip history, then committed atomically.
EOF

echo "Structure docs written to docs/STRUCTURE.md"
