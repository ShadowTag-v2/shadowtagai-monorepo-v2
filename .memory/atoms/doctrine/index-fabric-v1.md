---
id: "doctrine-index-fabric-v1"
created: "2026-04-27T17:52:00Z"
updated: "2026-04-27T17:52:00Z"
category: doctrine
tags: [indexing, gitnexus, scip, bazel, zoekt, rag, routing]
references:
  - file:///index_policy.yaml
  - file:///tool_contracts/index.query.yaml
  - file:///scripts/index-status.sh
status: active
---

# Multi-Index Routing Fabric

## Principle

No single index is total truth. Each index owns a specific class of questions.

## Index Registry

| Index | Role | Authority |
|-------|------|-----------|
| GitNexus | Agent impact graph | Impact and process truth |
| SCIP | Precise symbol navigation | Definition/reference truth |
| Bazel | Build dependency graph | Build/test truth |
| Zoekt | Fast code search | Text search truth |
| RAG | Semantic docs/memory | Recall only, not source truth |

## Routing Rules

- **Symbol definition** → SCIP → GitNexus → ripgrep
- **Impact analysis** → GitNexus → Bazel rdeps → SCIP refs
- **Build deps** → Bazel query → GitNexus import graph
- **Text search** → Zoekt → ripgrep
- **Architecture docs** → RAG → docs search

## Forbidden Patterns

- Using RAG as source truth for code mutation
- Using text search as only proof for refactor
- Skipping GitNexus impact for nontrivial refactor
- Skipping Bazel query for build metadata change
