---
id: atom-fact-miras-four-design-choices
type: fact
created: 2026-04-27T22:36:00Z
source: docs/research/miras-titans-notes.md
tags: [architecture, memory, miras, titans]
---

# MIRAS Four Design Choices

The MIRAS (Multi-scale Information Retention and Adaptive Selection) framework
defines four design choices that govern our `.memory/` system:

1. **Surprise-Based Memory Triage** — Prioritize high-surprise inputs (decisions,
   issues) over routine data (events, facts). Maps to `beads-capture.sh` type
   system.

2. **Multi-Scale Retention** — Three parallel stores: working (session handoff),
   episodic (beads journal + events), semantic (atoms + KIs). Different retention
   policies per tier.

3. **Adaptive Context Selection** — `repo-oracle` dynamically selects which stored
   memories to inject into active context based on task relevance. Budget enforced
   by `context-budget-discipline` skill.

4. **Hierarchical Compression** — `dream_consolidation.py` nightly merges daily
   logs into KIs. `ag-context-compactor` manages the 4-layer pipeline: raw events
   → session summaries → KIs → doctrinal truths.

## Cross-References

- Full research notes: `docs/research/miras-titans-notes.md`
- Memory config: `.memory/config.yaml`
- Dream daemon: `scripts/dream_consolidation.py`
- Context compactor: `skills/ag-context-compactor/SKILL.md`
