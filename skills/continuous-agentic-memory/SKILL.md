---
name: Continuous Agentic Memory
description: Greg Isenberg Compounding Context loop — self-updating persistent memory with preference extraction, knowledge graph, and LanceDB vector search.
---

# Continuous Agentic Memory

> Protocol: Execution → Reflection → Storage → Injection  
> Source: Greg Isenberg "Compounding Context" pattern

## Architecture

```
Session Start ──▶ Read .ai-memory.md ──▶ Inject into system prompt
     │
     ▼
Execute Tasks ──▶ Log to .beads/issues.jsonl
     │
     ▼
Reflection Daemon ──▶ Extract preferences via regex
     │
     ▼
Storage ──▶ data/memory/knowledge_graph.json
         ──▶ data/memory/reflections.jsonl
         ──▶ data/lance_corpus/ (vector search)
     │
     ▼
Session End ──▶ Update .ai-memory.md
```

## Files

| File | Purpose |
|------|---------|
| `.ai-memory.md` | Persistent fact store (human + machine readable) |
| `scripts/memory_reflection_daemon.py` | 4-stage reflection engine |
| `scripts/corpus_lancedb_embed.py` | LanceDB vector table builder |
| `scripts/corpus_bq_loader.py` | BigQuery GQL graph loader |
| `data/memory/knowledge_graph.json` | Preference graph (nodes/edges) |
| `data/memory/reflections.jsonl` | Timestamped reflection log |
| `data/drive_ingest/extractions.jsonl` | 1,094-doc corpus (25.1 MB) |

## Usage

```bash
# Session start — inject memory into prompt
python3 scripts/memory_reflection_daemon.py --inject

# Background daemon (5-min poll)
python3 scripts/memory_reflection_daemon.py --watch --interval 300

# One-shot reflection
python3 scripts/memory_reflection_daemon.py --reflect

# Build/rebuild knowledge graph
python3 scripts/memory_reflection_daemon.py --graph

# Stats
python3 scripts/memory_reflection_daemon.py --stats

# Semantic search over corpus
python3 scripts/corpus_lancedb_embed.py --query "search term" --top 5
python3 scripts/corpus_lancedb_embed.py --stats
```

## Rules

1. **Never delete `.ai-memory.md`** — it compounds over time
2. **Corrections go in the Correction Log** section with date prefix
3. **Preferences auto-extracted** from beads via regex (prefers X over Y, never use X)
4. **Knowledge graph is append-only** — nodes are never removed
5. **LanceDB table is rebuilt** when corpus changes; queries are instant
6. **Injection happens at session start** — daemon `--inject` generates `<persistent_memory>` block
