# Monorepo Guardrails

## Operator Invariants
1. Never push secrets (API keys, tokens) to git
2. All bootstrap scripts must be idempotent
3. Memory/context must be hydrated before reasoning
4. No local CPU for ML/tensor compute — use ANE or remote
5. GitHub App token only (no PAT, no SSH deploy keys)
6. filter-repo over BFG for history rewriting
7. Commit every fold-in with atomic message

## Folder Conventions
- apps/pnkln-stack_stack/  → primary app namespace
- memory/            → knowledge and memory files
- docs/              → governance, reports, bundles
- scripts/           → bootstrap and utility scripts
- third_party/       → vendored/cloned external repos
- libs/              → shared libraries

## Security
- .env and secrets excluded via .gitignore
- Rotate keys every 90 days
- Structured logging only, no PII
