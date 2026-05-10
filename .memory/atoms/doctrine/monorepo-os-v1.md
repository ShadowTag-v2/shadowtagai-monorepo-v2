---
id: "doctrine-monorepo-os-v1"
created: "2026-04-27T17:52:00Z"
updated: "2026-04-27T17:52:00Z"
category: doctrine
tags: [monorepo-os, core-doctrine, files-are-truth]
references:
  - file:///MONOREPO_OS.md
  - file:///index_policy.yaml
  - file:///upload_policy.yaml
status: active
---

# Monorepo OS — Files Are Truth

## Core Law

No agent action touches source truth until it has passed through graph truth,
build truth, safety truth, execution truth, and evidence truth.

## Subsystem Axioms

1. **Files are truth; SQLite is cache.** Knowledge atoms live as Markdown with
   YAML frontmatter. SQLite databases are rebuildable indexes.
2. **Track truth files. Ignore caches.** Git tracks atoms, events, contracts.
   Git ignores SQLite, logs, generated indexes.
3. **Record every mutation.** `events.ndjson` and `issues.jsonl` are append-only
   authoritative logs.
4. **Rebuild indexes.** Any cache can be deleted and rebuilt from truth files.
5. **Indexes are routed, not monolithic.** No single index answers all questions.
   Each index owns a specific class of queries.

## Architecture Layers

| Layer | Subsystem | Truth File |
|-------|-----------|------------|
| Source | Git | tracked files |
| Artifact | GCS | `artifacts/manifest.yaml` |
| Build | Bazel | `BUILD.bazel` + BEP |
| Safety | ToolGateway | `tool_contracts/` |
| Evidence | Flight Recorder | `.agent/evidence/` |
| Push | GitHub App | `scripts/push-with-app-gates.sh` |
| Memory | Knowledge Atoms | `.memory/atoms/` |
| Task | Beads | `.beads/issues.jsonl` |
